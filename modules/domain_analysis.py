import whois
import dns.resolver
import socket
import requests
from datetime import datetime

class DomainAnalyzer:
    def __init__(self):
        self.resolver = dns.resolver.Resolver()
        
    def analyze(self, domain):
        """Comprehensive domain analysis"""
        result = {
            'domain': domain,
            'timestamp': datetime.now().isoformat(),
            'whois': self.get_whois_info(domain),
            'dns': self.get_dns_records(domain),
            'http_headers': self.get_http_headers(domain),
            'ssl_info': self.check_ssl(domain)
        }
        return result
    
    def get_whois_info(self, domain):
        """Get WHOIS information"""
        try:
            w = whois.whois(domain)
            return {
                'registrar': w.registrar,
                'creation_date': str(w.creation_date),
                'expiration_date': str(w.expiration_date),
                'updated_date': str(w.updated_date),
                'name_servers': w.name_servers,
                'status': w.status,
                'emails': w.emails,
                'org': w.org,
                'country': w.country
            }
        except Exception as e:
            return {'error': str(e)}
    
    def get_dns_records(self, domain):
        """Get DNS records"""
        records = {}
        record_types = ['A', 'AAAA', 'MX', 'NS', 'TXT', 'CNAME', 'SOA']
        
        for record_type in record_types:
            try:
                answers = self.resolver.resolve(domain, record_type)
                records[record_type] = [str(rdata) for rdata in answers]
            except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, Exception):
                records[record_type] = []
        
        return records
    
    def get_http_headers(self, domain):
        """Get HTTP headers"""
        try:
            response = requests.get(f'http://{domain}', timeout=10, allow_redirects=True)
            return {
                'status_code': response.status_code,
                'headers': dict(response.headers),
                'final_url': response.url
            }
        except Exception as e:
            return {'error': str(e)}
    
    def check_ssl(self, domain):
        """Check SSL certificate"""
        try:
            import ssl
            import OpenSSL
            
            context = ssl.create_default_context()
            with socket.create_connection((domain, 443), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert = ssock.getpeercert()
                    
                    return {
                        'subject': dict(x[0] for x in cert['subject']),
                        'issuer': dict(x[0] for x in cert['issuer']),
                        'version': cert['version'],
                        'serialNumber': cert['serialNumber'],
                        'notBefore': cert['notBefore'],
                        'notAfter': cert['notAfter'],
                        'subjectAltName': cert.get('subjectAltName', [])
                    }
        except Exception as e:
            return {'error': str(e)}