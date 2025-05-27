#!/bin/bash

# Setup script for browser automation with Playwright/Puppeteer MCP servers
# This script installs necessary dependencies and configures the environment

echo "Browser Automation Setup Script"
echo "==============================="
echo ""

# Function to check if running in WSL
is_wsl() {
    if grep -qi microsoft /proc/version; then
        return 0
    else
        return 1
    fi
}

# Function to install Linux dependencies
install_linux_deps() {
    echo "Installing browser dependencies for Linux..."
    
    # Update package list
    sudo apt-get update
    
    # Install Chrome/Chromium dependencies
    sudo apt-get install -y \
        libnss3 \
        libnspr4 \
        libatk1.0-0 \
        libatk-bridge2.0-0 \
        libcups2 \
        libxkbcommon0 \
        libxcomposite1 \
        libxdamage1 \
        libxfixes3 \
        libxrandr2 \
        libgbm1 \
        libpango-1.0-0 \
        libcairo2 \
        libdrm2 \
        libxss1 \
        libasound2 \
        libxtst6 \
        fonts-liberation \
        xdg-utils \
        libglib2.0-0 \
        libgtk-3-0 \
        libxshmfence1
    
    # Additional dependencies for headless operation
    sudo apt-get install -y \
        libx11-xcb1 \
        libxcb-dri3-0 \
        libgl1 \
        libglu1-mesa
}

# Function to install Playwright browsers
install_playwright_browsers() {
    echo ""
    echo "Installing Playwright browsers..."
    
    # Install playwright and its browsers
    npx playwright install chromium
    npx playwright install-deps chromium
    
    echo "Playwright browser installation complete!"
}

# Function to verify installation
verify_installation() {
    echo ""
    echo "Verifying installation..."
    
    # Test Playwright
    echo "Testing Playwright..."
    node -e "
    const { chromium } = require('playwright');
    (async () => {
        try {
            const browser = await chromium.launch({ headless: true });
            await browser.close();
            console.log('✓ Playwright test successful!');
        } catch (error) {
            console.error('✗ Playwright test failed:', error.message);
        }
    })();
    " 2>/dev/null || echo "Note: Playwright test requires playwright npm package"
}

# Function to setup environment for WSL
setup_wsl_display() {
    echo ""
    echo "Setting up display for WSL..."
    
    # Check if DISPLAY is set
    if [ -z "$DISPLAY" ]; then
        echo "export DISPLAY=:0" >> ~/.bashrc
        export DISPLAY=:0
        echo "DISPLAY environment variable set to :0"
    fi
    
    # Install X11 dependencies for GUI mode
    sudo apt-get install -y x11-apps
}

# Main execution
main() {
    echo "Detecting environment..."
    
    if is_wsl; then
        echo "WSL environment detected."
        install_linux_deps
        setup_wsl_display
    else
        echo "Native Linux environment detected."
        install_linux_deps
    fi
    
    # Check if npm/npx is available
    if command -v npx &> /dev/null; then
        install_playwright_browsers
    else
        echo "Warning: npx not found. Please install Node.js and npm first."
        echo "You can install Node.js using: curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash - && sudo apt-get install -y nodejs"
    fi
    
    verify_installation
    
    echo ""
    echo "Setup complete!"
    echo ""
    echo "Next steps:"
    echo "1. Restart your terminal or run: source ~/.bashrc"
    echo "2. For GUI mode in WSL, ensure you have an X server running on Windows (e.g., VcXsrv, X410)"
    echo "3. Restart the MCP servers by running your Claude Code client"
}

# Run main function
main