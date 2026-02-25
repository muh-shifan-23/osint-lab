import phonenumbers
from phonenumbers import geocoder, carrier, timezone
import requests
from datetime import datetime
import re

class PhoneLookup:
    def __init__(self):
        self.numverify_api_key = None  # User should add their own API key
        self.carriers_database = self.load_carrier_database()
    
    def lookup(self, phone_number):
        """Comprehensive phone number lookup"""
        result = {
            'input_number': phone_number,
            'timestamp': datetime.now().isoformat(),
            'parsed_info': {},
            'validation': {},
            'carrier_info': {},
            'location_info': {},
            'timezone_info': {},
            'formats': {},
            'risk_analysis': {}
        }
        
        # Parse and validate phone number
        parsed_number = self.parse_number(phone_number)
        
        if parsed_number:
            result['parsed_info'] = self.get_parsed_info(parsed_number)
            result['validation'] = self.validate_number(parsed_number)
            result['carrier_info'] = self.get_carrier_info(parsed_number)
            result['location_info'] = self.get_location_info(parsed_number)
            result['timezone_info'] = self.get_timezone_info(parsed_number)
            result['formats'] = self.get_number_formats(parsed_number)
            result['risk_analysis'] = self.analyze_risk(parsed_number)
        else:
            result['error'] = 'Unable to parse phone number'
        
        return result
    
    def parse_number(self, phone_number):
        """Parse phone number using phonenumbers library"""
        try:
            # Try to parse with various region codes
            regions_to_try = ['US', 'GB', 'IN', 'CA', 'AU', None]
            
            for region in regions_to_try:
                try:
                    parsed = phonenumbers.parse(phone_number, region)
                    if phonenumbers.is_valid_number(parsed):
                        return parsed
                except:
                    continue
            
            # If all else fails, try without region
            return phonenumbers.parse(phone_number, None)
        except Exception as e:
            return None
    
    def get_parsed_info(self, parsed_number):
        """Get basic parsed information"""
        return {
            'country_code': parsed_number.country_code,
            'national_number': parsed_number.national_number,
            'extension': parsed_number.extension,
            'italian_leading_zero': parsed_number.italian_leading_zero,
            'raw_input': parsed_number.raw_input,
            'country_code_source': str(parsed_number.country_code_source)
        }
    
    def validate_number(self, parsed_number):
        """Validate phone number"""
        try:
            return {
                'is_valid': phonenumbers.is_valid_number(parsed_number),
                'is_possible': phonenumbers.is_possible_number(parsed_number),
                'number_type': self.get_number_type(parsed_number),
                'region_code': phonenumbers.region_code_for_number(parsed_number)
            }
        except Exception as e:
            return {'error': str(e)}
    
    def get_number_type(self, parsed_number):
        """Get the type of phone number"""
        number_type = phonenumbers.number_type(parsed_number)
        
        type_mapping = {
            0: 'FIXED_LINE',
            1: 'MOBILE',
            2: 'FIXED_LINE_OR_MOBILE',
            3: 'TOLL_FREE',
            4: 'PREMIUM_RATE',
            5: 'SHARED_COST',
            6: 'VOIP',
            7: 'PERSONAL_NUMBER',
            8: 'PAGER',
            9: 'UAN',
            10: 'VOICEMAIL',
            -1: 'UNKNOWN'
        }
        
        return type_mapping.get(number_type, 'UNKNOWN')
    
    def get_carrier_info(self, parsed_number):
        """Get carrier information"""
        try:
            carrier_name = carrier.name_for_number(parsed_number, 'en')
            
            return {
                'carrier': carrier_name if carrier_name else 'Unknown',
                'carrier_type': self.get_number_type(parsed_number)
            }
        except Exception as e:
            return {'error': str(e)}
    
    def get_location_info(self, parsed_number):
        """Get geographic location information"""
        try:
            location = geocoder.description_for_number(parsed_number, 'en')
            country = geocoder.country_name_for_number(parsed_number, 'en')
            region_code = phonenumbers.region_code_for_number(parsed_number)
            
            return {
                'location': location if location else 'Unknown',
                'country': country if country else 'Unknown',
                'region_code': region_code,
                'country_code': parsed_number.country_code
            }
        except Exception as e:
            return {'error': str(e)}
    
    def get_timezone_info(self, parsed_number):
        """Get timezone information"""
        try:
            timezones = timezone.time_zones_for_number(parsed_number)
            
            return {
                'timezones': list(timezones) if timezones else [],
                'primary_timezone': timezones[0] if timezones else 'Unknown'
            }
        except Exception as e:
            return {'error': str(e)}
    
    def get_number_formats(self, parsed_number):
        """Get various number formats"""
        try:
            return {
                'e164': phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164),
                'international': phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL),
                'national': phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.NATIONAL),
                'rfc3966': phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.RFC3966)
            }
        except Exception as e:
            return {'error': str(e)}
    
    def analyze_risk(self, parsed_number):
        """Analyze potential risks associated with the number"""
        risk_factors = []
        risk_score = 0
        
        try:
            # Check if it's a valid number
            if not phonenumbers.is_valid_number(parsed_number):
                risk_factors.append('Invalid number format')
                risk_score += 30
            
            # Check number type
            number_type = self.get_number_type(parsed_number)
            if number_type in ['VOIP', 'PREMIUM_RATE']:
                risk_factors.append(f'Number type: {number_type}')
                risk_score += 20
            
            if number_type == 'UNKNOWN':
                risk_factors.append('Unknown number type')
                risk_score += 15
            
            # Check carrier
            carrier_name = carrier.name_for_number(parsed_number, 'en')
            if not carrier_name or carrier_name == '':
                risk_factors.append('No carrier information available')
                risk_score += 10
            
            # Risk level classification
            if risk_score >= 50:
                risk_level = 'HIGH'
            elif risk_score >= 30:
                risk_level = 'MEDIUM'
            elif risk_score >= 10:
                risk_level = 'LOW'
            else:
                risk_level = 'MINIMAL'
            
            return {
                'risk_score': risk_score,
                'risk_level': risk_level,
                'risk_factors': risk_factors,
                'recommendation': self.get_risk_recommendation(risk_level)
            }
        except Exception as e:
            return {'error': str(e)}
    
    def get_risk_recommendation(self, risk_level):
        """Get recommendation based on risk level"""
        recommendations = {
            'HIGH': 'Exercise caution. This number shows multiple risk indicators.',
            'MEDIUM': 'Be cautious. Some risk factors detected.',
            'LOW': 'Low risk detected. Standard precautions recommended.',
            'MINIMAL': 'Number appears legitimate. Minimal risk detected.'
        }
        return recommendations.get(risk_level, 'Unable to determine risk level')
    
    def load_carrier_database(self):
        """Load carrier database (placeholder for extended functionality)"""
        # This could be extended with a database of known carriers
        return {}
    
    def lookup_with_numverify(self, phone_number):
        """Lookup using Numverify API (requires API key)"""
        if not self.numverify_api_key:
            return {
                'error': 'Numverify API key not configured',
                'note': 'Get a free API key from https://numverify.com/'
            }
        
        try:
            url = f"http://apilayer.net/api/validate"
            params = {
                'access_key': self.numverify_api_key,
                'number': phone_number,
                'country_code': '',
                'format': 1
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {'error': f'API returned status code {response.status_code}'}
        except Exception as e:
            return {'error': str(e)}
    
    def search_phone_in_social_media(self, phone_number):
        """Search for phone number mentions on social media (basic)"""
        # This is a placeholder for social media search functionality
        result = {
            'phone_number': phone_number,
            'search_note': 'Social media search requires platform-specific APIs',
            'recommendations': [
                'Search manually on Facebook using the phone number',
                'Try WhatsApp to see if profile exists',
                'Check LinkedIn connections',
                'Use Truecaller app for crowd-sourced information'
            ]
        }
        return result
    
    def format_for_whatsapp(self, parsed_number):
        """Format number for WhatsApp"""
        try:
            # WhatsApp uses E164 format without the + sign
            e164 = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
            whatsapp_number = e164.replace('+', '')
            
            return {
                'whatsapp_number': whatsapp_number,
                'whatsapp_link': f"https://wa.me/{whatsapp_number}",
                'whatsapp_api_link': f"https://api.whatsapp.com/send?phone={whatsapp_number}"
            }
        except Exception as e:
            return {'error': str(e)}
    
    def bulk_lookup(self, phone_numbers):
        """Lookup multiple phone numbers"""
        results = []
        
        for phone in phone_numbers:
            try:
                result = self.lookup(phone)
                results.append(result)
            except Exception as e:
                results.append({
                    'phone_number': phone,
                    'error': str(e)
                })
        
        return {
            'total_numbers': len(phone_numbers),
            'results': results,
            'timestamp': datetime.now().isoformat()
        }