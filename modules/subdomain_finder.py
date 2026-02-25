import dns.resolver
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

class SubdomainFinder:
    def __init__(self):
        self.resolver = dns.resolver.Resolver()
        self.resolver.timeout = 2
        self.resolver.lifetime = 2
        
        # Common subdomain wordlist
        self.common_subdomains = [
            'www', 'mail', 'ftp', 'localhost', 'webmail', 'smtp', 'pop', 'ns1',
            'webdisk', 'ns2', 'cpanel', 'whm', 'autodiscover', 'autoconfig',
            'ns', 'm', 'imap', 'test', 'ns3', 'blog', 'pop3', 'dev', 'www2',
            'admin', 'forum', 'news', 'vpn', 'ns4', 'mail2', 'new', 'mysql',
            'old', 'lists', 'support', 'mobile', 'mx', 'static', 'docs', 'beta',
            'shop', 'sql', 'secure', 'demo', 'cp', 'calendar', 'wiki', 'web',
            'media', 'email', 'images', 'img', 'www1', 'intranet', 'portal',
            'video', 'sip', 'dns2', 'api', 'cdn', 'stats', 'dns1', 'ns5',
            'dns', 'search', 'staging', 'server', 'mx1', 'chat', 'wap', 'my',
            'svn', 'mail1', 'sites', 'proxy', 'ads', 'host', 'crm', 'cms'
        ]
    
    def find(self, domain):
        """Find subdomains using multiple techniques"""
        result = {
            'domain': domain,
            'timestamp': datetime.now().isoformat(),
            'subdomains': [],
            'methods': {
                'dns_brute': [],
                'certificate_transparency': [],
                'web_scraping': []
            }
        }
        
        # Method 1: DNS Brute Force
        result['methods']['dns_brute'] = self.dns_brute_force(domain)
        
        # Method 2: Certificate Transparency
        result['methods']['certificate_transparency'] = self.cert_transparency(domain)
        
        # Method 3: Web scraping (crt.sh alternative)
        result['methods']['web_scraping'] = self.web_scrape_subdomains(domain)
        
        # Combine and deduplicate
        all_subdomains = set()
        for method, subs in result['methods'].items():
            all_subdomains.update(subs)
        
        result['subdomains'] = sorted(list(all_subdomains))
        result['total_found'] = len(result['subdomains'])
        
        return result
    
    def dns_brute_force(self, domain):
        """Brute force DNS for subdomains"""
        found_subdomains = []
        
        def check_subdomain(subdomain):
            full_domain = f"{subdomain}.{domain}"
            try:
                answers = self.resolver.resolve(full_domain, 'A')
                ips = [str(rdata) for rdata in answers]
                return {'subdomain': full_domain, 'ips': ips}
            except:
                return None
        
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = {executor.submit(check_subdomain, sub): sub 
                      for sub in self.common_subdomains}
            
            for future in as_completed(futures):
                result = future.result()
                if result:
                    found_subdomains.append(result['subdomain'])
        
        return found_subdomains
    
    def cert_transparency(self, domain):
        """Query Certificate Transparency logs via crt.sh"""
        found_subdomains = []
        
        try:
            url = f"https://crt.sh/?q=%.{domain}&output=json"
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                for entry in data:
                    name_value = entry.get('name_value', '')
                    subdomains = name_value.split('\n')
                    for sub in subdomains:
                        sub = sub.strip()
                        if sub and sub.endswith(domain):
                            found_subdomains.append(sub)
        except Exception as e:
            pass
        
        return list(set(found_subdomains))
    
    def web_scrape_subdomains(self, domain):
        """Alternative web-based subdomain discovery"""
        found_subdomains = []
        
        try:
            # Using HackerTarget API (free tier)
            url = f"https://api.hackertarget.com/hostsearch/?q={domain}"
            response = requests.get(url, timeout=15)
            
            if response.status_code == 200:
                lines = response.text.split('\n')
                for line in lines:
                    if ',' in line:
                        subdomain = line.split(',')[0].strip()
                        if subdomain:
                            found_subdomains.append(subdomain)
        except Exception as e:
            pass
        
        return found_subdomains