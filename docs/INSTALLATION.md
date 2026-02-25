# Installation Guide

## System Requirements

- Python 3.8 or higher
- 2GB RAM minimum
- Internet connection
- (Optional) Tor for dark web access

## Step-by-Step Installation

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/osint-lab.git
cd osint-lab
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# Activate on Linux/Mac
source venv/bin/activate

# Activate on Windows
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure (Optional)

Create `config.py` with your API keys:
```python
class Config:
    SECRET_KEY = 'your-secret-key-here'
    ABUSEIPDB_API_KEY = 'your-key'
    HIBP_API_KEY = 'your-key'
    NUMVERIFY_API_KEY = 'your-key'
```

### 5. Run Application
```bash
python app.py
```

Open browser: `http://localhost:5000`

## Optional: Tor Setup

For dark web access:
```bash
# Ubuntu/Debian
sudo apt-get install tor
sudo service tor start

# macOS
brew install tor
brew services start tor
```

Enable in `app.py`:
```python
shadow_tracker = ShadowTracker(use_tor=True)
```

## Troubleshooting

**Port 5000 in use:**
```python
# In app.py, change:
app.run(debug=True, port=5001)
```

**Module not found:**
```bash
pip install -r requirements.txt --upgrade
```

**Permission denied:**
```bash
chmod +x scripts/setup.sh
```
