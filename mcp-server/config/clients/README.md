# MCP Client Configurations

This directory contains **auto-generated** MCP server configurations for different AI development tools, all derived from the **master configuration** (`config/master-mcp-config.json`).

## 📁 Available Templates

| File | Client | Installation Path |
|------|--------|-------------------|
| `claude-desktop.json` | Claude Desktop | `%APPDATA%\Claude\claude_desktop_config.json` |
| `cursor.json` | Cursor | `%USERPROFILE%\.cursor\mcp.json` |
| `windsurf.json` | Windsurf | `%USERPROFILE%\.codeium\windsurf\mcp_config.json` |

## 🚀 Quick Setup

### Windows
```powershell
# Claude Desktop
Copy-Item "config\clients\claude-desktop.json" "$env:APPDATA\Claude\claude_desktop_config.json" -Force

# Cursor
Copy-Item "config\clients\cursor.json" "$env:USERPROFILE\.cursor\mcp.json" -Force

# Windsurf
Copy-Item "config\clients\windsurf.json" "$env:USERPROFILE\.codeium\windsurf\mcp_config.json" -Force
```

### Linux/macOS
```bash
# Claude Desktop
cp config/clients/claude-desktop.json ~/.config/Claude/claude_desktop_config.json

# Cursor
cp config/clients/cursor.json ~/.cursor/mcp.json

# Windsurf
cp config/clients/windsurf.json ~/.codeium/windsurf/mcp_config.json
```

## 🔧 How It Works

All templates use the Docker bridge approach:
```bash
docker run -i --rm alpine/socat STDIO TCP:host.docker.internal:3333
```

This connects each AI client to the unified MCP server running in Docker at port 3333.

## ✅ Prerequisites

1. **Docker running**: `docker-compose up -d`
2. **MCP server healthy**: `curl http://localhost:3333/health`
3. **Client restart**: Restart AI client after copying configuration

## 🎯 Result

All AI clients will have access to the same 12 MCP servers:
- unified-mcp, git, memory, playwright, puppeteer, browser-tools
- hyperbrowser, github, supabase, neon, figma, sequential-thinking
