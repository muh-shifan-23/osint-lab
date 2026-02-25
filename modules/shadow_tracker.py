"""
ShadowTracker - Dark Web Intelligence Crawler
Monitors dark web forums, paste sites, and underground markets for threat intelligence
"""

import re
import requests
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import socks
import socket
from urllib.parse import urljoin, urlparse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ThreatIntelligence:
    """Data class for threat intelligence findings"""
    source: str
    content: str
    url: str
    timestamp: datetime
    threat_actor: Optional[str]
    iocs: Dict[str, List[str]]
    severity: int  # 1-10
    tags: List[str]
    raw_html: Optional[str] = None


class IOCExtractor:
    """Extract Indicators of Compromise from text"""
    
    # Regex patterns for various IOCs
    PATTERNS = {
        'ipv4': r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b',
        'domain': r'\b(?:[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}\b',
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'md5': r'\b[a-fA-F0-9]{32}\b',
        'sha1': r'\b[a-fA-F0-9]{40}\b',
        'sha256': r'\b[a-fA-F0-9]{64}\b',
        'url': r'https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&/=]*)',
        'btc_address': r'\b[13][a-km-zA-HJ-NP-Z1-9]{25,34}\b',
        'cve': r'CVE-\d{4}-\d{4,7}',
    }
    
    @classmethod
    def extract(cls, text: str) -> Dict[str, List[str]]:
        """Extract all IOCs from text"""
        iocs = {}
        
        for ioc_type, pattern in cls.PATTERNS.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                # Deduplicate and filter
                unique_matches = list(set(matches))
                # Filter out common false positives
                if ioc_type == 'domain':
                    unique_matches = cls._filter_domains(unique_matches)
                iocs[ioc_type] = unique_matches
        
        return iocs
    
    @staticmethod
    def _filter_domains(domains: List[str]) -> List[str]:
        """Filter out common false positive domains"""
        false_positives = {'example.com', 'test.com', 'localhost.com', 'domain.com'}
        return [d for d in domains if d.lower() not in false_positives]


class TorSession:
    """Manage Tor connections for dark web scraping"""
    
    def __init__(self, tor_proxy: str = "127.0.0.1", tor_port: int = 9050):
        self.tor_proxy = tor_proxy
        self.tor_port = tor_port
        self.session = None
        
    def create_session(self) -> requests.Session:
        """Create a requests session through Tor"""
        session = requests.Session()
        session.proxies = {
            'http': f'socks5h://{self.tor_proxy}:{self.tor_port}',
            'https': f'socks5h://{self.tor_proxy}:{self.tor_port}'
        }
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        return session
    
    def verify_tor_connection(self) -> bool:
        """Verify that Tor is working"""
        try:
            session = self.create_session()
            response = session.get('https://check.torproject.org', timeout=10)
            return 'Congratulations' in response.text
        except Exception as e:
            logger.error(f"Tor connection failed: {e}")
            return False


