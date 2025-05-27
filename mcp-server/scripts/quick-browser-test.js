#!/usr/bin/env node

// Quick test to check if we can use Playwright to open Google

const { exec } = require('child_process');

console.log('Quick Browser Test for MCP');
console.log('==========================\n');

// Check if playwright is installed
exec('npm list playwright 2>/dev/null', (error, stdout, stderr) => {
    if (error) {
        console.log('Playwright not found. Installing...');
        exec('npm install playwright', (installError, installStdout, installStderr) => {
            if (installError) {
                console.error('Failed to install Playwright:', installError.message);
                process.exit(1);
            }
            console.log('Playwright installed successfully!');
            runBrowserTest();
        });
    } else {
        console.log('Playwright is already installed.');
        runBrowserTest();
    }
});

function runBrowserTest() {
    const { chromium } = require('playwright');
    
    (async () => {
        try {
            console.log('\nLaunching browser in headless mode...');
            const browser = await chromium.launch({
                headless: true,
                args: ['--no-sandbox', '--disable-setuid-sandbox']
            });
            
            const page = await browser.newPage();
            
            console.log('Navigating to Google...');
            await page.goto('https://www.google.com');
            
            const title = await page.title();
            console.log(`✓ Page title: ${title}`);
            
            // Take a screenshot
            await page.screenshot({ path: 'google-screenshot.png' });
            console.log('✓ Screenshot saved as google-screenshot.png');
            
            await browser.close();
            console.log('\n✓ Test completed successfully!');
            console.log('\nThe browser automation is working properly.');
            console.log('You should now be able to use Playwright MCP after restarting Claude Code.');
            
        } catch (error) {
            console.error('\n✗ Test failed:', error.message);
            console.log('\nTroubleshooting steps:');
            console.log('1. Run: sudo ./scripts/setup-browser-automation.sh');
            console.log('2. Install missing dependencies manually');
            console.log('3. Try using headless: true mode');
        }
    })();
}