# 🛠️ Scripts Directory

This directory contains utility scripts for managing, configuring, and deploying the MCP server.

## 📁 Directory Structure

```
scripts/
├── config/          # Configuration management scripts
├── deploy/          # Deployment and build scripts  
├── setup/           # Environment setup scripts
└── README.md        # This file
```

## 📋 Script Categories

### 🔧 **Configuration Scripts** (`config/`)
- `generate-mcp-configs.py` - Generate MCP server configurations
- `manage-mcp.py` - Manage MCP server connections
- `verify-claude-config.py` - Verify Claude Desktop configuration

### 🚀 **Deployment Scripts** (`deploy/`)
- `build-docker.ps1` - PowerShell Docker build script
- `build-docker.sh` - Bash Docker build script
- `deploy-second-pc.sh` - Deploy to remote systems

### ⚙️ **Setup Scripts** (`setup/`)
- `setup-environment.py` - Complete environment setup
- `setup-claude-code.py` - Claude Code integration setup
- `quick-start.sh` - Quick start for Linux/macOS
- `quick-start-legacy.sh` - Legacy quick start script

## 🚀 Quick Start

### **Complete Environment Setup**
```bash
# Run the comprehensive setup script
python scripts/setup/setup-environment.py
```

### **Docker Build and Deploy**
```bash
# Linux/macOS
./scripts/deploy/build-docker.sh

# Windows PowerShell
.\scripts\deploy\build-docker.ps1
```

### **Configuration Management**
```bash
# Generate MCP configurations
python scripts/config/generate-mcp-configs.py

# Verify Claude Desktop config
python scripts/config/verify-claude-config.py
```

## 📝 Usage Guidelines

### **Script Execution**
1. **Always run from project root** - Scripts expect to be run from the main project directory
2. **Check prerequisites** - Most scripts will verify required dependencies
3. **Review output** - Scripts provide detailed logging and status information

### **Environment Variables**
Many scripts support environment variables for configuration:
- `REGISTRY` - Docker registry prefix
- `TAG` - Image tag for builds
- `PLATFORMS` - Target platforms for multi-arch builds
- `PUSH` - Whether to push to registry

### **Error Handling**
- Scripts include comprehensive error handling
- Check exit codes for automation
- Review logs for troubleshooting

## 🔍 Script Details

### **Configuration Scripts**

#### `generate-mcp-configs.py`
Generates standardized MCP server configurations for different environments.

**Usage:**
```bash
python scripts/config/generate-mcp-configs.py [--environment dev|prod]
```

#### `manage-mcp.py`
Interactive tool for managing MCP server connections and configurations.

**Usage:**
```bash
python scripts/config/manage-mcp.py
```

#### `verify-claude-config.py`
Validates Claude Desktop configuration files and checks connectivity.

**Usage:**
```bash
python scripts/config/verify-claude-config.py
```

### **Deployment Scripts**

#### `build-docker.ps1` / `build-docker.sh`
Multi-platform Docker build scripts with registry support.

**Features:**
- Multi-architecture builds (AMD64, ARM64)
- Registry push support
- Build argument customization
- Comprehensive error handling

**Usage:**
```bash
# Basic build
./scripts/deploy/build-docker.sh

# Build and push to registry
./scripts/deploy/build-docker.sh --registry myregistry.com/ --push

# Custom tag and platform
./scripts/deploy/build-docker.sh --tag v1.0.0 --platforms linux/amd64
```

#### `deploy-second-pc.sh`
Automated deployment script for remote systems.

**Usage:**
```bash
./scripts/deploy/deploy-second-pc.sh [hostname] [username]
```

### **Setup Scripts**

#### `setup-environment.py`
Comprehensive environment setup with dependency checking.

**Features:**
- Dependency verification
- Environment file creation
- Configuration validation
- Test execution

**Usage:**
```bash
python scripts/setup/setup-environment.py
```

#### `setup-claude-code.py`
Specialized setup for Claude Code integration.

**Usage:**
```bash
python scripts/setup/setup-claude-code.py
```

#### `quick-start.sh`
Rapid setup for Linux/macOS systems.

**Usage:**
```bash
./scripts/setup/quick-start.sh
```

## 🔧 Customization

### **Adding New Scripts**
1. Place in appropriate subdirectory
2. Follow naming convention: `action-target.ext`
3. Include comprehensive help and error handling
4. Update this README

### **Script Standards**
- Include shebang line for shell scripts
- Use consistent logging format
- Provide help/usage information
- Handle errors gracefully
- Support common environment variables

## 🐛 Troubleshooting

### **Common Issues**
1. **Permission denied** - Ensure scripts are executable: `chmod +x script.sh`
2. **Command not found** - Check PATH and dependencies
3. **Docker issues** - Verify Docker is running and accessible
4. **Python errors** - Check Python version and virtual environment

### **Getting Help**
- Run scripts with `--help` or `-h` flag
- Check script comments for detailed information
- Review project documentation in `docs/` directory

## 📚 Related Documentation

- [Setup Guide](../docs/guides/SETUP.md)
- [Deployment Guide](../docs/deployment/)
- [Troubleshooting Guide](../docs/guides/TROUBLESHOOTING.md)
- [Architecture Overview](../docs/architecture/ARCHITECTURE.md)