class PasteSiteScraper:
    """Scrape public paste sites for leaked data"""
    
    PASTE_SITES = [
        'https://pastebin.com/api_scraping.php',
        'https://ghostbin.com/recent',
        # Add more paste sites
    ]
    
    def __init__(self):
        self.session = requests.Session()
    
    async def scrape_pastebin(self, keywords: List[str]) -> List[ThreatIntelligence]:
        """
        Scrape Pastebin for specific keywords
        Note: Requires Pastebin API key for proper access
        """
        findings = []
        
        # Example implementation - adjust based on API availability
        url = "https://pastebin.com/api_scraping.php"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        for paste in data:
                            content = paste.get('scrape_raw_data', '')
                            
                            # Check if any keywords match
                            if any(kw.lower() in content.lower() for kw in keywords):
                                iocs = IOCExtractor.extract(content)
                                
                                intel = ThreatIntelligence(
                                    source='pastebin',
                                    content=content[:500],  # First 500 chars
                                    url=paste.get('scrape_url', ''),
                                    timestamp=datetime.now(),
                                    threat_actor=None,
                                    iocs=iocs,
                                    severity=self._calculate_severity(iocs),
                                    tags=keywords
                                )
                                findings.append(intel)
        
        except Exception as e:
            logger.error(f"Error scraping Pastebin: {e}")
        
        return findings
    
    def _calculate_severity(self, iocs: Dict[str, List[str]]) -> int:
        """Calculate threat severity based on IOC count and types"""
        severity = 0
        
        # Weight different IOC types
        weights = {
            'ipv4': 2,
            'domain': 2,
            'email': 1,
            'md5': 3,
            'sha256': 3,
            'url': 1,
            'btc_address': 4,
            'cve': 5
        }
        
        for ioc_type, matches in iocs.items():
            severity += len(matches) * weights.get(ioc_type, 1)
        
        # Normalize to 1-10 scale
        return min(10, max(1, severity // 5))


class DarkWebForumScraper:
    """Scrape dark web forums and marketplaces"""
    
    def __init__(self, use_tor: bool = True):
        self.use_tor = use_tor
        if use_tor:
            self.tor_session = TorSession()
            if not self.tor_session.verify_tor_connection():
                logger.warning("Tor not available, using regular connection")
                self.use_tor = False
    
    async def scrape_forum(self, 
                          forum_url: str, 
                          keywords: List[str],
                          max_pages: int = 5) -> List[ThreatIntelligence]:
        """
        Scrape a dark web forum for threat intelligence
        
        Args:
            forum_url: Base URL of the forum
            keywords: Keywords to search for
            max_pages: Maximum number of pages to scrape
        """
        findings = []
        
        session = self.tor_session.create_session() if self.use_tor else requests.Session()
        
        try:
            for page in range(1, max_pages + 1):
                url = f"{forum_url}?page={page}"
                
                response = session.get(url, timeout=30)
                if response.status_code != 200:
                    logger.warning(f"Failed to fetch {url}: {response.status_code}")
                    continue
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Example parsing - adjust based on forum structure
                posts = soup.find_all('div', class_='post')  # Adjust selector
                
                for post in posts:
                    content = post.get_text()
                    
                    # Check for keywords
                    if any(kw.lower() in content.lower() for kw in keywords):
                        # Extract metadata
                        author = post.find('span', class_='author')  # Adjust
                        author_name = author.text if author else "Unknown"
                        
                        iocs = IOCExtractor.extract(content)
                        
                        intel = ThreatIntelligence(
                            source=urlparse(forum_url).netloc,
                            content=content[:1000],
                            url=url,
                            timestamp=datetime.now(),
                            threat_actor=author_name,
                            iocs=iocs,
                            severity=self._assess_threat_level(content, iocs),
                            tags=keywords,
                            raw_html=str(post)
                        )
                        findings.append(intel)
                
                # Rate limiting
                await asyncio.sleep(2)
        
        except Exception as e:
            logger.error(f"Error scraping forum {forum_url}: {e}")
        
        return findings
    
    def _assess_threat_level(self, content: str, iocs: Dict) -> int:
        """Assess threat level based on content and IOCs"""
        severity = 5  # Base severity
        
        # Increase severity for specific keywords
        high_threat_keywords = [
            'ransomware', 'breach', 'dump', 'leaked', 'exploit',
            'zero-day', '0day', 'backdoor', 'malware', 'apt'
        ]
        
        content_lower = content.lower()
        for keyword in high_threat_keywords:
            if keyword in content_lower:
                severity += 1
        
        # Increase based on IOC richness
        if sum(len(v) for v in iocs.values()) > 10:
            severity += 2
        
        return min(10, severity)


class TelegramMonitor:
    """Monitor Telegram channels for threat intelligence"""
    
    def __init__(self, api_id: Optional[str] = None, api_hash: Optional[str] = None):
        """
        Initialize Telegram monitor
        Requires Telegram API credentials from https://my.telegram.org
        """
        self.api_id = api_id
        self.api_hash = api_hash
        # Note: Actual implementation would use telethon or pyrogram library
    
    async def monitor_channel(self, channel_username: str, keywords: List[str]) -> List[ThreatIntelligence]:
        """
        Monitor a Telegram channel for specific keywords
        
        This is a placeholder - actual implementation requires telethon:
        
        from telethon import TelegramClient
        
        client = TelegramClient('session', api_id, api_hash)
        await client.start()
        
        async for message in client.iter_messages(channel_username, limit=100):
            if any(kw in message.text.lower() for kw in keywords):
                # Process message
        """
        logger.info(f"Monitoring Telegram channel: {channel_username}")
        # Placeholder implementation
        return []


class ShadowTracker:
    """Main ShadowTracker orchestrator"""
    
    def __init__(self, 
                 use_tor: bool = False,
                 telegram_api_id: Optional[str] = None,
                 telegram_api_hash: Optional[str] = None):
        self.paste_scraper = PasteSiteScraper()
        self.forum_scraper = DarkWebForumScraper(use_tor=use_tor)
        self.telegram_monitor = TelegramMonitor(telegram_api_id, telegram_api_hash)
        self.findings_db = []  # In production, use actual database
    
    async def hunt(self, 
                   keywords: List[str],
                   sources: List[str] = None) -> List[ThreatIntelligence]:
        """
        Main hunting method - searches across all configured sources
        
        Args:
            keywords: List of keywords to search for
            sources: List of sources to search (paste_sites, dark_web, telegram)
        """
        if sources is None:
            sources = ['paste_sites']  # Default to paste sites (safest)
        
        all_findings = []
        
        # Scrape paste sites
        if 'paste_sites' in sources:
            logger.info("Scraping paste sites...")
            paste_findings = await self.paste_scraper.scrape_pastebin(keywords)
            all_findings.extend(paste_findings)
        
        # Scrape dark web forums (requires Tor)
        if 'dark_web' in sources:
            logger.info("Scraping dark web forums...")
            # Add your forum URLs here
            forums = []  # e.g., ['http://someforumxyz.onion']
            
            for forum_url in forums:
                forum_findings = await self.forum_scraper.scrape_forum(
                    forum_url, keywords, max_pages=3
                )
                all_findings.extend(forum_findings)
        
        # Monitor Telegram
        if 'telegram' in sources:
            logger.info("Monitoring Telegram channels...")
            # Add your channel usernames here
            channels = []  # e.g., ['@threatintelchannel']
            
            for channel in channels:
                tg_findings = await self.telegram_monitor.monitor_channel(
                    channel, keywords
                )
                all_findings.extend(tg_findings)
        
        # Store findings
        self.findings_db.extend(all_findings)
        
        # Filter and deduplicate
        unique_findings = self._deduplicate(all_findings)
        
        logger.info(f"Found {len(unique_findings)} unique threat intelligence items")
        
        return unique_findings
    
    def _deduplicate(self, findings: List[ThreatIntelligence]) -> List[ThreatIntelligence]:
        """Remove duplicate findings based on content similarity"""
        # Simple deduplication - can be enhanced with fuzzy matching
        seen_urls = set()
        unique = []
        
        for finding in findings:
            if finding.url not in seen_urls:
                seen_urls.add(finding.url)
                unique.append(finding)
        
        return unique
    
    def get_high_severity_findings(self, min_severity: int = 7) -> List[ThreatIntelligence]:
        """Get high-severity findings for alerting"""
        return [f for f in self.findings_db if f.severity >= min_severity]
    
    def export_to_stix(self, findings: List[ThreatIntelligence]) -> Dict:
        """
        Export findings to STIX 2.1 format for threat intelligence sharing
        """
        # Placeholder - actual implementation would use stix2 library
        return {
            "type": "bundle",
            "id": f"bundle--{datetime.now().timestamp()}",
            "objects": [
                {
                    "type": "indicator",
                    "pattern": f"[ipv4-addr:value = '{ioc}']",
                    "labels": ["malicious-activity"]
                }
                for finding in findings
                for ioc in finding.iocs.get('ipv4', [])
            ]
        }


# Example usage
async def main():
    """Example usage of ShadowTracker"""
    
    # Initialize tracker
    tracker = ShadowTracker(use_tor=False)  # Set to True if Tor is configured
    
    # Define your intelligence requirements
    keywords = [
        'data breach',
        'credentials dump',
        'ransomware',
        'your-company-name',  # Monitor mentions of your organization
        'zero-day',
        'exploit'
    ]
    
    # Hunt for intelligence
    findings = await tracker.hunt(
        keywords=keywords,
        sources=['paste_sites']  # Start with paste sites
    )
    
    # Process findings
    for finding in findings:
        print(f"\n{'='*60}")
        print(f"Source: {finding.source}")
        print(f"URL: {finding.url}")
        print(f"Severity: {finding.severity}/10")
        print(f"Threat Actor: {finding.threat_actor}")
        print(f"IOCs Found: {sum(len(v) for v in finding.iocs.values())}")
        print(f"Content Preview: {finding.content[:200]}...")
        
        # Print extracted IOCs
        for ioc_type, ioc_list in finding.iocs.items():
            if ioc_list:
                print(f"\n{ioc_type.upper()}: {', '.join(ioc_list[:5])}")
    
    # Get high-severity alerts
    alerts = tracker.get_high_severity_findings(min_severity=8)
    print(f"\n\n🚨 HIGH SEVERITY ALERTS: {len(alerts)}")


if __name__ == "__main__":
    # Run the tracker
    asyncio.run(main())