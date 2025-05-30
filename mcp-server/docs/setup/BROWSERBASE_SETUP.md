# Browserbase MCP Server Setup Guide

## 🚀 **Quick Setup Guide**

The Browserbase MCP Server has been added to your configuration but requires API credentials to function. Follow this guide to get it working.

## 📋 **Step 1: Get Browserbase Account**

### Sign Up
1. **Visit**: [https://browserbase.com](https://browserbase.com)
2. **Sign up** for a free account
3. **Verify** your email address
4. **Complete** the onboarding process

### Create a Project
1. **Log in** to your Browserbase dashboard
2. **Click** "Create Project" or "New Project"
3. **Enter** a project name (e.g., "MCP Automation")
4. **Select** your preferred region
5. **Click** "Create Project"

## 🔑 **Step 2: Get API Credentials**

### Get API Key
1. **Navigate** to your project dashboard
2. **Click** on "Settings" or "API Keys"
3. **Generate** a new API key
4. **Copy** the API key (keep it secure!)

### Get Project ID
1. **Check** the project URL: `https://app.browserbase.com/projects/PROJECT_ID`
2. **Or** find it in the project settings
3. **Copy** the project ID

## ⚙️ **Step 3: Set Environment Variables**

### Windows (PowerShell) - Recommended
```powershell
# Set environment variables for current session
$env:BROWSERBASE_API_KEY = "bb_your_api_key_here"
$env:BROWSERBASE_PROJECT_ID = "your_project_id_here"

# To make permanent, add to your PowerShell profile
Add-Content $PROFILE '$env:BROWSERBASE_API_KEY = "bb_your_api_key_here"'
Add-Content $PROFILE '$env:BROWSERBASE_PROJECT_ID = "your_project_id_here"'
```

### Windows (System Environment Variables)
1. **Press** `Win + R`, type `sysdm.cpl`
2. **Click** "Environment Variables"
3. **Add** new user variables:
   - Name: `BROWSERBASE_API_KEY`, Value: `bb_your_api_key_here`
   - Name: `BROWSERBASE_PROJECT_ID`, Value: `your_project_id_here`
4. **Restart** Claude Desktop

### Linux/macOS
```bash
# Add to your shell profile (~/.bashrc, ~/.zshrc, etc.)
export BROWSERBASE_API_KEY="bb_your_api_key_here"
export BROWSERBASE_PROJECT_ID="your_project_id_here"

# Reload your shell
source ~/.bashrc  # or ~/.zshrc
```

## 🧪 **Step 4: Test the Setup**

### Test Environment Variables
```powershell
# Windows PowerShell
echo $env:BROWSERBASE_API_KEY
echo $env:BROWSERBASE_PROJECT_ID
```

```bash
# Linux/macOS
echo $BROWSERBASE_API_KEY
echo $BROWSERBASE_PROJECT_ID
```

### Test MCP Server
```powershell
# This should not show the "environment variable required" error
npx -y @browserbasehq/mcp
```

## 🔧 **Step 5: Update Configuration (Optional)**

### Basic Configuration (Current)
Your current configuration is already set up:
```json
{
  "browserbase": {
    "command": "npx",
    "args": ["-y", "@browserbasehq/mcp"],
    "env": {
      "BROWSERBASE_API_KEY": "$env:BROWSERBASE_API_KEY",
      "BROWSERBASE_PROJECT_ID": "$env:BROWSERBASE_PROJECT_ID"
    }
  }
}
```

### Advanced Configuration Options

#### With Proxies
```json
{
  "browserbase": {
    "command": "npx",
    "args": ["-y", "@browserbasehq/mcp", "--proxies"],
    "env": {
      "BROWSERBASE_API_KEY": "$env:BROWSERBASE_API_KEY",
      "BROWSERBASE_PROJECT_ID": "$env:BROWSERBASE_PROJECT_ID"
    }
  }
}
```

#### With Advanced Stealth (Scale Plan Required)
```json
{
  "browserbase": {
    "command": "npx",
    "args": ["-y", "@browserbasehq/mcp", "--advancedStealth"],
    "env": {
      "BROWSERBASE_API_KEY": "$env:BROWSERBASE_API_KEY",
      "BROWSERBASE_PROJECT_ID": "$env:BROWSERBASE_PROJECT_ID"
    }
  }
}
```

#### With Custom Viewport (1920x1080)
```json
{
  "browserbase": {
    "command": "npx",
    "args": [
      "-y", "@browserbasehq/mcp",
      "--browserWidth", "1920",
      "--browserHeight", "1080"
    ],
    "env": {
      "BROWSERBASE_API_KEY": "$env:BROWSERBASE_API_KEY",
      "BROWSERBASE_PROJECT_ID": "$env:BROWSERBASE_PROJECT_ID"
    }
  }
}
```

## 🎯 **Step 6: Restart and Test**

### Restart Services
1. **Restart Claude Desktop** to load environment variables
2. **Test** by asking Claude to browse a website
3. **Verify** sessions appear in your Browserbase dashboard

### Example Test Commands
Ask Claude:
- "Can you browse to google.com and take a screenshot?"
- "Navigate to example.com and tell me what you see"
- "Create a browser session and visit wikipedia.org"

## 📊 **Browserbase Plans**

### Free Tier
- **Sessions**: Limited free sessions per month
- **Features**: Basic browser automation
- **Good for**: Testing and small projects

### Paid Plans
- **More Sessions**: Higher session limits
- **Advanced Features**: Stealth mode, proxies
- **Professional Support**: Priority support

### Scale Plan
- **Advanced Stealth**: Required for `--advancedStealth` flag
- **Enterprise Features**: Custom configurations
- **High Volume**: Unlimited sessions

## 🔍 **Troubleshooting**

### Common Issues

#### Environment Variables Not Found
**Problem**: "BROWSERBASE_API_KEY environment variable is required"
**Solutions**:
1. Verify environment variables are set correctly
2. Restart Claude Desktop after setting variables
3. Check variable names are exact (case-sensitive)

#### Invalid API Key
**Problem**: Authentication failed
**Solutions**:
1. Verify API key is correct and complete
2. Check if API key has proper permissions
3. Regenerate API key if needed

#### Project Not Found
**Problem**: Project ID not recognized
**Solutions**:
1. Verify project ID is correct
2. Check if you have access to the project
3. Ensure project is active

#### Session Creation Failed
**Problem**: Cannot create browser sessions
**Solutions**:
1. Check your Browserbase plan limits
2. Verify project has available session quota
3. Try again after a few minutes

### Getting Help
- **Browserbase Docs**: [https://docs.browserbase.com](https://docs.browserbase.com)
- **Support**: Contact Browserbase support
- **Community**: Check Browserbase Discord/forums

## ✅ **Verification Checklist**

- [ ] Browserbase account created
- [ ] Project created and configured
- [ ] API key generated and copied
- [ ] Project ID identified
- [ ] Environment variables set
- [ ] Claude Desktop restarted
- [ ] Test command successful
- [ ] Browser session visible in dashboard

## 🎉 **Success!**

Once setup is complete, you'll have:
- **Cloud browser automation** in Claude
- **Professional browser infrastructure**
- **Advanced anti-detection capabilities**
- **Persistent browser contexts**
- **Global proxy support**

Your MCP studio now has enterprise-grade browser automation capabilities!
