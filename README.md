# 🔍 OSINT Lab - Cyber Intelligence Platform

![OSINT Lab Banner](static/img/banner.png)

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/muh-shifan-2003/osint-lab.svg)](https://github.com/yourusername/osint-lab/stargazers)
[![GitHub Issues](https://img.shields.io/github/issues/muh-shifan-2003/osint-lab.svg)](https://github.com/yourusername/osint-lab/issues)

A unified web-based Open Source Intelligence platform that integrates multiple free intelligence gathering tools for cybersecurity and investigation purposes.

## 🌟 Features

### Core Modules
- 🌐 **Domain Analysis** - WHOIS, DNS, SSL certificates, HTTP headers
- 📍 **IP Investigation** - Geolocation, reverse DNS, port scanning, threat intelligence
- 🔎 **Subdomain Finder** - DNS brute force, certificate transparency, web scraping
- 📄 **Metadata Extractor** - EXIF from images, PDF metadata, DOCX properties
- 📧 **Email OSINT** - Email validation, breach checking, domain verification
- 👤 **Social Media OSINT** - Username search across 15+ platforms
- 📱 **Phone Number Lookup** - Carrier identification, location, risk analysis
- 🕵️ **Dark Web Intelligence** - IOC extraction, paste site monitoring, threat hunting
- 📊 **Report Generator** - Export findings in JSON, CSV, HTML, TXT

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip package manager
- (Optional) Tor for dark web access

### Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/osint-lab.git
cd osint-lab

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

Open your browser and navigate to `http://localhost:5000`

## 📚 Documentation

- [Installation Guide](docs/INSTALLATION.md)
- [Usage Guide](docs/USAGE.md)
- [API Documentation](docs/API.md)
- [Module Documentation](docs/MODULES.md)
- [Contributing Guidelines](docs/CONTRIBUTING.md)

## 🎯 Usage Examples

### Domain Analysis
```python
from modules.domain_analysis import DomainAnalyzer

analyzer = DomainAnalyzer()
result = analyzer.analyze('example.com')
print(result)
```

### Phone Number Lookup
```python
from modules.phone_lookup import PhoneLookup

lookup = PhoneLookup()
result = lookup.lookup('+14155552671')
print(f"Country: {result['location_info']['country']}")
```

### IOC Extraction
```python
from modules.shadow_tracker import IOCExtractor

text = "Malicious IP: 192.168.1.100, domain: evil.com"
iocs = IOCExtractor.extract(text)
print(iocs)
```

## 🔧 Configuration

Create a `config.py` file for custom settings:
```python
class Config:
    SECRET_KEY = 'your-secret-key'
    ABUSEIPDB_API_KEY = 'your-api-key'
    HIBP_API_KEY = 'your-api-key'
    NUMVERIFY_API_KEY = 'your-api-key'
```

## 🛡️ Security & Ethics

⚠️ **IMPORTANT**: This tool is for authorized security research and educational purposes only.

- ✅ Only investigate domains/IPs you own or have permission to test
- ✅ Respect rate limits and terms of service
- ✅ Follow local laws and regulations
- ✅ Handle collected data responsibly
- ❌ Do NOT use for illegal activities
- ❌ Do NOT access unauthorized systems

## 📊 Supported Platforms

### Social Media (15+ Platforms)
- GitHub, Reddit, Twitter, Instagram, LinkedIn
- Facebook, YouTube, TikTok, Pinterest, Medium
- Twitch, Snapchat, Telegram, Discord, Spotify

### Data Sources
- WHOIS databases
- DNS records
- Certificate Transparency logs
- IP geolocation services
- Paste sites (Pastebin, etc.)
- Public breach databases

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guidelines](docs/CONTRIBUTING.md) first.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with Flask, dnspython, python-whois, and many other open-source tools
- Inspired by the OSINT community
- Thanks to all contributors

## 📞 Support

- 📫 Issues: [GitHub Issues](https://github.com/muh-shifan-2003/osint-lab/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/muh-shifan-2003/osint-lab/discussions)
- 📧 Email: your.email@example.com

## ⚠️ Disclaimer

This tool is intended for legitimate security research, authorized penetration testing, and educational purposes only. Users are responsible for complying with applicable laws and obtaining necessary permissions before conducting any investigations.

---

**Made with ❤️ by the OSINT community**

**⭐ Star this repo if you find it useful!**
