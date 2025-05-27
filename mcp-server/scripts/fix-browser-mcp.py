#!/usr/bin/env python3
"""
Fix Browser MCP Configuration
This script updates the MCP configuration to use proper browser automation setup
"""

import json
import os
import sys
from pathlib import Path

def update_mcp_config():
    """Update MCP configuration for browser automation"""
    
    # Path to MCP config
    config_path = Path("/mnt/c/Users/loai1/OneDrive/Documents/GitHub/mcp-server/mcp-server/.mcp.json")
    
    if not config_path.exists():
        print(f"Error: MCP config not found at {config_path}")
        return False
    
    # Read current config
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # Update playwright configuration
    config["mcpServers"]["playwright"] = {
        "command": "npx",
        "args": [
            "-y",
            "@executeautomation/playwright-mcp-server"
        ],
        "env": {
            "PLAYWRIGHT_BROWSERS_PATH": "/home/loai1/.cache/ms-playwright",
            "DISPLAY": ":0"
        },
        "description": "Browser automation with Playwright"
    }
    
    # Update playwright-vision configuration
    config["mcpServers"]["playwright-vision"] = {
        "command": "npx",
        "args": [
            "@playwright/mcp@latest",
            "--vision"
        ],
        "env": {
            "PLAYWRIGHT_BROWSERS_PATH": "/home/loai1/.cache/ms-playwright",
            "DISPLAY": ":0"
        },
        "description": "Browser automation with Playwright and vision capabilities"
    }
    
    # Update puppeteer configuration
    config["mcpServers"]["puppeteer"] = {
        "command": "npx",
        "args": [
            "-y",
            "@modelcontextprotocol/server-puppeteer"
        ],
        "env": {
            "PUPPETEER_SKIP_CHROMIUM_DOWNLOAD": "false",
            "PUPPETEER_EXECUTABLE_PATH": "/usr/bin/chromium-browser",
            "DISPLAY": ":0"
        },
        "description": "Browser automation with Puppeteer"
    }
    
    # Remove browser-tools as it's redundant
    if "browser-tools" in config["mcpServers"]:
        del config["mcpServers"]["browser-tools"]
    
    # Save updated config
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print("✓ MCP configuration updated successfully!")
    return True

def create_browser_test_script():
    """Create a test script for browser automation"""
    
    test_script = '''#!/usr/bin/env node
/**
 * Browser Automation Test Script
 * Tests Playwright functionality
 */

const { chromium } = require('playwright');

async function testBrowser() {
    console.log('Testing browser automation...');
    
    try {
        // Launch browser
        const browser = await chromium.launch({
            headless: true,
            args: ['--no-sandbox', '--disable-setuid-sandbox']
        });
        
        // Create page
        const page = await browser.newPage();
        
        // Navigate to Google
        await page.goto('https://www.google.com');
        
        // Take screenshot
        await page.screenshot({ path: 'google-test.png' });
        
        // Get title
        const title = await page.title();
        console.log(`✓ Successfully loaded: ${title}`);
        
        // Close browser
        await browser.close();
        
        console.log('✓ Browser test completed successfully!');
        return true;
    } catch (error) {
        console.error('✗ Browser test failed:', error.message);
        return false;
    }
}

// Run test
testBrowser();
'''
    
    test_path = Path("/mnt/c/Users/loai1/OneDrive/Documents/GitHub/mcp-server/mcp-server/scripts/test-browser.js")
    
    with open(test_path, 'w') as f:
        f.write(test_script)
    
    os.chmod(test_path, 0o755)
    print(f"✓ Test script created at: {test_path}")

def main():
    """Main function"""
    print("Browser MCP Configuration Fixer")
    print("===============================")
    print()
    
    # Update MCP config
    if not update_mcp_config():
        sys.exit(1)
    
    # Create test script
    create_browser_test_script()
    
    print()
    print("Next steps:")
    print("1. Run: ./scripts/setup-browser-automation.sh")
    print("2. Restart Claude Code to reload MCP servers")
    print("3. Try opening Google again with Playwright")
    print()
    print("Alternative: Use Hyperbrowser MCP for cloud-based browsing (no local setup required)")

if __name__ == "__main__":
    main()