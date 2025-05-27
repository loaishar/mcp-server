# Browser Automation Solution for MCP Servers

This document provides a complete solution for fixing browser automation issues with Playwright/Puppeteer MCP servers.

## Problem Summary

The browser automation MCP servers (Playwright, Puppeteer) are failing due to:
1. Missing system dependencies (libnss3.so and others)
2. WSL environment limitations
3. MCP server configuration issues

## Complete Solution

### Step 1: Install Dependencies

Run the setup script with sudo privileges:

```bash
sudo ./scripts/setup-browser-automation.sh
```

This script will:
- Install all required browser dependencies
- Configure the display for WSL
- Install Playwright browsers
- Verify the installation

### Step 2: Update MCP Configuration

The MCP configuration has been updated to include proper environment variables:

```bash
python3 ./scripts/fix-browser-mcp.py
```

### Step 3: Test Browser Automation

Test if browser automation is working:

```bash
node ./scripts/quick-browser-test.js
```

### Step 4: Restart Claude Code

After completing the setup:
1. Close Claude Code completely
2. Restart it to reload the MCP servers
3. Try the Playwright command again

## Alternative Solutions

### 1. Use Hyperbrowser MCP (Cloud-based)

If local browser automation continues to fail, use Hyperbrowser which runs in the cloud:

```javascript
// Example: Open Google with Hyperbrowser
mcp__hyperbrowser__browser_use_agent({
  task: "Navigate to https://www.google.com and take a screenshot"
})
```

### 2. Standalone Playwright Script

Use the created launcher script directly:

```bash
# Install Playwright first
npm install playwright

# Run the launcher
node /tmp/launch-browser-mcp.js
```

### 3. Python Selenium Alternative

Use the Selenium-based solution:

```bash
python3 /tmp/selenium-browser-launcher.py
```

## Troubleshooting

### Issue: "Cannot find shared library"

Solution:
```bash
sudo apt-get update
sudo apt-get install -y libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0
```

### Issue: "No display found" in WSL

Solution:
1. Install an X server on Windows (VcXsrv, X410, or WSLg)
2. Set DISPLAY environment variable:
   ```bash
   export DISPLAY=:0
   ```
3. Or use headless mode in your scripts

### Issue: "Permission denied"

Solution:
```bash
# Add --no-sandbox flag to browser launch options
args: ['--no-sandbox', '--disable-setuid-sandbox']
```

## Quick Test Command

After setup, test with:

```bash
# Using curl to verify connectivity
curl -I https://www.google.com

# Using the test script
node ./scripts/test-browser.js
```

## Files Created

1. `scripts/setup-browser-automation.sh` - Main setup script
2. `scripts/fix-browser-mcp.py` - MCP configuration fixer
3. `scripts/browser-automation-solution.sh` - Complete solution script
4. `scripts/quick-browser-test.js` - Quick test script
5. `scripts/test-browser.js` - Browser test script

## Next Steps

1. Run `sudo ./scripts/setup-browser-automation.sh`
2. Restart Claude Code
3. Try opening Google with Playwright MCP again

If issues persist, use Hyperbrowser MCP as an alternative cloud-based solution.