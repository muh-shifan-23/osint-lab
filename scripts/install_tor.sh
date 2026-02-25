#!/bin/bash

# OSINT Lab - Tor Installation Script
# Automatically installs and configures Tor for dark web access

echo "========================================"
echo "  🕵️  OSINT Lab - Tor Installation"
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

# Detect OS
print_info "Detecting operating system..."

if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
    print_success "Detected: Linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
    print_success "Detected: macOS"
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
    OS="windows"
    print_success "Detected: Windows"
else
    print_error "Unknown operating system: $OSTYPE"
    exit 1
fi

# Check if Tor is already installed
print_info "Checking if Tor is already installed..."
if command -v tor &> /dev/null; then
    TOR_VERSION=$(tor --version | head -n 1)
    print_warning "Tor is already installed: $TOR_VERSION"
    read -p "Do you want to reinstall/update Tor? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Skipping Tor installation"
        exit 0
    fi
fi

# Install Tor based on OS
case $OS in
    linux)
        print_info "Installing Tor on Linux..."
        
        # Detect Linux distribution
        if [ -f /etc/os-release ]; then
            . /etc/os-release
            DISTRO=$ID
        else
            print_error "Cannot detect Linux distribution"
            exit 1
        fi
        
        case $DISTRO in
            ubuntu|debian)
                print_info "Detected: Ubuntu/Debian"
                print_info "Updating package list..."
                sudo apt-get update
                
                print_info "Installing Tor..."
                sudo apt-get install -y tor
                
                print_success "Tor installed successfully"
                
                # Start Tor service
                print_info "Starting Tor service..."
                sudo systemctl start tor
                sudo systemctl enable tor
                
                print_success "Tor service started and enabled"
                ;;
                
            fedora|rhel|centos)
                print_info "Detected: Fedora/RHEL/CentOS"
                print_info "Installing Tor..."
                sudo dnf install -y tor || sudo yum install -y tor
                
                print_success "Tor installed successfully"
                
                # Start Tor service
                print_info "Starting Tor service..."
                sudo systemctl start tor
                sudo systemctl enable tor
                
                print_success "Tor service started and enabled"
                ;;
                
            arch)
                print_info "Detected: Arch Linux"
                print_info "Installing Tor..."
                sudo pacman -S --noconfirm tor
                
                print_success "Tor installed successfully"
                
                # Start Tor service
                print_info "Starting Tor service..."
                sudo systemctl start tor
                sudo systemctl enable tor
                
                print_success "Tor service started and enabled"
                ;;
                
            *)
                print_error "Unsupported Linux distribution: $DISTRO"
                print_info "Please install Tor manually:"
                print_info "https://www.torproject.org/download/"
                exit 1
                ;;
        esac
        ;;
        
    macos)
        print_info "Installing Tor on macOS..."
        
        # Check if Homebrew is installed
        if ! command -v brew &> /dev/null; then
            print_error "Homebrew is not installed"
            print_info "Please install Homebrew first:"
            print_info "/bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
            exit 1
        fi
        
        print_success "Homebrew found"
        
        print_info "Installing Tor via Homebrew..."
        brew install tor
        
        print_success "Tor installed successfully"
        
        # Start Tor service
        print_info "Starting Tor service..."
        brew services start tor
        
        print_success "Tor service started"
        ;;
        
    windows)
        print_warning "Automated installation not available for Windows"
        print_info "Please install Tor manually:"
        echo ""
        print_info "Option 1: Tor Browser (Easiest)"
        print_info "  Download: https://www.torproject.org/download/"
        echo ""
        print_info "Option 2: Tor Expert Bundle"
        print_info "  Download: https://www.torproject.org/download/tor/"
        print_info "  Extract and run tor.exe"
        echo ""
        exit 0
        ;;
esac

# Wait for Tor to start
print_info "Waiting for Tor to initialize..."
sleep 5

# Verify Tor installation
print_info "Verifying Tor installation..."

# Check if Tor process is running
if pgrep -x "tor" > /dev/null; then
    print_success "Tor process is running"
else
    print_warning "Tor process not detected. Trying to start manually..."
    
    case $OS in
        linux)
            sudo systemctl start tor
            sleep 3
            ;;
        macos)
            brew services start tor
            sleep 3
            ;;
    esac
fi

# Check if Tor is listening on port 9050
print_info "Checking if Tor is listening on port 9050..."
if netstat -an 2>/dev/null | grep -q ":9050" || lsof -i :9050 2>/dev/null | grep -q "LISTEN"; then
    print_success "Tor is listening on port 9050"
