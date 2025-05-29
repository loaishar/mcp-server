# Unified MCP Server v2

A fully MCP-compliant server implementation that acts as a bridge to multiple MCP servers, providing a unified interface for AI assistants like Claude Desktop.

## 🚀 Features

- **Full MCP Protocol Compliance**: Implements JSON-RPC 2.0 with proper error handling
- **Multi-Server Proxy**: Connect to multiple MCP servers through a single interface
- **Connection Pooling**: Persistent connections for better performance
- **Dual Transport**: Both stdio (local) and HTTP/SSE (remote) transports
- **Complete Capabilities**: Tools, Resources, and Prompts support
- **Production Ready**: Docker support, health checks, and comprehensive testing

## 📁 Project Structure

```
mcp-server/
├── src/                     # Source code
│   ├── server/             # Server implementations
│   ├── client/             # Client implementations
│   └── utils/              # Utilities
├── config/                 # Configuration files
├── docker/                 # Docker files
├── scripts/                # Utility scripts
│   ├── setup/             # Setup scripts
│   ├── config/            # Config management
│   └── deploy/            # Deployment scripts
├── tests/                  # Test suites
├── docs/                   # Documentation
└── examples/               # Examples
```

## 🔧 Quick Start

### Option 1: Direct Python
```bash
# Install dependencies
pip install -r requirements.txt
pip install aiohttp python-dotenv

# Run the server
./scripts/setup/quick-start.sh
```

### Option 2: Docker
```bash
# Build and run with Docker Compose
docker-compose -f docker/docker-compose.yml up
```

### Option 3: Manual Setup
```bash
# Stdio mode (for Claude Desktop)
python src/server/unified_mcp_v2.py --transport stdio

# HTTP mode (for remote access)
python src/server/unified_mcp_v2.py --transport http --port 3333
```

## 🔌 Claude Desktop Configuration

Add to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "unified-mcp": {
      "command": "python3",
      "args": ["/path/to/mcp-server/src/server/unified_mcp_v2.py"],
      "env": {
        "SUPABASE_ACCESS_TOKEN": "your-token",
        "GITHUB_PERSONAL_ACCESS_TOKEN": "your-token"
      }
    }
  }
}
```

## 📚 Documentation

- [Architecture Overview](docs/architecture/ARCHITECTURE.md)
- [Getting Started Guide](docs/guides/GETTING_STARTED.md)
- [Migration from v1](docs/guides/MIGRATION_V2.md)
- [Linux Setup Guide](docs/guides/LINUX_GUIDE.md)
- [Docker Deployment](docs/deployment/DOCKER_DEPLOYMENT.md)
- [Troubleshooting](docs/guides/TROUBLESHOOTING.md)

## 🧪 Testing

Run the compliance test suite:
```bash
python -m pytest tests/test_mcp_compliance.py -v
```

## 🛠️ Supported MCP Servers

The unified server can proxy to:
- Playwright (browser automation)
- Puppeteer (browser automation)
- Supabase (database operations)
- GitHub (repository management)
- Git (version control)
- Memory (persistent storage)
- Sequential Thinking (reasoning)
- Neon (database)
- Figma (design)
- Hyperbrowser (web scraping)

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Run tests to ensure compliance
4. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details