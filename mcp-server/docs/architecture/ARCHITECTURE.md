# MCP Configuration Architecture

## 🏗️ Professional Single Source of Truth Design

This project implements a **professional-grade MCP configuration management system** where the Claude Desktop configuration serves as the **single source of truth** for all MCP clients.

## 📋 Architecture Overview

```
claude-desktop.json (MASTER - All 13 servers)
    ↓ (inherits from)
config/clients/
    ├── cursor.json (unified-mcp only)
    ├── windsurf.json (unified-mcp only)
    └── vs-copilot.json (unified-mcp only)
```

**Claude Desktop = Single Source of Truth**
- **Direct Access**: All 13 MCP servers connected directly
- **Maximum Performance**: No bridge server overhead
- **Full Functionality**: Each server operates at full capacity
- **Master Configuration**: Other clients inherit from Claude Desktop

### Key Principles

1. **Single Source of Truth**: `config/master-mcp-config.json` is the authoritative configuration
2. **Auto-Generation**: All client configs are generated from the master
3. **Client Profiles**: Each client has a customized server set based on its use case
4. **No Manual Editing**: Client configs are never edited directly
5. **Professional Workflow**: Management scripts handle all configuration changes

## 🔧 Components

### Master Configuration (`config/master-mcp-config.json`)
- **Complete server definitions** for all 13 MCP servers
- **Client profiles** defining which servers each client should use
- **Metadata** including categories, priorities, and capabilities
- **Enable/disable flags** for fine-grained control

### Generation Scripts (`scripts/`)
- **`generate-mcp-configs.py`**: Generates all client configurations from master
- **`manage-mcp.py`**: CLI tool for managing configurations
- **Auto-deployment**: Direct deployment to Claude Desktop

### Client Configurations (`config/clients/`)
- **Auto-generated** from master configuration
- **Client-specific** server selections
- **Clean format** without metadata (optimized for clients)
- **Metadata tracking** for audit and debugging

## 📊 Current Configuration

### Claude Desktop - Master Configuration (13 servers)
**Direct connections to all MCP servers:**
- **unified-mcp**: Bridge server (for other clients)
- **playwright-vision**: Browser automation with vision
- **git**: Git operations and repository management
- **memory**: Persistent memory for conversations
- **sequential-thinking**: Enhanced reasoning capabilities
- **playwright**: Browser automation with Playwright
- **puppeteer**: Browser automation with Puppeteer
- **browser-tools**: Advanced browser interaction tools
- **neon**: Neon database operations
- **supabase**: Supabase database and auth operations
- **github**: GitHub repository and issue management
- **figma**: Figma design file access and manipulation
- **hyperbrowser**: Advanced web browsing and scraping

### Other Clients - Inherit from Master (1 server each)
- **cursor**: unified-mcp only (inherits all 13 servers via bridge)
- **windsurf**: unified-mcp only (inherits all 13 servers via bridge)
- **vs-copilot**: unified-mcp only (inherits all 13 servers via bridge)

## 🚀 Management Workflow

### Adding a New MCP Server
```bash
# 1. Add to master configuration
python scripts/manage-mcp.py add-server "new-server" "npx new-mcp-server" "Description" "category"

# 2. Enable for specific clients
python scripts/manage-mcp.py add-to-client "new-server" "claude-desktop"

# 3. Regenerate and deploy
python scripts/manage-mcp.py deploy
```

### Modifying Server Assignments
```bash
# Enable/disable servers globally
python scripts/manage-mcp.py enable memory
python scripts/manage-mcp.py disable playwright

# Check current status
python scripts/manage-mcp.py status

# Regenerate all configurations
python scripts/generate-mcp-configs.py
```

### Deploying Changes
```bash
# Deploy to Claude Desktop
python scripts/manage-mcp.py deploy

# Or manually copy to other clients
cp config/clients/cursor.json ~/.cursor/mcp.json
```

## 🎯 Benefits

### For Development Teams
- **Consistency**: All team members use identical server configurations
- **Version Control**: Single file to track in git
- **Easy Onboarding**: New team members get complete setup automatically
- **Centralized Management**: One place to add/remove/modify servers

### For DevOps
- **Automated Deployment**: Scripts handle configuration distribution
- **Environment Parity**: Same configs across dev/staging/prod
- **Audit Trail**: All changes tracked in master configuration
- **Rollback Capability**: Easy to revert configuration changes

### For Maintenance
- **DRY Principle**: No duplicate server definitions
- **Single Point of Truth**: Eliminates configuration drift
- **Automated Testing**: Scripts can validate configurations
- **Documentation**: Self-documenting through metadata

## 🔍 File Structure

```
mcp-server/
├── config/
│   ├── master-mcp-config.json     # MASTER CONFIGURATION
│   └── clients/                   # Generated client configs
│       ├── claude-desktop.json
│       ├── cursor.json
│       ├── windsurf.json
│       ├── vs-copilot.json
│       └── README.md
├── scripts/
│   ├── generate-mcp-configs.py    # Configuration generator
│   └── manage-mcp.py              # Management CLI
├── unified_mcp.py                 # Unified MCP protocol server
├── .mcp.json                      # Legacy config (auto-generated)
└── docs/
    └── ARCHITECTURE.md             # This document
```

## 📝 Best Practices

### Configuration Management
1. **Always edit the master config** - never edit client configs directly
2. **Use management scripts** for all configuration changes
3. **Test changes** with `manage-mcp.py status` before deploying
4. **Backup master config** before making major changes
5. **Document changes** in commit messages

### Server Organization
1. **Use categories** to group related servers (core, browser, development, etc.)
2. **Set priorities** to control server loading order
3. **Enable/disable strategically** to avoid client overload
4. **Use unified-mcp** as the primary bridge for most servers

### Client Profiles
1. **Customize per use case** - different tools need different server sets
2. **Respect client limits** - some clients have maximum server counts
3. **Consider performance** - more servers = more resource usage
4. **Test thoroughly** after profile changes

## 🎉 Result

This architecture provides a **professional, maintainable, and scalable** MCP configuration system that:
- ✅ Eliminates configuration duplication and drift
- ✅ Provides centralized management and deployment
- ✅ Supports multiple AI development tools seamlessly
- ✅ Scales easily as new MCP servers are added
- ✅ Maintains consistency across development teams
