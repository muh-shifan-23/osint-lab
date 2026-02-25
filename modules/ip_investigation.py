import requests
import socket
from datetime import datetime

class IPInvestigator:
    def __init__(self):
        self.ipapi_url = "http://ip-api.com/json/"
        self.shodan_alternatives = [
            "https://ipinfo.io/",
            "http://ip-api.com/json/"
        ]
    
    def investigate(self, ip):
        """Comprehensive IP investigation"""
        result = {
            'ip': ip,
            'timestamp': datetime.now().isoformat(),
            'geolocation': self.get_geolocation(ip),
            'reverse_dns': self.get_reverse_dns(ip),
            'whois': self.get_ip_whois(ip),
            'threat_intelligence': self.check_threat_intel(ip),
            'open_ports': self.scan_common_ports(ip)
        }
        return result
    
    def get_geolocation(self, ip):
        """Get IP geolocation using ip-api.com (free)"""
        try:
            response = requests.get(f"{self.ipapi_url}{ip}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return {
                    'country': data.get('country'),
                    'country_code': data.get('countryCode'),
                    'region': data.get('regionName'),
                    'city': data.get('city'),
                    'zip': data.get('zip'),
                    'lat': data.get('lat'),
                    'lon': data.get('lon'),
                    'timezone': data.get('timezone'),
                    'isp': data.get('isp'),
                    'org': data.get('org'),
                    'as': data.get('as'),
                    'query': data.get('query')
                }
        except Exception as e:
            return {'error': str(e)}
    
    def get_reverse_dns(self, ip):
        """Get reverse DNS"""
        try:
            hostname = socket.gethostbyaddr(ip)
            return {
                'hostname': hostname[0],
                'aliases': hostname[1]
            }
        except Exception as e:
            return {'error': str(e)}
    
    def get_ip_whois(self, ip):
        """Get IP WHOIS information"""
        try:
            import ipwhois
            obj = ipwhois.IPWhois(ip)
            results = obj.lookup_rdap()
            return {
                'asn': results.get('asn'),
                'asn_description': results.get('asn_description'),
                'asn_country_code': results.get('asn_country_code'),
                'network': results.get('network', {}).get('cidr'),
                'network_name': results.get('network', {}).get('name'),
                'registry': results.get('asn_registry')
            }
        except Exception as e:
            return {'error': str(e)}
    
    def check_threat_intel(self, ip):
        """Check IP against threat intelligence (AbuseIPDB free tier)"""
        try:
            # Using AbuseIPDB free API (requires API key - user should add their own)
            # For demo, using IPVoid API alternative
            url = f"https://api.abuseipdb.com/api/v2/check"
            headers = {
                'Accept': 'application/json',
                'Key': 'YOUR_API_KEY_HERE'  # User needs to replace this
            }
            params = {
                'ipAddress': ip,
                'maxAgeInDays': '90'
            }
            
            # Note: This requires API key. Alternative free check:
            return {
                'note': 'Add your AbuseIPDB API key for threat intelligence',
                'abuseConfidenceScore': None,
                'totalReports': None
            }
        except Exception as e:
            return {'error': str(e)}
    
    def scan_common_ports(self, ip):
        """Scan common ports (basic, non-intrusive)"""
        common_ports = {
            21: 'FTP',
            22: 'SSH',
            23: 'Telnet',
            25: 'SMTP',
            53: 'DNS',
            80: 'HTTP',
            443: 'HTTPS',
            3306: 'MySQL',
            3389: 'RDP',
            8080: 'HTTP-Proxy'
        }
        
        open_ports = []
        
        for port, service in common_ports.items():
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex((ip, port))
                if result == 0:
                    open_ports.append({
                        'port': port,
                        'service': service,
                        'state': 'open'
                    })
                sock.close()
            except:
                pass
        
        return open_ports