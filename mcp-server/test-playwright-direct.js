const { chromium } = require('playwright');

(async () => {
    try {
        console.log('Launching browser...');
        const browser = await chromium.launch({ 
            headless: true,
            args: ['--no-sandbox', '--disable-setuid-sandbox']
        });
        
        const page = await browser.newPage();
        console.log('Navigating to Google...');
        await page.goto('https://www.google.com');
        
        const title = await page.title();
        console.log('Page title:', title);
        
        await browser.close();
        console.log('Success!');
    } catch (error) {
        console.error('Error:', error.message);
        console.error('Full error:', error);
    }
})();