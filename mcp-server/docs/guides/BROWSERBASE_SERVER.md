# Playwright Browserbase MCP Server

## Overview

The Playwright Browserbase MCP Server provides cloud-based browser automation capabilities through Browserbase's infrastructure. This server enables LLMs to perform web automation tasks using remote browser sessions with advanced features like stealth mode, proxies, and persistent contexts.

## Core Features

### Cloud Browser Automation
- **Remote Browser Sessions**: Cloud-hosted browser instances
- **Stealth Mode**: Advanced anti-detection capabilities
- **Proxy Support**: Route traffic through Browserbase proxies
- **Persistent Contexts**: Maintain cookies and auth across sessions
- **Custom Viewport**: Configurable browser window sizes

### Session Management
- **Context Creation**: Create persistent browser contexts
- **Session Persistence**: Maintain state across multiple sessions
- **Cookie Management**: Direct cookie manipulation and injection
- **Authentication Persistence**: Keep login states across sessions

## Required Credentials

⚠️ **IMPORTANT**: This server requires Browserbase API credentials to function.

### Required Environment Variables
- `BROWSERBASE_API_KEY`: Your Browserbase API key
- `BROWSERBASE_PROJECT_ID`: Your Browserbase project ID

### Getting Credentials
1. **Sign up** at [Browserbase](https://browserbase.com)
2. **Create a project** in your Browserbase dashboard
3. **Get your API key** from the project settings
4. **Copy your project ID** from the project URL or settings

## Configuration

### Current Setup (NPX)
```json
{
  "browserbase": {
    "command": "npx",
    "args": ["-y", "@browserbasehq/mcp"],
    "env": {
      "BROWSERBASE_API_KEY": "$env:BROWSERBASE_API_KEY",
      "BROWSERBASE_PROJECT_ID": "$env:BROWSERBASE_PROJECT_ID"
    },
    "description": "Cloud-based browser automation with Browserbase"
  }
}
```

### Setting Up Environment Variables

#### Windows (PowerShell)
```powershell
$env:BROWSERBASE_API_KEY = "your_api_key_here"
$env:BROWSERBASE_PROJECT_ID = "your_project_id_here"
```

#### Windows (Command Prompt)
```cmd
set BROWSERBASE_API_KEY=your_api_key_here
set BROWSERBASE_PROJECT_ID=your_project_id_here
```

#### Linux/macOS
```bash
export BROWSERBASE_API_KEY="your_api_key_here"
export BROWSERBASE_PROJECT_ID="your_project_id_here"
```

## Available Tools

### Session Management
1. **browserbase_session_create** - Create new browser session
2. **browserbase_session_get** - Get session information
3. **browserbase_session_delete** - Delete browser session

### Context Management
4. **browserbase_context_create** - Create persistent context
5. **browserbase_context_delete** - Delete context

### Cookie Management
6. **browserbase_cookies_add** - Add cookies to session
7. **browserbase_cookies_get** - Get session cookies
8. **browserbase_cookies_delete** - Delete specific cookies

### Browser Automation
9. **browserbase_navigate** - Navigate to URL
10. **browserbase_click** - Click elements
11. **browserbase_type** - Type text into elements
12. **browserbase_screenshot** - Take screenshots
13. **browserbase_scroll** - Scroll page
14. **browserbase_wait** - Wait for elements/conditions

## Advanced Configuration Options

### With Proxies
```json
{
  "command": "npx",
  "args": ["-y", "@browserbasehq/mcp", "--proxies"],
  "env": {
    "BROWSERBASE_API_KEY": "your_api_key",
    "BROWSERBASE_PROJECT_ID": "your_project_id"
  }
}
```

### With Advanced Stealth (Scale Plan)
```json
{
  "command": "npx",
  "args": ["-y", "@browserbasehq/mcp", "--advancedStealth"],
  "env": {
    "BROWSERBASE_API_KEY": "your_api_key",
    "BROWSERBASE_PROJECT_ID": "your_project_id"
  }
}
```

### With Custom Context
```json
{
  "command": "npx",
  "args": ["-y", "@browserbasehq/mcp", "--contextId", "your_context_id"],
  "env": {
    "BROWSERBASE_API_KEY": "your_api_key",
    "BROWSERBASE_PROJECT_ID": "your_project_id"
  }
}
```

### With Custom Viewport
```json
{
  "command": "npx",
  "args": [
    "-y", "@browserbasehq/mcp",
    "--browserWidth", "1920",
    "--browserHeight", "1080"
  ],
  "env": {
    "BROWSERBASE_API_KEY": "your_api_key",
    "BROWSERBASE_PROJECT_ID": "your_project_id"
  }
}
```

## Usage Examples

### Basic Web Automation
```json
{
  "name": "browserbase_session_create",
  "arguments": {
    "projectId": "your_project_id"
  }
}
```

### Navigate and Screenshot
```json
{
  "name": "browserbase_navigate",
  "arguments": {
    "sessionId": "session_id",
    "url": "https://example.com"
  }
}
```

```json
{
  "name": "browserbase_screenshot",
  "arguments": {
    "sessionId": "session_id"
  }
}
```

### Persistent Context Usage
```json
{
  "name": "browserbase_context_create",
  "arguments": {
    "projectId": "your_project_id",
    "name": "my_persistent_context"
  }
}
```

## Key Benefits

### Cloud Infrastructure
- **No Local Setup**: No need to install browsers locally
- **Scalability**: Handle multiple concurrent sessions
- **Reliability**: Professional browser infrastructure
- **Performance**: Optimized for automation tasks

### Advanced Features
- **Stealth Mode**: Bypass bot detection
- **Proxy Support**: Geographic location flexibility
- **Context Persistence**: Maintain login states
- **Cookie Management**: Fine-grained cookie control

### Integration Benefits
- **MCP Protocol**: Standardized integration
- **Claude Integration**: Direct use in Claude Desktop
- **Flexible Configuration**: Multiple setup options
- **Professional Support**: Browserbase platform support

## Troubleshooting

### Common Issues

#### 1. Missing API Credentials
**Error**: "BROWSERBASE_API_KEY environment variable is required"
**Solution**: Set the required environment variables

#### 2. Invalid Project ID
**Error**: Project not found or access denied
**Solution**: Verify your project ID and API key permissions

#### 3. Session Limits
**Error**: Session creation failed
**Solution**: Check your Browserbase plan limits

### Verification Steps
1. **Check credentials**: Verify API key and project ID
2. **Test connection**: Try creating a simple session
3. **Check logs**: Review Browserbase dashboard for session logs
4. **Verify plan**: Ensure your plan supports required features

## Integration Status

✅ **NPX Package**: `@browserbasehq/mcp` - Available and configured
✅ **Configuration**: Added to `.mcp.json` and Claude Desktop config
✅ **Environment Setup**: Template configuration ready
⚠️ **Credentials Required**: Need Browserbase API key and project ID
✅ **Server Integration**: Loaded in unified MCP server (14 servers total)

## Next Steps

1. **Get Browserbase Account**: Sign up at browserbase.com
2. **Set Environment Variables**: Configure API credentials
3. **Test Basic Session**: Create and test a browser session
4. **Explore Features**: Try stealth mode, proxies, and contexts
5. **Integrate Workflows**: Use for web automation tasks

## Pricing Considerations

- **Free Tier**: Limited sessions for testing
- **Paid Plans**: Higher session limits and advanced features
- **Scale Plan**: Required for Advanced Stealth mode
- **Usage-Based**: Pay per session or monthly plans

## Security Notes

- **API Keys**: Keep credentials secure and private
- **Environment Variables**: Use secure environment variable management
- **Session Data**: Sessions may contain sensitive information
- **Compliance**: Ensure usage complies with target website terms
