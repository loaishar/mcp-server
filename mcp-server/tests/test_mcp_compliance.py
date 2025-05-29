#!/usr/bin/env python3
"""
MCP Compliance Test Suite
Tests the Unified MCP Server v2 against MCP protocol specifications
"""

import asyncio
import json
import pytest
import sys
from typing import Dict, Any

class MCPTestClient:
    """Test client for MCP protocol compliance testing"""

    def __init__(self, server_cmd: list):
        self.server_cmd = server_cmd
        self.process = None
        self.request_id = 0

    async def start(self):
        """Start the MCP server process"""
        self.process = await asyncio.create_subprocess_exec(
            *self.server_cmd,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

    async def stop(self):
        """Stop the MCP server process"""
        if self.process:
            self.process.terminate()
            await self.process.wait()

    async def send_request(self, method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Send a request and wait for response"""
        self.request_id += 1
        request = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": method,
            "params": params or {}
        }

        self.process.stdin.write((json.dumps(request) + "\n").encode())
        await self.process.stdin.drain()

        response_line = await self.process.stdout.readline()
        return json.loads(response_line.decode())

    async def send_notification(self, method: str, params: Dict[str, Any] = None):
        """Send a notification (no response expected)"""
        notification = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {}
        }

        self.process.stdin.write((json.dumps(notification) + "\n").encode())
        await self.process.stdin.drain()


@pytest.mark.asyncio
class TestMCPProtocolCompliance:
    """Test suite for MCP protocol compliance"""

    @pytest.fixture
    async def client(self):
        """Create and start test client"""
        client = MCPTestClient([sys.executable, "src/unified_mcp_v2.py"])
        await client.start()
        yield client
        await client.stop()

    async def test_json_rpc_format(self, client):
        """Test that server follows JSON-RPC 2.0 format"""
        # Test valid request
        response = await client.send_request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test", "version": "1.0"}
        })

        assert "jsonrpc" in response
        assert response["jsonrpc"] == "2.0"
        assert "id" in response
        assert "result" in response or "error" in response

    async def test_error_codes(self, client):
        """Test that server returns correct error codes"""
        # Test method not found
        response = await client.send_request("invalid_method")
        assert "error" in response
        assert response["error"]["code"] == -32601  # Method not found

        # Test invalid params (calling tool before initialization)
        response = await client.send_request("tools/call", {"name": "test"})
        assert "error" in response
        assert response["error"]["code"] == -32603  # Internal error

    async def test_initialization_flow(self, client):
        """Test proper initialization sequence"""
        # Step 1: Send initialize request
        init_response = await client.send_request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test", "version": "1.0"}
        })

        assert "result" in init_response
        result = init_response["result"]
        assert "protocolVersion" in result
        assert "capabilities" in result
        assert "serverInfo" in result

        # Step 2: Send initialized notification
        await client.send_notification("initialized")

        # Step 3: Verify server is ready for requests
        tools_response = await client.send_request("tools/list")
        assert "result" in tools_response
        assert "tools" in tools_response["result"]

    async def test_capabilities_declaration(self, client):
        """Test that server properly declares its capabilities"""
        response = await client.send_request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test", "version": "1.0"}
        })

        capabilities = response["result"]["capabilities"]

        # Server should only declare capabilities it implements
        if "tools" in capabilities:
            # Must be able to handle tools/list and tools/call
            await client.send_notification("initialized")
            tools_response = await client.send_request("tools/list")
            assert "result" in tools_response

        if "resources" in capabilities:
            # Must be able to handle resources/list and resources/read
            await client.send_notification("initialized")
            resources_response = await client.send_request("resources/list")
            assert "result" in resources_response

        if "prompts" in capabilities:
            # Must be able to handle prompts/list and prompts/get
            await client.send_notification("initialized")
            prompts_response = await client.send_request("prompts/list")
            assert "result" in prompts_response

    async def test_tools_implementation(self, client):
        """Test tools functionality"""
        # Initialize first
        await client.send_request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test", "version": "1.0"}
        })
        await client.send_notification("initialized")

        # List tools
        tools_response = await client.send_request("tools/list")
        assert "tools" in tools_response["result"]
        tools = tools_response["result"]["tools"]

        # Each tool must have required fields
        for tool in tools:
            assert "name" in tool
            assert "description" in tool
            assert "inputSchema" in tool

        # Call a built-in tool
        if any(t["name"] == "health_check" for t in tools):
            call_response = await client.send_request("tools/call", {
                "name": "health_check",
                "arguments": {}
            })
            assert "result" in call_response
            assert "content" in call_response["result"]

    async def test_resources_implementation(self, client):
        """Test resources functionality"""
        # Initialize first
        init_response = await client.send_request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test", "version": "1.0"}
        })

        # Check if resources are supported
        if "resources" not in init_response["result"]["capabilities"]:
            pytest.skip("Server doesn't support resources")

        await client.send_notification("initialized")

        # List resources
        resources_response = await client.send_request("resources/list")
        assert "resources" in resources_response["result"]
        resources = resources_response["result"]["resources"]

        # Each resource must have required fields
        for resource in resources:
            assert "uri" in resource
            assert "name" in resource

        # Read a built-in resource if available
        if any(r["uri"] == "config://mcp-servers" for r in resources):
            read_response = await client.send_request("resources/read", {
                "uri": "config://mcp-servers"
            })
            assert "result" in read_response
            assert "contents" in read_response["result"]

    async def test_prompts_implementation(self, client):
        """Test prompts functionality"""
        # Initialize first
        init_response = await client.send_request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test", "version": "1.0"}
        })

        # Check if prompts are supported
        if "prompts" not in init_response["result"]["capabilities"]:
            pytest.skip("Server doesn't support prompts")

        await client.send_notification("initialized")

        # List prompts
        prompts_response = await client.send_request("prompts/list")
        assert "prompts" in prompts_response["result"]
        prompts = prompts_response["result"]["prompts"]

        # Each prompt must have required fields
        for prompt in prompts:
            assert "name" in prompt
            assert "description" in prompt

        # Get a built-in prompt if available
        if any(p["name"] == "analyze_error" for p in prompts):
            get_response = await client.send_request("prompts/get", {
                "name": "analyze_error",
                "arguments": {"error_message": "Test error"}
            })
            assert "result" in get_response
            assert "messages" in get_response["result"]

    async def test_concurrent_requests(self, client):
        """Test that server handles concurrent requests properly"""
        # Initialize
        await client.send_request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test", "version": "1.0"}
        })
        await client.send_notification("initialized")

        # Send multiple requests without waiting
        requests = []
        for i in range(5):
            client.request_id += 1
            request = {
                "jsonrpc": "2.0",
                "id": client.request_id,
                "method": "tools/list",
                "params": {}
            }
            client.process.stdin.write((json.dumps(request) + "\n").encode())
            requests.append(client.request_id)

        await client.process.stdin.drain()

        # Collect responses
        responses = []
        for _ in requests:
            response_line = await client.process.stdout.readline()
            response = json.loads(response_line.decode())
            responses.append(response)

        # Verify all requests got responses
        response_ids = [r["id"] for r in responses if "id" in r]
        assert sorted(response_ids) == sorted(requests)

    async def test_malformed_requests(self, client):
        """Test server handles malformed requests gracefully"""
        # Send invalid JSON
        client.process.stdin.write(b"invalid json\n")
        await client.process.stdin.drain()

        response_line = await client.process.stdout.readline()
        response = json.loads(response_line.decode())

        assert "error" in response
        assert response["error"]["code"] == -32700  # Parse error

        # Send request without jsonrpc field
        invalid_request = {"method": "test", "id": 1}
        client.process.stdin.write((json.dumps(invalid_request) + "\n").encode())
        await client.process.stdin.drain()

        response_line = await client.process.stdout.readline()
        response = json.loads(response_line.decode())

        assert "error" in response
        assert response["error"]["code"] == -32600  # Invalid request


# HTTP/SSE Transport Tests
@pytest.mark.asyncio
class TestHTTPTransport:
    """Test HTTP/SSE transport compliance"""

    @pytest.fixture
    async def http_server(self):
        """Start server with HTTP transport"""
        process = await asyncio.create_subprocess_exec(
            sys.executable, "src/unified_mcp_v2.py", "--transport", "http", "--port", "8765",
            stderr=asyncio.subprocess.PIPE
        )

        # Wait for server to start
        await asyncio.sleep(2)

        yield "http://localhost:8765"

        process.terminate()
        await process.wait()

    async def test_http_health_check(self, http_server):
        """Test HTTP health endpoint"""
        import aiohttp

        async with aiohttp.ClientSession() as session:
            async with session.get(f"{http_server}/health") as response:
                assert response.status == 200
                data = await response.json()
                assert data["status"] == "healthy"
                assert data["transport"] == "http_sse"

    async def test_http_json_rpc(self, http_server):
        """Test JSON-RPC over HTTP POST"""
        import aiohttp

        async with aiohttp.ClientSession() as session:
            # Send initialize request
            request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "test", "version": "1.0"}
                }
            }

            async with session.post(f"{http_server}/rpc", json=request) as response:
                assert response.status == 200
                data = await response.json()
                assert "result" in data
                assert "protocolVersion" in data["result"]

    async def test_sse_connection(self, http_server):
        """Test SSE connection for server-sent events"""
        import aiohttp

        async with aiohttp.ClientSession() as session:
            async with session.get(f"{http_server}/sse") as response:
                assert response.status == 200
                assert response.content_type == 'text/event-stream'

                # Read first event
                data = await response.content.readline()
                assert b'event: connected' in data


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])