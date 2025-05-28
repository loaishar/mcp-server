# 🐧 MCP Server Guide for Linux Users

## 🎯 Overview

Since Claude Desktop is not yet available on Linux, this guide provides comprehensive alternatives for using MCP (Model Context Protocol) servers on Linux systems. Our Docker-based implementation makes MCP development and testing seamless on Linux.

## 🚀 Quick Start for Linux

### Prerequisites
- Docker and Docker Compose
- Python 3.10+ (for local development)
- Node.js 18+ (for NPM-based MCP servers)

### 1-Minute Setup
```bash
# Clone and start
git clone https://github.com/loaishar/mcp-server.git
cd mcp-server/mcp-server

# Start Docker services
./scripts/quick-start.sh

# Test MCP servers
./scripts/test-mcp-docker.sh

# Interactive MCP client
python3 src/mcp_client.py docker exec -i unified-mcp-server python src/unified_mcp.py
```

## 🛠️ MCP Development on Linux

### Docker-Based Development (Recommended)

#### Start MCP Services
```bash
# Start all MCP servers
docker compose up -d

# Check status
docker compose ps

# View logs
docker compose logs -f unified-mcp
```

#### Test MCP Servers
```bash
# Run comprehensive tests
./scripts/test-mcp-docker.sh

# Quick health check
./scripts/test-mcp-docker.sh --quick

# Interactive testing
python3 src/mcp_client.py docker exec -i unified-mcp-server python src/unified_mcp.py
```

### Local Development

#### Setup Local Environment
```bash
# Install Python dependencies
pip install mcp httpx python-dotenv psutil

# Install Node.js MCP servers
npm install -g @playwright/mcp @modelcontextprotocol/server-git @modelcontextprotocol/server-memory

# Install Playwright browsers
npx playwright install
```

#### Run MCP Servers Locally
```bash
# Unified MCP server
python3 src/unified_mcp.py

# Playwright MCP server
npx @playwright/mcp@latest --vision

# Git MCP server
npx @modelcontextprotocol/server-git

# Memory MCP server
npx @modelcontextprotocol/server-memory
```

## 🔧 MCP Client Tools for Linux

### 1. Built-in Python MCP Client

Our custom MCP client provides full MCP protocol support:

```bash
# Interactive mode
python3 src/mcp_client.py python3 src/unified_mcp.py

# Test mode
python3 src/mcp_client.py --test python3 src/unified_mcp.py

# With Docker
python3 src/mcp_client.py docker exec -i unified-mcp-server python src/unified_mcp.py
```

**Features:**
- ✅ Interactive tool calling
- ✅ Parameter validation
- ✅ Resource and prompt listing
- ✅ Error handling and debugging
- ✅ Docker container support

### 2. MCP Inspector (Web-based)

The official MCP Inspector provides a web interface:

```bash
# Install MCP Inspector
npm install -g @modelcontextprotocol/inspector

# Launch with local server
npx @modelcontextprotocol/inspector python3 src/unified_mcp.py

# Launch with Docker server
npx @modelcontextprotocol/inspector docker exec -i unified-mcp-server python src/unified_mcp.py
```

Access at: http://localhost:5173

### 3. Command Line Testing

Direct JSON-RPC testing:

```bash
# Test server initialization
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}' | python3 src/unified_mcp.py

# List tools
echo '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}' | python3 src/unified_mcp.py

# Call a tool
echo '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"test_tool","arguments":{}}}' | python3 src/unified_mcp.py
```

## 🔌 Alternative MCP Clients

### VS Code with Continue.dev

1. **Install Continue.dev extension**
2. **Configure MCP servers** in `~/.continue/config.json`:

```json
{
  "mcpServers": {
    "unified-mcp": {
      "command": "docker",
      "args": ["exec", "-i", "unified-mcp-server", "python", "src/unified_mcp.py"]
    },
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp@latest", "--vision"]
    }
  }
}
```

### Open Interpreter

```bash
# Install Open Interpreter
pip install open-interpreter

# Use with MCP (experimental)
interpreter --mcp-server 'docker exec -i unified-mcp-server python src/unified_mcp.py'
```

### Custom MCP Clients

Build your own using our example:

```python
# See src/mcp_client.py for a complete implementation
from mcp_client import MCPClient

async def my_mcp_app():
    client = MCPClient(['python3', 'src/unified_mcp.py'])
    await client.start_server()
    await client.initialize()
    
    # Your MCP application logic here
    tools = await client.list_tools()
    result = await client.call_tool('my_tool', {'param': 'value'})
    
    await client.close()
```

## 🐳 Docker Configuration Examples

### For Different MCP Clients

#### Standard Docker Exec
```json
{
  "command": "docker",
  "args": ["exec", "-i", "unified-mcp-server", "python", "src/unified_mcp.py"]
}
```

