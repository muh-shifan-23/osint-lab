import re
import requests
import dns.resolver
from datetime import datetime

class EmailOSINT:
    def __init__(self):
        self.resolver = dns.resolver.Resolver()
    
    def analyze(self, email):
        """Comprehensive email analysis"""
        result = {
            'email': email,
            'timestamp': datetime.now().isoformat(),
            'valid_format': self.validate_email_format(email),
            'domain': self.extract_domain(email),
            'username': self.extract_username(email),
            'domain_info': {},
            'breach_check': {},
            'disposable_check': False
        }
        
        if result['valid_format']:
            domain = result['domain']
            result['domain_info'] = self.check_domain(domain)
            result['disposable_check'] = self.check_disposable(domain)
            result['breach_check'] = self.check_breaches(email)
        
        return result
    
    def validate_email_format(self, email):
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def extract_domain(self, email):
        """Extract domain from email"""
        try:
            return email.split('@')[1]
        except:
            return None
    
    def extract_username(self, email):
        """Extract username from email"""
        try:
            return email.split('@')[0]
        except:
            return None
    
    def check_domain(self, domain):
        """Check domain validity and MX records"""
        info = {
            'has_mx_records': False,
            'mx_records': [],
            'spf_record': None,
            'dmarc_record': None
        }
        
        # Check MX records
        try:
            mx_records = self.resolver.resolve(domain, 'MX')
            info['has_mx_records'] = True
            info['mx_records'] = [str(r.exchange) for r in mx_records]
        except:
            pass
        
        # Check SPF record
        try:
            txt_records = self.resolver.resolve(domain, 'TXT')
            for txt in txt_records:
                txt_str = str(txt)
                if 'v=spf1' in txt_str:
                    info['spf_record'] = txt_str
                    break
        except:
            pass
        
        # Check DMARC record
        try:
            dmarc_domain = f'_dmarc.{domain}'
            dmarc_records = self.resolver.resolve(dmarc_domain, 'TXT')
            for record in dmarc_records:
                record_str = str(record)
                if 'v=DMARC1' in record_str:
                    info['dmarc_record'] = record_str
                    break
        except:
            pass
        
        return info
    
    def check_disposable(self, domain):
        """Check if email domain is disposable"""
        # List of common disposable email domains
        disposable_domains = [
            'tempmail.com', '10minutemail.com', 'guerrillamail.com',
            'mailinator.com', 'maildrop.cc', 'throwaway.email',
            'yopmail.com', 'temp-mail.org', 'getnada.com', 'trashmail.com'
        ]
        
        return domain.lower() in disposable_domains
    
    def check_breaches(self, email):
        """Check if email appears in data breaches (using HaveIBeenPwned API)"""
        # Note: HIBP API requires API key for automated checks
        # This is a placeholder implementation
        
        try:
            # For demo purposes - users should add their own HIBP API key
            headers = {
                'User-Agent': 'OSINT-Lab',
                'hibp-api-key': 'YOUR_API_KEY_HERE'
            }
            
            url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}"
            
            # Note: Actual implementation requires API key
            return {
                'note': 'Add your HaveIBeenPwned API key for breach checks',
                'breaches_found': None,
                'status': 'API key required'
            }
        except Exception as e:
            return {'error': str(e)}
    
    def social_media_check(self, email):
        """Check for social media profiles (basic implementation)"""
        # This would require various social media APIs
        # Here's a basic structure
        
        platforms = {
            'github': f"https://github.com/{email.split('@')[0]}",
            'twitter': f"https://twitter.com/{email.split('@')[0]}",
            'linkedin': f"https://linkedin.com/in/{email.split('@')[0]}"
        }
        
        results = {}
        for platform, url in platforms.items():
            try:
                response = requests.head(url, timeout=5, allow_redirects=True)
                results[platform] = {
                    'url': url,
                    'exists': response.status_code == 200
                }
            except:
                results[platform] = {
                    'url': url,
                    'exists': False
                }
        
        return results