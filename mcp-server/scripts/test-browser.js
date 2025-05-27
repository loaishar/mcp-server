#!/usr/bin/env node
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