else
    print_warning "Port 9050 not detected. Tor might still be starting..."
    print_info "Wait a few seconds and check with: netstat -an | grep 9050"
fi

# Test Tor connection
print_info "Testing Tor connection..."
TEST_RESULT=$(curl -s --socks5 127.0.0.1:9050 https://check.torproject.org/ 2>&1)

if echo "$TEST_RESULT" | grep -q "Congratulations"; then
    print_success "Tor connection test PASSED"
    print_success "You are successfully connected through Tor!"
else
    print_warning "Tor connection test inconclusive"
    print_info "Tor might need a few more seconds to fully initialize"
    print_info "You can test manually with:"
    print_info "  curl --socks5 127.0.0.1:9050 https://check.torproject.org/"
fi

# Configure Tor for OSINT Lab
print_info "Configuring Tor for OSINT Lab..."

# Check if torrc exists
if [ -f /etc/tor/torrc ] || [ -f /usr/local/etc/tor/torrc ]; then
    TORRC_PATH=""
    
    if [ -f /etc/tor/torrc ]; then
        TORRC_PATH="/etc/tor/torrc"
    elif [ -f /usr/local/etc/tor/torrc ]; then
        TORRC_PATH="/usr/local/etc/tor/torrc"
    fi
    
    print_info "Found Tor configuration: $TORRC_PATH"
    
    # Check if SOCKS port is already configured
    if grep -q "^SOCKSPort 9050" "$TORRC_PATH" 2>/dev/null; then
        print_success "SOCKS port already configured"
    else
        print_info "Adding SOCKS port configuration..."
        echo "" | sudo tee -a "$TORRC_PATH" > /dev/null
        echo "# OSINT Lab Configuration" | sudo tee -a "$TORRC_PATH" > /dev/null
        echo "SOCKSPort 9050" | sudo tee -a "$TORRC_PATH" > /dev/null
        print_success "SOCKS port configured"
        
        # Restart Tor to apply changes
        print_info "Restarting Tor to apply changes..."
        case $OS in
            linux)
                sudo systemctl restart tor
                ;;
            macos)
                brew services restart tor
                ;;
        esac
        sleep 3
        print_success "Tor restarted"
    fi
else
    print_warning "Tor configuration file not found"
    print_info "Tor should still work with default settings"
fi

# Update app.py to enable Tor
print_info "Checking OSINT Lab configuration..."

if [ -f "app.py" ]; then
    if grep -q "use_tor=False" app.py; then
        print_info "Updating app.py to enable Tor..."
        
        # Create backup
        cp app.py app.py.backup
        print_info "Created backup: app.py.backup"
        
        # Update configuration
        sed -i.tmp 's/use_tor=False/use_tor=True/g' app.py
        rm -f app.py.tmp
        
        print_success "app.py updated to use Tor"
    elif grep -q "use_tor=True" app.py; then
        print_success "app.py is already configured to use Tor"
    else
        print_warning "Could not find use_tor configuration in app.py"
        print_info "Please manually set: shadow_tracker = ShadowTracker(use_tor=True)"
    fi
else
    print_warning "app.py not found in current directory"
    print_info "Make sure to set: shadow_tracker = ShadowTracker(use_tor=True)"
fi

echo ""
echo "========================================"
echo "  ✓ Tor Installation Complete!"
echo "========================================"
echo ""

print_success "Tor is installed and running"
print_info "Tor SOCKS proxy: 127.0.0.1:9050"
echo ""

print_info "Next steps:"
echo "  1. Verify Tor is working:"
echo "     curl --socks5 127.0.0.1:9050 https://check.torproject.org/"
echo ""
echo "  2. Test in Python:"
echo "     python3 -c 'from modules.shadow_tracker import TorSession; tor = TorSession(); print(\"✓ Tor works!\" if tor.verify_tor_connection() else \"✗ Tor not working\")'"
echo ""
echo "  3. Restart your OSINT Lab:"
echo "     python app.py"
echo ""

print_warning "IMPORTANT SECURITY REMINDER:"
print_warning "  • Only access public .onion sites"
print_warning "  • Do NOT access illegal marketplaces"
print_warning "  • Use for legitimate threat intelligence only"
print_warning "  • Follow your local laws"
echo ""

print_success "Happy dark web intelligence hunting! 🕵️"
echo ""

# Show Tor status
print_info "Current Tor status:"
case $OS in
    linux)
        sudo systemctl status tor --no-pager | head -n 5
        ;;
    macos)
        brew services list | grep tor
        ;;
esac

echo ""
