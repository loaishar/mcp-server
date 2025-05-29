# 📁 Project Structure

This document provides a comprehensive overview of the MCP server project organization.

## 🏗️ Directory Layout

```
mcp-server/
├── 📁 config/                    # Configuration files
│   ├── 📁 clients/              # Client-specific configurations
│   │   ├── claude-desktop.json  # Claude Desktop config
│   │   ├── cursor.json          # Cursor IDE config
│   │   ├── vs-copilot.json      # VS Code Copilot config
│   │   └── windsurf.json        # Windsurf IDE config
│   ├── linux-mcp-examples.json  # Linux MCP examples
│   └── mcp-config.json          # Main MCP configuration
│
├── 📁 docker/                   # Docker containerization
│   ├── 📁 config/              # Docker-specific configs
│   ├── Dockerfile              # Main Python Dockerfile
│   ├── Dockerfile.nodejs       # Node.js Dockerfile
│   ├── docker-compose.yml      # Production compose
│   └── docker-compose.legacy.yml # Legacy compose
│
├── 📁 docs/                     # Documentation
│   ├── 📁 architecture/        # Architecture documentation
│   │   └── ARCHITECTURE.md     # System architecture
│   ├── 📁 deployment/          # Deployment guides
│   │   ├── CLAUDE_CODE_INTEGRATION.md
│   │   └── DOCKER_DEPLOYMENT.md
│   └── 📁 guides/              # User guides
│       ├── LINUX_GUIDE.md      # Linux setup guide
│       ├── MIGRATION_V2.md     # Migration guide
│       ├── PERFORMANCE_MONITORING.md
│       └── TROUBLESHOOTING.md  # Troubleshooting guide
│
├── 📁 examples/                 # Example implementations
│   ├── 📁 browser-automation/  # Browser automation examples
│   ├── 📁 custom-tools/        # Custom tool examples
│   └── README.md               # Examples documentation
│
├── 📁 logs/                     # Log files (gitignored)
│
├── 📁 scripts/                  # Utility scripts
│   ├── 📁 config/              # Configuration scripts
│   │   ├── generate-mcp-configs.py
│   │   ├── manage-mcp.py
│   │   └── verify-claude-config.py
│   ├── 📁 deploy/              # Deployment scripts
│   │   ├── build-docker.ps1    # PowerShell build script
│   │   ├── build-docker.sh     # Bash build script
│   │   └── deploy-second-pc.sh # Remote deployment
│   ├── 📁 setup/               # Setup scripts
│   │   ├── quick-start.sh      # Quick start script
│   │   ├── quick-start-legacy.sh
│   │   ├── setup-claude-code.py
│   │   └── setup-environment.py
│   └── README.md               # Scripts documentation
│
├── 📁 src/                      # Source code
│   ├── 📁 client/              # Client implementations
│   │   ├── __init__.py
│   │   └── mcp_client.py       # MCP client
│   ├── 📁 server/              # Server implementations
│   │   ├── 📁 legacy/          # Legacy server code
│   │   ├── __init__.py
│   │   └── unified_mcp_v2.py   # Main server (v2)
│   ├── 📁 utils/               # Utility modules
│   └── __init__.py
│
├── 📁 tests/                    # Test suite
│   ├── test_comprehensive.py   # Comprehensive tests
│   ├── test_mcp_compliance.py  # MCP compliance tests
│   └── test_mcp_connection.py  # Connection tests
│
├── 📄 .env.example             # Environment template
├── 📄 .gitignore               # Git ignore rules
├── 📄 FIXES_APPLIED.md         # Applied fixes log
├── 📄 PROJECT_STRUCTURE.md     # This file
├── 📄 README.md                # Main documentation
├── 📄 pytest.ini              # Pytest configuration
└── 📄 requirements.txt         # Python dependencies
```

## 📋 File Categories

### 🔧 **Configuration Files**
| File | Purpose | Location |
|------|---------|----------|
| `.env.example` | Environment variables template | Root |
| `mcp-config.json` | Main MCP server configuration | `config/` |
| `claude-desktop.json` | Claude Desktop integration | `config/clients/` |
| `docker-compose.yml` | Docker orchestration | `docker/` |
| `pytest.ini` | Test configuration | Root |

### 🐳 **Docker Files**
| File | Purpose | Description |
|------|---------|-------------|
| `Dockerfile` | Python server image | Multi-stage production build |
| `Dockerfile.nodejs` | Node.js servers image | For Node.js MCP servers |
| `docker-compose.yml` | Production deployment | Full stack deployment |
| `docker-compose.legacy.yml` | Legacy deployment | Backward compatibility |

