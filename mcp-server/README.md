# 🚀 Professional MCP Configuration Management System

A **production-ready** Model Context Protocol (MCP) configuration management system with **Claude Desktop as the single source of truth** and automated inheritance for all other MCP clients.

## 🎯 **Overview**

This project implements a **unified MCP server architecture** that allows all AI clients (Claude Desktop, Cursor, Windsurf, VS Code Copilot) to share the same set of powerful MCP servers through a single Docker container.

### **Key Benefits**
- ✅ **Single Source of Truth**: One configuration for all AI clients
- ✅ **Docker-Based**: Consistent deployment across any PC
- ✅ **Production Ready**: Security, monitoring, and health checks
- ✅ **Team Friendly**: Easy onboarding and sharing
- ✅ **Cross-Platform**: Windows, macOS, Linux support

## 🚀 **Quick Start**

### **Prerequisites**
- **Docker Desktop** (Windows/macOS) or **Docker Engine** (Linux)
- **Git** installed
- **Python 3.10+** (for local development and Linux MCP clients)
- **Node.js 18+** (for NPM-based MCP servers)

### **1-Minute Docker Setup (Recommended)**
```bash
# 1. Clone repository
git clone https://github.com/loaishar/mcp-server.git
cd mcp-server/mcp-server

# 2. Quick start (interactive setup)
./scripts/quick-start.sh
# or on Windows: .\scripts\quick-start.ps1

# 3. Verify deployment
curl http://localhost:3333/health
```

### **Manual Docker Setup**
```bash
# 1. Configure environment
cp .env.example .env
# Edit .env with your API keys (optional)

# 2. Deploy with Docker Compose
docker compose up -d

# 3. Verify deployment
docker compose ps
curl http://localhost:3333/health
```

### **Configure AI Clients**

#### For Windows/macOS (Claude Desktop Available)
```bash
# Windows:
scripts\deploy-docker.ps1

# macOS:
scripts/deploy-docker.sh
```

#### For Linux (Claude Desktop Not Available)
```bash
# Test MCP servers
./scripts/test-mcp-docker.sh

# Interactive MCP client
python3 src/mcp_client.py docker exec -i unified-mcp-server python src/unified_mcp.py

# MCP Inspector (web-based)
npx @modelcontextprotocol/inspector docker exec -i unified-mcp-server python src/unified_mcp.py

# See full Linux guide
cat LINUX_MCP_GUIDE.md
```

### **Claude Code Integration**
Import your MCP servers from Claude Desktop to Claude Code (requires WSL/macOS):
```bash
# In WSL or macOS terminal:
claude mcp add-from-claude-desktop

# Verify import:
claude mcp list

# Add to global configuration:
claude mcp add-from-claude-desktop -s global
```

**Note**: Server names must follow pattern `^[a-zA-Z0-9_-]{1,64}$` (no spaces).

## 📦 **What's Included**

### **12 MCP Servers Available**
| Category | Server | Description |
|----------|--------|-------------|
| **Core** | `unified-mcp` | Custom server with testing, deployment, Git operations |
| | `git` | Git repository management |
| | `memory` | Persistent conversation memory |
| **Browser** | `playwright` | Browser automation with Playwright |
| | `puppeteer` | Browser automation with Puppeteer |
| | `browser-tools` | Advanced browser interaction tools |
| | `hyperbrowser` | Web browsing and scraping |
| **Services** | `github` | GitHub repository and issue management |
| | `supabase` | Database and authentication |
| | `neon` | Database operations |
| | `figma` | Design file access and manipulation |
| **AI** | `sequential-thinking` | Enhanced reasoning capabilities |

### **Supported AI Clients**
- ✅ **Claude Desktop** - Full integration (Master configuration)
- ✅ **Claude Code** - Import from Claude Desktop via CLI
- ✅ **Cursor** - Full integration
- ✅ **Windsurf** - Full integration
- ✅ **VS Code Copilot** - Configuration available
- ✅ **Docker Desktop AI (Gordon)** - Via Docker MCP Toolkit

## 📁 **Project Structure**