#### Direct Container Run
```json
{
  "command": "docker",
  "args": ["run", "-i", "--rm", "--network", "mcp-network", "unified-mcp:latest"]
}
```

#### With Environment Variables
```json
{
  "command": "docker",
  "args": ["exec", "-i", "-e", "DEBUG=1", "unified-mcp-server", "python", "src/unified_mcp.py"]
}
```

## 🧪 Testing and Debugging

### Comprehensive Testing
```bash
# Run all tests
./scripts/test-mcp-docker.sh

# Test specific components
./scripts/test-mcp-docker.sh --quick    # Quick tests only
./scripts/test-mcp-docker.sh --logs     # Show logs only
```

### Manual Testing
```bash
# Test server startup
docker exec unified-mcp-server python src/unified_mcp.py &
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}' | nc localhost 3333

# Test tool functionality
python3 src/mcp_client.py --test docker exec -i unified-mcp-server python src/unified_mcp.py
```

### Debugging Tips

#### Container Issues
```bash
# Check container status
docker compose ps

# View container logs
docker compose logs unified-mcp

# Access container shell
docker exec -it unified-mcp-server bash

# Check container resources
docker stats unified-mcp-server
```

#### MCP Communication Issues
```bash
# Test STDIO communication
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}' | python3 src/unified_mcp.py

# Check for JSON-RPC compliance
python3 src/mcp_client.py --test python3 src/unified_mcp.py

# Use MCP Inspector for visual debugging
npx @modelcontextprotocol/inspector python3 src/unified_mcp.py
```

## 📊 Performance Optimization

### Container Optimization
```bash
# Use multi-stage builds
docker build --target runtime -t unified-mcp:optimized .

# Limit container resources
docker run --memory=512m --cpus=1.0 unified-mcp:latest

# Use volume caching
docker compose up -d  # Uses volume caching automatically
```

### MCP Server Optimization
```python
# In your MCP server code
import asyncio

# Use connection pooling for HTTP requests
async with httpx.AsyncClient() as client:
    # Reuse client for multiple requests
    pass

# Implement caching for expensive operations
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_operation(param):
    # Cached operation
    pass
```

## 🔄 Development Workflow

### Typical Development Cycle

1. **Start Development Environment**
   ```bash
   docker compose up -d
   ```

2. **Make Code Changes**
   ```bash
   # Edit src/unified_mcp.py or other files
   vim src/unified_mcp.py
   ```

3. **Test Changes**
   ```bash
   # Restart container to pick up changes
   docker compose restart unified-mcp
   
   # Test with client
   python3 src/mcp_client.py docker exec -i unified-mcp-server python src/unified_mcp.py
   ```

4. **Debug Issues**
   ```bash
   # Check logs
   docker compose logs unified-mcp
   
   # Use inspector
   npx @modelcontextprotocol/inspector docker exec -i unified-mcp-server python src/unified_mcp.py
   ```

5. **Deploy Changes**
   ```bash
   # Build new image
   docker compose build unified-mcp
   
   # Deploy
   docker compose up -d
   ```

## 🚀 Production Deployment on Linux

### Server Deployment
```bash
# Production compose file
cp docker-compose.yml docker-compose.prod.yml

# Configure for production
export COMPOSE_FILE=docker-compose.prod.yml
export COMPOSE_PROFILES=full

# Deploy
docker compose up -d

# Monitor
docker compose logs -f
```

### Systemd Service
```ini
# /etc/systemd/system/mcp-server.service
[Unit]
Description=MCP Server Stack
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/mcp-server
ExecStart=/usr/bin/docker compose up -d
ExecStop=/usr/bin/docker compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
```

### Monitoring and Logging
```bash
# Set up log rotation
echo '/var/lib/docker/containers/*/*-json.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0644 root root
}' > /etc/logrotate.d/docker

# Monitor with systemd
journalctl -u mcp-server -f

# Monitor containers
docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"
```

## 🤝 Contributing to Linux Support

### Areas for Contribution
- Additional MCP client implementations
- Performance optimizations
- Better debugging tools
- Integration with Linux desktop environments
- Automated testing improvements

### Development Setup
```bash
# Fork and clone
git clone https://github.com/yourusername/mcp-server.git
cd mcp-server

# Create feature branch
git checkout -b feature/linux-enhancement

# Make changes and test
./scripts/test-mcp-docker.sh

# Submit PR
git push origin feature/linux-enhancement
```

## 📚 Additional Resources

- **[MCP Official Documentation](https://modelcontextprotocol.io/)**
- **[MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)**
- **[MCP TypeScript SDK](https://github.com/modelcontextprotocol/typescript-sdk)**
- **[Docker Best Practices](https://docs.docker.com/develop/best-practices/)**
- **[Linux Container Security](https://docs.docker.com/engine/security/)**

---

**🎉 With this setup, Linux users have full access to MCP development capabilities without needing Claude Desktop!**
