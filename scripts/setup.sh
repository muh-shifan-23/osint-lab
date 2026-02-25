#!/bin/bash

# OSINT Lab - Automated Setup Script
# This script automates the installation process

echo "========================================"
echo "  🔍 OSINT Lab - Automated Setup"
echo "========================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Check Python version
print_info "Checking Python version..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    print_success "Python 3 found: $(python3 --version)"
    
    # Check if version is 3.8 or higher
    if (( $(echo "$PYTHON_VERSION >= 3.8" | bc -l) )); then
        print_success "Python version is compatible (>= 3.8)"
    else
        print_error "Python 3.8 or higher is required"
        exit 1
    fi
else
    print_error "Python 3 is not installed"
    echo "Please install Python 3.8 or higher from https://www.python.org/"
    exit 1
fi

# Check pip
print_info "Checking pip..."
if command -v pip3 &> /dev/null; then
    print_success "pip3 found: $(pip3 --version)"
else
    print_error "pip3 is not installed"
    echo "Please install pip3"
    exit 1
fi

# Create virtual environment
print_info "Creating virtual environment..."
if [ -d "venv" ]; then
    print_warning "Virtual environment already exists. Skipping..."
else
    python3 -m venv venv
    print_success "Virtual environment created"
fi

# Activate virtual environment
print_info "Activating virtual environment..."
source venv/bin/activate
print_success "Virtual environment activated"

# Upgrade pip
print_info "Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1
print_success "pip upgraded"

# Install dependencies
print_info "Installing dependencies from requirements.txt..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    print_success "All dependencies installed"
else
    print_error "requirements.txt not found!"
    exit 1
fi

# Create necessary directories
print_info "Creating necessary directories..."
directories=("modules" "templates" "static" "static/css" "static/js" "static/img" "temp" "tests" "docs" "scripts" "examples")

for dir in "${directories[@]}"; do
    if [ ! -d "$dir" ]; then
        mkdir -p "$dir"
        print_success "Created $dir/"
    else
        print_warning "$dir/ already exists"
    fi
done

# Create __init__.py files
print_info "Creating __init__.py files..."
init_dirs=("modules" "tests")

for dir in "${init_dirs[@]}"; do
    if [ ! -f "$dir/__init__.py" ]; then
        touch "$dir/__init__.py"
        print_success "Created $dir/__init__.py"
    else
        print_warning "$dir/__init__.py already exists"
    fi
done

# Create .gitignore if it doesn't exist
print_info "Creating .gitignore..."
if [ ! -f ".gitignore" ]; then
    cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/
*.egg-info/
dist/
build/

# Flask
instance/
.webassets-cache

# Environment
.env
config_local.py

# IDE
.vscode/
.idea/
*.swp

# Project
temp/
*.db
*.log

# OS
.DS_Store
Thumbs.db
EOF
    print_success "Created .gitignore"
else
    print_warning ".gitignore already exists"
fi

# Create config template
print_info "Creating config template..."
if [ ! -f "config.py" ]; then
    cat > config.py << 'EOF'
import os

class Config:
    """Application configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # API Keys (Optional - Get free keys)
    ABUSEIPDB_API_KEY = os.environ.get('ABUSEIPDB_API_KEY', '')
    HIBP_API_KEY = os.environ.get('HIBP_API_KEY', '')
    VIRUSTOTAL_API_KEY = os.environ.get('VIRUSTOTAL_API_KEY', '')
    NUMVERIFY_API_KEY = os.environ.get('NUMVERIFY_API_KEY', '')
    
    # Upload settings
    MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = 'temp'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'docx', 'doc'}
EOF
    print_success "Created config.py"
else
    print_warning "config.py already exists"
fi

# Check if app.py exists
print_info "Checking application files..."
if [ -f "app.py" ]; then
    print_success "app.py found"
else
    print_warning "app.py not found - you need to create it"
fi

# Check if modules exist
if [ -f "modules/domain_analysis.py" ]; then
    print_success "OSINT modules found"
else
    print_warning "OSINT modules not found - you need to add them to modules/"
fi

# Check if template exists
if [ -f "templates/index.html" ]; then
    print_success "Frontend template found"
else
    print_warning "Frontend template not found - you need to add index.html to templates/"
fi

# Check for Tor (optional)
print_info "Checking for Tor (optional)..."
if command -v tor &> /dev/null; then
    print_success "Tor is installed"
    print_info "To enable dark web features, set use_tor=True in app.py"
else
    print_warning "Tor is not installed (optional for dark web features)"
    print_info "To install Tor:"
    print_info "  Ubuntu/Debian: sudo apt-get install tor"
    print_info "  macOS: brew install tor"
fi

echo ""
echo "========================================"
echo "  ✓ Setup Complete!"
echo "========================================"
echo ""
print_info "Next steps:"
echo "  1. Add your module files to modules/"
echo "  2. Add index.html to templates/"
echo "  3. Configure API keys in config.py (optional)"
echo "  4. Run the application:"
echo ""
echo "     source venv/bin/activate  # Activate virtual environment"
echo "     python app.py              # Start the application"
echo ""
echo "  5. Open browser: http://localhost:5000"
echo ""
print_success "Happy OSINT hunting! 🔍"
echo ""
