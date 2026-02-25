from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os

# Import OSINT modules
from modules.domain_analysis import DomainAnalyzer
from modules.ip_investigation import IPInvestigator
from modules.metadata_extractor import MetadataExtractor
from modules.subdomain_finder import SubdomainFinder
from modules.email_osint import EmailOSINT
from modules.social_media_osint import SocialMediaOSINT
from modules.phone_lookup import PhoneLookup
from modules.shadow_tracker import ShadowTracker, IOCExtractor
import asyncio

app = Flask(__name__)
CORS(app)

# Initialize OSINT modules
domain_analyzer = DomainAnalyzer()
ip_investigator = IPInvestigator()
metadata_extractor = MetadataExtractor()
subdomain_finder = SubdomainFinder()
email_osint = EmailOSINT()
social_media_osint = SocialMediaOSINT()
phone_lookup = PhoneLookup()
shadow_tracker = ShadowTracker(use_tor=True)  # Set to True if Tor is configured

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/domain/analyze', methods=['POST'])
def analyze_domain():
    try:
        data = request.get_json()
        domain = data.get('domain')
        
        if not domain:
            return jsonify({'error': 'Domain is required'}), 400
        
        result = domain_analyzer.analyze(domain)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ip/investigate', methods=['POST'])
def investigate_ip():
    try:
        data = request.get_json()
        ip = data.get('ip')
        
        if not ip:
            return jsonify({'error': 'IP address is required'}), 400
        
        result = ip_investigator.investigate(ip)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/subdomain/find', methods=['POST'])
def find_subdomains():
    try:
        data = request.get_json()
        domain = data.get('domain')
        
        if not domain:
            return jsonify({'error': 'Domain is required'}), 400
        
        result = subdomain_finder.find(domain)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/metadata/extract', methods=['POST'])
def extract_metadata():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Save temporarily
        temp_path = os.path.join('temp', file.filename)
        os.makedirs('temp', exist_ok=True)
        file.save(temp_path)
        
        try:
            result = metadata_extractor.extract(temp_path)
        except Exception as extract_error:
            # Log the actual error
            import traceback
            error_details = traceback.format_exc()
            print(f"Extraction Error: {error_details}")
            result = {
                'error': str(extract_error),
                'error_type': type(extract_error).__name__,
                'filename': file.filename
            }
        finally:
            # Clean up - always remove temp file
            try:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
            except:
                pass
        
        return jsonify(result)
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Route Error: {error_details}")
        return jsonify({'error': str(e), 'details': error_details}), 500

@app.route('/api/email/analyze', methods=['POST'])
def analyze_email():
    try:
        data = request.get_json()
        email = data.get('email')
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        result = email_osint.analyze(email)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/social/search', methods=['POST'])
def search_social_media():
    try:
        data = request.get_json()
        username = data.get('username')
        
        if not username:
            return jsonify({'error': 'Username is required'}), 400
        
        result = social_media_osint.search_username(username)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/social/profile', methods=['POST'])
def get_social_profile():
    try:
        data = request.get_json()
        platform = data.get('platform')
        username = data.get('username')
        
        if not platform or not username:
            return jsonify({'error': 'Platform and username are required'}), 400
        
        result = social_media_osint.analyze_profile(platform, username)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/phone/lookup', methods=['POST'])
def lookup_phone():
    try:
        data = request.get_json()
        phone = data.get('phone')
        
        if not phone:
            return jsonify({'error': 'Phone number is required'}), 400
        
        result = phone_lookup.lookup(phone)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/darkweb/hunt', methods=['POST'])
def darkweb_hunt():
    try:
        data = request.get_json()
        keywords = data.get('keywords', [])
        sources = data.get('sources', ['paste_sites'])
        
        if not keywords:
            return jsonify({'error': 'Keywords are required'}), 400
        
        # Run async hunt
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        findings = loop.run_until_complete(
            shadow_tracker.hunt(keywords, sources)
        )
        loop.close()
        
        # Convert findings to JSON-serializable format
        result = {
            'total_findings': len(findings),
            'findings': [
                {
                    'source': f.source,
                    'url': f.url,
                    'severity': f.severity,
                    'threat_actor': f.threat_actor,
                    'timestamp': f.timestamp.isoformat(),
                    'tags': f.tags,
                    'iocs': f.iocs,
                    'content_preview': f.content[:200]
                }
                for f in findings
            ]
        }
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/darkweb/extract-iocs', methods=['POST'])
def extract_iocs():
    try:
        data = request.get_json()
        text = data.get('text')
        
        if not text:
            return jsonify({'error': 'Text is required'}), 400
        
        iocs = IOCExtractor.extract(text)
        
        return jsonify({
            'iocs': iocs,
            'total_iocs': sum(len(v) for v in iocs.values())
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)