```
mcp-server/
├── 🐳 Core Application
│   ├── unified_mcp.py          # Main MCP server application
│   ├── requirements.txt        # Python dependencies
│   ├── Dockerfile             # Multi-stage Docker build
│   └── docker-compose.yml     # Production orchestration
│
├── ⚙️ Configuration
│   ├── .mcp.json              # Unified MCP server definitions
│   ├── config/
│   │   ├── .env.example       # Environment template
│   │   └── clients/           # AI client configuration templates
│   │       ├── claude-desktop.json
│   │       ├── cursor.json
│   │       ├── windsurf.json
│   │       └── README.md
│
├── 🛠️ Scripts
│   ├── deploy-docker.ps1      # Windows deployment script
│   ├── deploy-docker.sh       # Linux/macOS deployment script
│   └── test_comprehensive.py  # Testing suite
│
├── 📚 Documentation
│   ├── docs/
│   │   ├── docker-mcp-deployment.md
│   │   └── unified-mcp-setup.md
│   └── README.md              # This file
│
└── 🔧 Docker & Git
    ├── .dockerignore
    ├── .gitignore
    └── logs/                  # Runtime logs (gitignored)
```

## 🔧 **Management Commands**

### **Docker Operations**
| Task | Command |
|------|---------|
| **Quick start** | `./scripts/quick-start.sh` (Linux/macOS) or `.\scripts\quick-start.ps1` (Windows) |
| **Start server** | `docker compose up -d` |
| **Stop server** | `docker compose down` |
| **View logs** | `docker compose logs -f` |
| **Restart** | `docker compose restart` |
| **Update** | `docker compose pull && docker compose up -d` |
| **Health check** | `curl http://localhost:3333/health` |
| **Build images** | `./scripts/build-docker.sh` or `.\scripts\build-docker.ps1` |
| **Multi-platform build** | `PLATFORMS=linux/amd64,linux/arm64 ./scripts/build-docker.sh` |
| **Push to registry** | `REGISTRY=myregistry.com/ PUSH=true ./scripts/build-docker.sh` |

### **MCP Configuration**
| Task | Command |
|------|---------|
| **Deploy to Claude Desktop** | `python scripts/manage-mcp.py deploy` |
| **Check configuration** | `python scripts/verify-claude-config.py` |
| **Generate configs** | `python scripts/generate-mcp-configs.py` |
| **Claude Code setup** | `python scripts/setup-claude-code.py status` |
| **Import to Claude Code** | `./scripts/claude-code-import.sh` (WSL) |

## 🔗 **Access Points**

| Service | URL | Description |
|---------|-----|-------------|
| **Health Check** | http://localhost:3333/health | Server status |
| **API Docs** | http://localhost:3333/docs | Interactive API documentation |
| **OpenAPI Schema** | http://localhost:3333/openapi.json | API schema |

## 📋 **Documentation**

- **[Docker Deployment Guide](DOCKER_DEPLOYMENT.md)** - Complete Docker containerization guide
- **[Linux MCP Guide](LINUX_MCP_GUIDE.md)** - Complete guide for Linux users (Claude Desktop alternative)
- **[Legacy Docker Guide](docs/docker-mcp-deployment.md)** - Original Docker setup
- **[Unified MCP Setup](docs/unified-mcp-setup.md)** - Configuration details
- **[Claude Code Integration](docs/claude-code-integration.md)** - Import from Claude Desktop
- **[Client Configuration](config/clients/README.md)** - AI client setup
- **[Linux Examples](config/linux-mcp-examples.json)** - MCP configuration examples for Linux

## 🤝 **Contributing**

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit changes**: `git commit -m 'Add amazing feature'`
4. **Push to branch**: `git push origin feature/amazing-feature`
5. **Open Pull Request**

## 📄 **License**

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 **Support**

- **Issues**: [GitHub Issues](https://github.com/your-org/mcp-server/issues)
- **Documentation**: [docs/](docs/)
- **Health Check**: `curl http://localhost:3333/health`

---

**🎉 Ready to supercharge your AI development workflow with unified MCP servers!**
