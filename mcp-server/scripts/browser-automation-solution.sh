#!/bin/bash

# Complete Browser Automation Solution for MCP Servers
# This script provides a full solution to setup and test browser automation

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" &> /dev/null
}

# Function to install Chromium browser
install_chromium() {
    print_status "Installing Chromium browser..."
    
    # Check if chromium is already installed
    if command_exists chromium-browser || command_exists chromium; then
        print_status "Chromium is already installed"
    else
        sudo apt-get update
        sudo apt-get install -y chromium-browser
        print_status "Chromium installed successfully"
    fi
}

# Function to create a simple browser launcher script
create_browser_launcher() {
    cat > /tmp/launch-browser-mcp.js << 'EOF'
#!/usr/bin/env node

const { chromium } = require('playwright');

async function openGoogle() {
    console.log('Launching browser to open Google...');
    
    try {
        const browser = await chromium.launch({
            headless: false, // Set to true for headless mode
            args: [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu'
            ]
        });
        
        const context = await browser.newContext();
        const page = await context.newPage();
        
        console.log('Navigating to Google...');
        await page.goto('https://www.google.com', {
            waitUntil: 'networkidle'
        });
        
        console.log('✓ Successfully opened Google!');
        console.log('✓ Browser will remain open. Close it manually when done.');
        
        // Keep the script running
        await new Promise(() => {});
        
    } catch (error) {
        console.error('Error:', error.message);
        process.exit(1);
    }
}

openGoogle();
EOF

    chmod +x /tmp/launch-browser-mcp.js
    print_status "Browser launcher script created"
}

# Function to create alternative Python solution using Selenium
create_selenium_solution() {
    cat > /tmp/selenium-browser-launcher.py << 'EOF'
#!/usr/bin/env python3
"""
Alternative browser automation solution using Selenium
"""

import sys
import time

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
except ImportError:
    print("Installing Selenium...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "selenium"])
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service

def open_google_with_selenium():
    """Open Google using Selenium WebDriver"""
    
    # Configure Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    
    # For WSL, we might need to run headless
    # chrome_options.add_argument("--headless")
    
    try:
        # Create driver
        driver = webdriver.Chrome(options=chrome_options)
        
        # Open Google
        print("Opening Google...")
        driver.get("https://www.google.com")
        
        print("✓ Successfully opened Google!")
        print("✓ Browser will remain open for 30 seconds...")
        
        # Keep browser open for 30 seconds
        time.sleep(30)
        
        # Close browser
        driver.quit()
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    open_google_with_selenium()
EOF

    chmod +x /tmp/selenium-browser-launcher.py
    print_status "Selenium solution script created"
}

# Function to test with curl (simple test)
test_with_curl() {
    print_status "Testing connectivity to Google with curl..."
    
    if curl -s -o /dev/null -w "%{http_code}" https://www.google.com | grep -q "200"; then
        print_status "Google is accessible"
    else
        print_error "Cannot reach Google"
    fi
}

# Main execution
main() {
    echo "Complete Browser Automation Solution"
    echo "===================================="
    echo ""
    
    # Check environment
    print_status "Checking environment..."
    
    # Install dependencies
    print_warning "This script needs sudo access to install dependencies"
    echo "Please enter your password when prompted:"
    
    # Install basic dependencies
    sudo apt-get update
    sudo apt-get install -y \
        curl \
        wget \
        ca-certificates \
        gnupg \
        lsb-release
    
    # Install browser dependencies
    print_status "Installing browser dependencies..."
    bash /mnt/c/Users/loai1/OneDrive/Documents/GitHub/mcp-server/mcp-server/scripts/setup-browser-automation.sh
    
    # Install Chromium
    install_chromium
    
    # Test connectivity
    test_with_curl
    
    # Create launcher scripts
    create_browser_launcher
    create_selenium_solution
    
    echo ""
    print_status "Setup complete!"
    echo ""
    echo "To open Google, you have several options:"
    echo ""
    echo "1. Using Playwright (after restarting Claude Code):"
    echo "   The MCP servers should now work properly"
    echo ""
    echo "2. Using the standalone Playwright script:"
    echo "   First install playwright: npm install playwright"
    echo "   Then run: node /tmp/launch-browser-mcp.js"
    echo ""
    echo "3. Using Selenium (Python alternative):"
    echo "   python3 /tmp/selenium-browser-launcher.py"
    echo ""
    echo "4. For headless operation in WSL, modify the scripts to use headless: true"
    echo ""
    print_warning "Remember to restart Claude Code to reload the MCP servers!"
}

# Run main function
main