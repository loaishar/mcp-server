# 🚀 Claude Code MCP Integration Guide

Complete guide for importing and managing MCP servers in Claude Code from your existing Claude Desktop configuration.

## 📋 **Overview**

Claude Code can import MCP servers directly from Claude Desktop using the built-in CLI, making it easy to sync your entire MCP ecosystem across both platforms.

### **Key Benefits**
- ✅ **One-Command Import**: Import all 13 MCP servers instantly
- ✅ **Automatic Sync**: Maintains consistency with Claude Desktop
- ✅ **Global Configuration**: Available across all Claude Code sessions
- ✅ **Easy Management**: Full CLI control for server management

## 🔧 **Prerequisites**

### **Platform Requirements**
- **macOS** or **Windows Subsystem for Linux (WSL)**
- Claude Code CLI installed
- Claude Desktop with configured MCP servers

### **Server Name Compatibility**
Claude Code requires server names to follow the pattern: `^[a-zA-Z0-9_-]{1,64}$`

**✅ Valid Names:**
- `unified-mcp`
- `playwright_vision`
- `sequential-thinking`

**❌ Invalid Names:**
- `sams Server` (contains space)
- `my@server` (contains special character)

## 🚀 **Import Process**

### **Step 1: Import from Claude Desktop**
```bash
# Basic import
claude mcp add-from-claude-desktop

# Import to global configuration (recommended)
claude mcp add-from-claude-desktop -s global
```

### **Step 2: Verify Import**
```bash
# List all imported servers
claude mcp list

# Get details for specific server
claude mcp get unified-mcp
```

### **Expected Output**
After successful import, you should see all 13 MCP servers:

```
unified-mcp
playwright-vision
git
memory
sequential-thinking
playwright
puppeteer
browser-tools
neon
supabase
github
figma
hyperbrowser
```

## 🔧 **Server Management**

### **View Server Details**
```bash
# Get configuration for specific server
claude mcp get supabase

# Show all server configurations
claude mcp list --verbose
```

### **Remove Servers**
```bash
# Remove specific server
claude mcp remove old-server

# Remove multiple servers
claude mcp remove server1 server2
```

### **Update Servers**
```bash
# Re-import to update configurations
claude mcp add-from-claude-desktop -s global --force
```

## 🔍 **Troubleshooting**

### **Issue: Server Names with Spaces**
If you have servers with spaces in Claude Desktop:

**Problem:**
```
Error: Server name "sams Server" is invalid
```

**Solution:**
1. Rename servers in Claude Desktop to use underscores or hyphens
2. Re-run the import command

### **Issue: Import Command Not Found**
```bash
# Check if Claude Code CLI is installed
which claude

# Install if missing (WSL/Linux)
curl -fsSL https://claude.ai/install.sh | sh
```

### **Issue: No Servers Found**
```bash
# Verify Claude Desktop configuration exists
ls "$APPDATA/Claude/claude_desktop_config.json"  # Windows
ls "~/Library/Application Support/Claude/claude_desktop_config.json"  # macOS
```

## 📊 **Configuration Comparison**

| Feature | Claude Desktop | Claude Code |
|---------|----------------|-------------|
| **Server Count** | 13 servers | 13 servers (imported) |
| **Configuration** | JSON file | CLI managed |
| **Environment Variables** | Supported | Supported |
| **Auto-sync** | Manual | Via re-import |
| **Global Access** | Per-app | Cross-session |

## 🔄 **Sync Workflow**

### **Regular Sync Process**
1. **Update Claude Desktop** configuration
2. **Re-import** to Claude Code:
   ```bash
   claude mcp add-from-claude-desktop -s global --force
   ```
3. **Verify** changes:
   ```bash
   claude mcp list
   ```

### **Automated Sync Script**
Create a sync script for regular updates:

```bash
#!/bin/bash
# sync-mcp-servers.sh

echo "🔄 Syncing MCP servers from Claude Desktop to Claude Code..."

# Import servers
claude mcp add-from-claude-desktop -s global --force

# Verify import
echo "📊 Current servers:"
claude mcp list

echo "✅ Sync complete!"
```

## 🎯 **Best Practices**

### **Naming Convention**
- Use **kebab-case** for server names: `my-server`
- Keep names **descriptive** but **concise**
- Avoid **special characters** except hyphens and underscores

### **Configuration Management**
- **Claude Desktop** as the **master** configuration
- **Regular imports** to keep Claude Code in sync
- **Test changes** in Claude Desktop before importing

### **Environment Variables**
- Ensure **environment variables** are available in both platforms
- Use **consistent naming** across environments
- **Document** required environment variables

## 📚 **Related Documentation**

- **[Claude Desktop Setup](../README.md#configure-ai-clients)** - Master configuration
- **[MCP Server Management](../scripts/manage-mcp.py)** - Configuration scripts
- **[Troubleshooting Guide](../TROUBLESHOOTING.md)** - Common issues

## 🆘 **Support**

### **Common Commands Reference**
```bash
# Import servers
claude mcp add-from-claude-desktop -s global

# List servers
claude mcp list

# Get server details
claude mcp get <server-name>

# Remove server
claude mcp remove <server-name>

# Help
claude mcp --help
```

### **Getting Help**
- **Claude Code Documentation**: [Official Docs](https://docs.anthropic.com/en/docs/claude-code)
- **MCP Protocol**: [Model Context Protocol](https://modelcontextprotocol.io/)
- **Repository Issues**: [GitHub Issues](https://github.com/your-org/mcp-server/issues)

---

**🎉 Your MCP servers are now available in both Claude Desktop and Claude Code!**
