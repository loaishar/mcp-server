# Migration Guide: Unified MCP Server v1 to v2

This guide helps you migrate from the original Unified MCP Server to the fully MCP-compliant v2 implementation.

## 🎯 Key Improvements in v2

### Protocol Compliance
- ✅ Full JSON-RPC 2.0 compliance with proper error codes
- ✅ Proper initialization flow with `initialized` notification support
- ✅ Complete implementation of resources and prompts (not just tools)
- ✅ Standard MCP error codes (-32700, -32600, etc.)
- ✅ Proper capability advertisement

### Architecture Improvements
- ✅ Connection pooling for proxy servers (no more subprocess per request)
- ✅ Persistent connections to MCP servers
- ✅ Concurrent request handling
- ✅ HTTP/SSE transport support for remote access
- ✅ Better error handling and lifecycle management

### New Features
- ✅ Resources support (list and read)
- ✅ Prompts support (list and get)
- ✅ Health check endpoints
- ✅ Server status monitoring
- ✅ Multiple transport options (stdio, HTTP/SSE)

## 📋 Migration Steps

### 1. Update Your Configuration

The `.mcp.json` configuration file remains compatible. No changes needed.

### 2. Update Claude Desktop Configuration

Replace the old server entry with the new one:

```json
{
  "mcpServers": {
    "unified-mcp": {
      "command": "python3",
      "args": [
        "/path/to/mcp-server/src/unified_mcp_v2.py"
      ],
      "env": {
        "SUPABASE_ACCESS_TOKEN": "your-token",
        "GITHUB_PERSONAL_ACCESS_TOKEN": "your-token",
        // ... other environment variables
      }
    }
  }
}
```

### 3. Update Docker Deployment

#### Option A: Quick Migration (Stdio only)
```bash
# Build new image
docker build -f Dockerfile.v2 -t unified-mcp-v2:latest .

# Run stdio version (for Claude Desktop)
docker run -it --rm \
  -e SUPABASE_ACCESS_TOKEN=$SUPABASE_ACCESS_TOKEN \
  -e GITHUB_TOKEN=$GITHUB_TOKEN \
  unified-mcp-v2:latest
```

#### Option B: Full Deployment (Stdio + HTTP)
```bash
# Use the new docker-compose file
docker-compose -f docker-compose.v2.yml up -d

# For HTTP mode only
docker-compose -f docker-compose.v2.yml --profile http up -d

# For development mode
docker-compose -f docker-compose.v2.yml --profile dev up -d
```

### 4. Update Client Code

If you have custom MCP clients, update them to:

1. Send `initialized` notification after receiving `initialize` response:
```python
# After receiving initialize response
await client.send_notification("initialized")
```

2. Handle new error codes properly:
```python
ERROR_CODES = {
    -32700: "Parse error",
    -32600: "Invalid Request",
    -32601: "Method not found",
    -32602: "Invalid params",
    -32603: "Internal error"
}
```

3. Use new capabilities if needed:
```python
# List resources
response = await client.send_request("resources/list")

# Read a resource
response = await client.send_request("resources/read", {
    "uri": "config://mcp-servers"
})

# List prompts
response = await client.send_request("prompts/list")

# Get a prompt
response = await client.send_request("prompts/get", {
    "name": "analyze_error",
    "arguments": {"error_message": "..."}
})
```

## 🔧 Testing Your Migration

### 1. Run Compliance Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio aiohttp

# Run compliance tests
python -m pytest tests/test_mcp_compliance.py -v
```

### 2. Test with MCP Client
```bash
# Test with the included client
python src/mcp_client.py python3 src/unified_mcp_v2.py --test
```

### 3. Verify in Claude Desktop
1. Update configuration as shown above
2. Restart Claude Desktop
3. Test tools work as expected
4. Check new features (resources, prompts)

## 🚀 New Features to Explore

### HTTP/SSE Transport
Run the server with HTTP transport for remote access:
```bash
python src/unified_mcp_v2.py --transport http --port 3333
```

Access via:
- JSON-RPC endpoint: `http://localhost:3333/rpc`
- SSE endpoint: `http://localhost:3333/sse`
- Health check: `http://localhost:3333/health`

### Built-in Tools
- `health_check`: Monitor server health
- `list_connected_servers`: See all proxy connections
- `server_capabilities`: Query specific server capabilities

### Resources
- `config://mcp-servers`: View current MCP configuration

### Prompts
- `analyze_error`: Analyze error messages

## ⚠️ Breaking Changes

1. **Tool Names**: Proxied tools now have server prefix (e.g., `playwright_navigate` → `playwright_navigate_playwright`)
2. **Error Codes**: Now uses standard JSON-RPC error codes
3. **Initialization**: Server now waits for `initialized` notification

## 🆘 Troubleshooting

### Server Won't Start
- Check Python version (3.10+ required)
- Install dependencies: `pip install aiohttp python-dotenv`
- Check `.mcp.json` exists and is valid JSON

### Tools Not Working
- Ensure `initialized` notification is sent after `initialize`
- Check server logs for connection errors
- Verify environment variables are set

### Docker Issues
- Use `docker-compose logs` to check for errors
- Ensure all required environment variables are set
- Check port 3333 is not in use (for HTTP mode)

## 📝 Rollback Plan

If you need to rollback to v1:
1. Change `unified_mcp_v2.py` back to `unified_mcp.py` in your configuration
2. Use original Dockerfile and docker-compose.yml
3. Remove any code that sends `initialized` notifications

## 🎉 Benefits After Migration

- **Better Performance**: Connection pooling reduces latency
- **More Reliable**: Proper error handling and lifecycle management
- **Future-Proof**: Full MCP compliance ensures compatibility
- **More Features**: Resources and prompts support
- **Remote Access**: HTTP/SSE transport for distributed setups
- **Better Monitoring**: Health checks and status tools

## 📚 Additional Resources

- [MCP Protocol Documentation](https://modelcontextprotocol.io/)
- [JSON-RPC 2.0 Specification](https://www.jsonrpc.org/specification)
- Test suite: `tests/test_mcp_compliance.py`
- Example client: `src/mcp_client.py`