### 📚 **Documentation**
| Directory | Content | Purpose |
|-----------|---------|---------|
| `docs/architecture/` | System design docs | Architecture overview |
| `docs/deployment/` | Deployment guides | Setup and deployment |
| `docs/guides/` | User guides | Usage instructions |

### 🛠️ **Scripts**
| Directory | Content | Purpose |
|-----------|---------|---------|
| `scripts/config/` | Configuration management | Setup and validation |
| `scripts/deploy/` | Deployment automation | Build and deploy |
| `scripts/setup/` | Environment setup | Initial setup |

### 💻 **Source Code**
| Directory | Content | Purpose |
|-----------|---------|---------|
| `src/client/` | Client implementations | MCP clients |
| `src/server/` | Server implementations | MCP servers |
| `src/utils/` | Utility modules | Shared utilities |

### 🧪 **Tests**
| File | Purpose | Coverage |
|------|---------|----------|
| `test_mcp_connection.py` | Connection testing | Basic connectivity |
| `test_mcp_compliance.py` | Protocol compliance | MCP specification |
| `test_comprehensive.py` | Full system testing | End-to-end tests |

## 🎯 Key Components

### **Main Server** (`src/server/unified_mcp_v2.py`)
- **Purpose**: Unified MCP server with multi-transport support
- **Features**: 
  - Health monitoring
  - Performance tracking
  - Automatic reconnection
  - Multi-server aggregation
- **Transports**: stdio, HTTP/SSE

### **Client** (`src/client/mcp_client.py`)
- **Purpose**: MCP client for testing and integration
- **Features**: Connection management, request handling

### **Configuration System**
- **Main Config**: `config/mcp-config.json`
- **Client Configs**: `config/clients/*.json`
- **Environment**: `.env` files

### **Docker System**
- **Multi-stage builds** for optimized images
- **Multi-platform support** (AMD64, ARM64)
- **Production-ready** configurations

## 🔄 Workflow Integration

### **Development Workflow**
1. **Setup**: Run `scripts/setup/setup-environment.py`
2. **Development**: Edit source in `src/`
3. **Testing**: Run tests in `tests/`
4. **Documentation**: Update `docs/`

### **Deployment Workflow**
1. **Build**: Use `scripts/deploy/build-docker.sh`
2. **Test**: Run comprehensive tests
3. **Deploy**: Use Docker Compose or direct deployment

### **Configuration Workflow**
1. **Generate**: Use `scripts/config/generate-mcp-configs.py`
2. **Validate**: Use `scripts/config/verify-claude-config.py`
3. **Manage**: Use `scripts/config/manage-mcp.py`

## 📏 Naming Conventions

### **Files**
- **Scripts**: `action-target.ext` (e.g., `setup-environment.py`)
- **Configs**: `service-config.json` (e.g., `claude-desktop.json`)
- **Tests**: `test_feature.py` (e.g., `test_mcp_connection.py`)
- **Docs**: `TOPIC.md` (e.g., `ARCHITECTURE.md`)

### **Directories**
- **Lowercase with hyphens**: `browser-automation`
- **Descriptive names**: `performance-monitoring`
- **Grouped by function**: `config/`, `deploy/`, `setup/`

### **Code**
- **Python**: PEP 8 compliance
- **Classes**: PascalCase (`MCPServerV2`)
- **Functions**: snake_case (`handle_request`)
- **Constants**: UPPER_CASE (`DEFAULT_PORT`)

## 🔒 Security Considerations

### **Sensitive Files**
- `.env` files (gitignored)
- API keys and tokens
- Private configuration files

### **File Permissions**
- Scripts: `755` (executable)
- Configs: `644` (read-only)
- Secrets: `600` (owner only)

## 🧹 Maintenance

### **Regular Cleanup**
- Remove `__pycache__/` directories
- Clear log files in `logs/`
- Update dependencies in `requirements.txt`

### **Version Control**
- Use `.gitignore` for generated files
- Tag releases appropriately
- Maintain clean commit history

### **Documentation Updates**
- Keep README.md current
- Update architecture docs for changes
- Maintain changelog

## 🚀 Getting Started

### **Quick Start**
```bash
# 1. Clone and setup
git clone <repository>
cd mcp-server
python scripts/setup/setup-environment.py

# 2. Run tests
python -m pytest tests/ -v

# 3. Start server
python src/server/unified_mcp_v2.py
```

### **Docker Start**
```bash
# Build and run with Docker
docker-compose -f docker/docker-compose.yml up --build
```

This structure provides a clean, maintainable, and scalable foundation for the MCP server project.
