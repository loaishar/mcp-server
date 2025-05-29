#!/usr/bin/env python3
"""
Unified MCP Protocol Server v2 - Fully MCP Compliant Implementation
Compatible with Claude Desktop and other MCP clients via JSON-RPC over stdio/HTTP.
Follows MCP best practices from https://modelcontextprotocol.io/
"""

import asyncio
import json
import sys
import os
import logging
import subprocess
from typing import Dict, List, Any, Optional, Union, Callable
from datetime import datetime
import time
from enum import Enum
from dataclasses import dataclass, field
import aiohttp
from aiohttp import web
import uuid

# Set up logging to stderr to avoid interfering with stdio
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mcp_server_v2.log'),
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger("unified-mcp-v2")

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# JSON-RPC Error Codes (MCP Standard)
class JsonRpcError(Enum):
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603
    SERVER_ERROR = -32000  # to -32099 for server-specific errors

@dataclass
class ServerConnection:
    """Manages a persistent connection to an MCP server"""
    name: str
    command: List[str]
    env: Dict[str, str] = field(default_factory=dict)
    process: Optional[asyncio.subprocess.Process] = None
    initialized: bool = False
    capabilities: Dict[str, Any] = field(default_factory=dict)
    tools: List[Dict[str, Any]] = field(default_factory=list)
    resources: List[Dict[str, Any]] = field(default_factory=list)
    prompts: List[Dict[str, Any]] = field(default_factory=list)
    request_id: int = 0
    pending_requests: Dict[int, asyncio.Future] = field(default_factory=dict)
    reader_task: Optional[asyncio.Task] = None

class TransportType(Enum):
    STDIO = "stdio"
    HTTP_SSE = "http_sse"

class MCPServerV2:
    """Fully compliant Unified MCP Server with connection pooling and multiple transports."""

    def __init__(self, transport: TransportType = TransportType.STDIO):
        self.transport = transport
        self.server_info = {
            "name": "unified-mcp-v2",
            "version": "2.0.0"
        }
        self.initialized = False
        self.client_info = {}
        self.protocol_version = None
        
        # Connection pool for proxy servers
        self.server_connections: Dict[str, ServerConnection] = {}
        
        # Aggregate capabilities
        self.tools: List[Dict[str, Any]] = []
        self.resources: List[Dict[str, Any]] = []
        self.prompts: List[Dict[str, Any]] = []
        
        # HTTP/SSE specific
        self.sse_clients: List[web.StreamResponse] = []
        
        # Load configuration
        self.load_mcp_config()

    def load_mcp_config(self):
        """Load MCP server configurations from .mcp.json"""
        try:
            with open('.mcp.json', 'r') as f:
                config = json.load(f)
            
            self.mcp_servers = config.get('mcpServers', {})
            
            # Add built-in tools
            self.tools = [
                {
                    "name": "health_check",
                    "description": "Check health of unified MCP server",
                    "inputSchema": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                },
                {
                    "name": "list_connected_servers",
                    "description": "List all connected MCP servers and their status",
                    "inputSchema": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                },
                {
                    "name": "server_capabilities",
                    "description": "Get capabilities of a specific server",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "server_name": {
                                "type": "string",
                                "description": "Name of the server to query"
                            }
                        },
                        "required": ["server_name"]
                    }
                }
            ]
            
            # Add example resources
            self.resources = [
                {
                    "uri": "config://mcp-servers",
                    "name": "MCP Server Configuration",
                    "description": "Current MCP server configuration",
                    "mimeType": "application/json"
                }
            ]
            
            # Add example prompts
            self.prompts = [
                {
                    "name": "analyze_error",
                    "description": "Analyze an error message and suggest fixes",
                    "arguments": [
                        {
                            "name": "error_message",
                            "description": "The error message to analyze",
                            "required": true
                        }
                    ]
                }
            ]
            
            logger.info(f"Loaded configuration with {len(self.mcp_servers)} servers")
            
        except Exception as e:
            logger.error(f"Failed to load MCP config: {e}")
            self.mcp_servers = {}

    async def start_server_connection(self, server_name: str, server_config: Dict[str, Any]) -> ServerConnection:
        """Start and initialize a connection to an MCP server"""
        try:
            # Skip if it's ourselves
            if server_name == "unified-mcp":
                return None
                
            conn = ServerConnection(
                name=server_name,
                command=[server_config['command']] + server_config.get('args', []),
                env={**os.environ, **server_config.get('env', {})}
            )
            
            # Start the process
            conn.process = await asyncio.create_subprocess_exec(
                *conn.command,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=conn.env
            )
            
            # Start reader task
            conn.reader_task = asyncio.create_task(self.read_server_output(conn))
            
            # Initialize the server
            conn.request_id += 1
            init_request = {
                "jsonrpc": "2.0",
                "id": conn.request_id,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {
                        "name": "unified-mcp-v2",
                        "version": "2.0.0"
                    }
                }
            }
            
            # Send initialization request
            response = await self.send_server_request(conn, init_request)
            
            if response and "result" in response:
                conn.initialized = True
                conn.capabilities = response["result"].get("capabilities", {})
                
                # Send initialized notification
                await self.send_server_notification(conn, {
                    "jsonrpc": "2.0",
                    "method": "initialized",
                    "params": {}
                })
                
                # Fetch tools, resources, and prompts
                await self.fetch_server_capabilities(conn)
                
                logger.info(f"Successfully connected to {server_name}")
                return conn
            else:
                logger.error(f"Failed to initialize {server_name}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to start server {server_name}: {e}")
            return None

    async def read_server_output(self, conn: ServerConnection):
        """Read output from a server process"""
        try:
            while conn.process and not conn.process.stdout.at_eof():
                line = await conn.process.stdout.readline()
                if not line:
                    break
                    
                try:
                    message = json.loads(line.decode())
                    
                    # Handle responses to our requests
                    if "id" in message and message["id"] in conn.pending_requests:
                        future = conn.pending_requests.pop(message["id"])
                        if not future.cancelled():
                            future.set_result(message)
                    
                    # Handle notifications from server
                    elif "method" in message and "id" not in message:
                        await self.handle_server_notification(conn, message)
                        
                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON from {conn.name}: {line}")
                    
        except Exception as e:
            logger.error(f"Error reading from {conn.name}: {e}")

    async def send_server_request(self, conn: ServerConnection, request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Send a request to a server and wait for response"""
        if not conn.process or conn.process.returncode is not None:
            return None
            
        try:
            # Create future for response
            request_id = request.get("id")
            if request_id:
                future = asyncio.Future()
                conn.pending_requests[request_id] = future
            
            # Send request
            conn.process.stdin.write((json.dumps(request) + "\n").encode())
            await conn.process.stdin.drain()
            
            # Wait for response if it's a request (not a notification)
            if request_id:
                return await asyncio.wait_for(future, timeout=30.0)
            
            return None
            
        except asyncio.TimeoutError:
            logger.error(f"Request timeout for {conn.name}")
            if request_id in conn.pending_requests:
                conn.pending_requests.pop(request_id)
            return None
        except Exception as e:
            logger.error(f"Error sending request to {conn.name}: {e}")
            return None

    async def send_server_notification(self, conn: ServerConnection, notification: Dict[str, Any]):
        """Send a notification to a server (no response expected)"""
        if not conn.process or conn.process.returncode is not None:
            return
            
        try:
            conn.process.stdin.write((json.dumps(notification) + "\n").encode())
            await conn.process.stdin.drain()
        except Exception as e:
            logger.error(f"Error sending notification to {conn.name}: {e}")

    async def handle_server_notification(self, conn: ServerConnection, notification: Dict[str, Any]):
        """Handle notifications from connected servers"""
        method = notification.get("method")
        logger.info(f"Notification from {conn.name}: {method}")

    async def fetch_server_capabilities(self, conn: ServerConnection):
        """Fetch tools, resources, and prompts from a connected server"""
        try:
            # Fetch tools
            conn.request_id += 1
            tools_response = await self.send_server_request(conn, {
                "jsonrpc": "2.0",
                "id": conn.request_id,
                "method": "tools/list",
                "params": {}
            })
            
            if tools_response and "result" in tools_response:
                tools = tools_response["result"].get("tools", [])
                # Prefix tool names with server name to avoid conflicts
                for tool in tools:
                    tool["name"] = f"{conn.name}_{tool['name']}"
                    tool["description"] = f"[{conn.name}] {tool.get('description', '')}"
                conn.tools = tools
                self.tools.extend(tools)
            
            # Fetch resources
            conn.request_id += 1
            resources_response = await self.send_server_request(conn, {
                "jsonrpc": "2.0",
                "id": conn.request_id,
                "method": "resources/list",
                "params": {}
            })
            
            if resources_response and "result" in resources_response:
                resources = resources_response["result"].get("resources", [])
                # Prefix resource URIs with server name
                for resource in resources:
                    resource["uri"] = f"{conn.name}://{resource.get('uri', '')}"
                    resource["name"] = f"[{conn.name}] {resource.get('name', '')}"
                conn.resources = resources
                self.resources.extend(resources)
            
            # Fetch prompts
            conn.request_id += 1
            prompts_response = await self.send_server_request(conn, {
                "jsonrpc": "2.0",
                "id": conn.request_id,
                "method": "prompts/list",
                "params": {}
            })
            
            if prompts_response and "result" in prompts_response:
                prompts = prompts_response["result"].get("prompts", [])
                # Prefix prompt names with server name
                for prompt in prompts:
                    prompt["name"] = f"{conn.name}_{prompt['name']}"
                    prompt["description"] = f"[{conn.name}] {prompt.get('description', '')}"
                conn.prompts = prompts
                self.prompts.extend(prompts)
                
        except Exception as e:
            logger.error(f"Error fetching capabilities from {conn.name}: {e}")

    async def initialize_proxy_servers(self):
        """Initialize connections to all configured MCP servers"""
        logger.info("Initializing proxy server connections...")
        
        tasks = []
        for server_name, server_config in self.mcp_servers.items():
            if server_name != "unified-mcp":  # Skip ourselves
                task = self.start_server_connection(server_name, server_config)
                tasks.append(task)
        
        # Start all servers concurrently
        connections = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Store successful connections
        for conn in connections:
            if isinstance(conn, ServerConnection) and conn:
                self.server_connections[conn.name] = conn
        
        logger.info(f"Connected to {len(self.server_connections)} servers")

    async def handle_initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP initialize request"""
        logger.info(f"Initialize request: {params}")
        
        self.protocol_version = params.get("protocolVersion")
        self.client_info = params.get("clientInfo", {})
        
        # Initialize proxy connections
        await self.initialize_proxy_servers()
        
        # Build aggregate capabilities
        capabilities = {
            "tools": {} if self.tools else None,
            "resources": {} if self.resources else None,
            "prompts": {} if self.prompts else None,
            "logging": {}
        }
        
        # Remove None capabilities
        capabilities = {k: v for k, v in capabilities.items() if v is not None}
        
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": capabilities,
            "serverInfo": self.server_info
        }

    async def handle_initialized(self, params: Dict[str, Any]) -> None:
        """Handle initialized notification from client"""
        logger.info("Client initialized notification received")
        self.initialized = True

    async def handle_tools_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tools/list request"""
        if not self.initialized:
            raise Exception("Server not initialized")
            
        return {"tools": self.tools}

    async def handle_tools_call(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tools/call request"""
        if not self.initialized:
            raise Exception("Server not initialized")
            
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        logger.info(f"Tool call: {tool_name} with args: {arguments}")
        
        # Handle built-in tools
        if tool_name == "health_check":
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps({
                            "status": "healthy",
                            "version": self.server_info["version"],
                            "connected_servers": len(self.server_connections),
                            "total_tools": len(self.tools),
                            "total_resources": len(self.resources),
                            "total_prompts": len(self.prompts),
                            "initialized": self.initialized,
                            "transport": self.transport.value
                        }, indent=2)
                    }
                ]
            }
        
        elif tool_name == "list_connected_servers":
            servers_info = {}
            for name, conn in self.server_connections.items():
                servers_info[name] = {
                    "connected": conn.process is not None and conn.process.returncode is None,
                    "initialized": conn.initialized,
                    "tools_count": len(conn.tools),
                    "resources_count": len(conn.resources),
                    "prompts_count": len(conn.prompts)
                }
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(servers_info, indent=2)
                    }
                ]
            }
        
        elif tool_name == "server_capabilities":
            server_name = arguments.get("server_name")
            if server_name not in self.server_connections:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Server '{server_name}' not found or not connected"
                        }
                    ]
                }
            
            conn = self.server_connections[server_name]
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps({
                            "capabilities": conn.capabilities,
                            "tools": [t["name"] for t in conn.tools],
                            "resources": [r["uri"] for r in conn.resources],
                            "prompts": [p["name"] for p in conn.prompts]
                        }, indent=2)
                    }
                ]
            }
        
        # Proxy to appropriate server
        for server_name, conn in self.server_connections.items():
            prefixed_name = f"{server_name}_{tool_name}"
            if any(tool["name"] == tool_name for tool in conn.tools):
                # Found the tool, proxy the request
                conn.request_id += 1
                response = await self.send_server_request(conn, {
                    "jsonrpc": "2.0",
                    "id": conn.request_id,
                    "method": "tools/call",
                    "params": {
                        "name": tool_name.replace(f"{server_name}_", ""),  # Remove prefix
                        "arguments": arguments
                    }
                })
                
                if response and "result" in response:
                    return response["result"]
                elif response and "error" in response:
                    raise Exception(f"Server error: {response['error'].get('message', 'Unknown error')}")
                else:
                    raise Exception(f"No response from {server_name}")
        
        raise Exception(f"Tool not found: {tool_name}")

    async def handle_resources_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle resources/list request"""
        if not self.initialized:
            raise Exception("Server not initialized")
            
        return {"resources": self.resources}

    async def handle_resources_read(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle resources/read request"""
        if not self.initialized:
            raise Exception("Server not initialized")
            
        uri = params.get("uri")
        
        # Handle built-in resources
        if uri == "config://mcp-servers":
            return {
                "contents": [
                    {
                        "uri": uri,
                        "mimeType": "application/json",
                        "text": json.dumps(self.mcp_servers, indent=2)
                    }
                ]
            }
        
        # Proxy to appropriate server
        for server_name, conn in self.server_connections.items():
            if uri.startswith(f"{server_name}://"):
                # Remove server prefix from URI
                original_uri = uri.replace(f"{server_name}://", "")
                
                conn.request_id += 1
                response = await self.send_server_request(conn, {
                    "jsonrpc": "2.0",
                    "id": conn.request_id,
                    "method": "resources/read",
                    "params": {"uri": original_uri}
                })
                
                if response and "result" in response:
                    return response["result"]
                elif response and "error" in response:
                    raise Exception(f"Server error: {response['error'].get('message', 'Unknown error')}")
                else:
                    raise Exception(f"No response from {server_name}")
        
        raise Exception(f"Resource not found: {uri}")

    async def handle_prompts_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle prompts/list request"""
        if not self.initialized:
            raise Exception("Server not initialized")
            
        return {"prompts": self.prompts}

    async def handle_prompts_get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle prompts/get request"""
        if not self.initialized:
            raise Exception("Server not initialized")
            
        name = params.get("name")
        arguments = params.get("arguments", {})
        
        # Handle built-in prompts
        if name == "analyze_error":
            error_message = arguments.get("error_message", "")
            return {
                "messages": [
                    {
                        "role": "user",
                        "content": {
                            "type": "text",
                            "text": f"Please analyze this error and suggest fixes:\n\n{error_message}"
                        }
                    }
                ]
            }
        
        # Proxy to appropriate server
        for server_name, conn in self.server_connections.items():
            if any(prompt["name"] == name for prompt in conn.prompts):
                conn.request_id += 1
                response = await self.send_server_request(conn, {
                    "jsonrpc": "2.0",
                    "id": conn.request_id,
                    "method": "prompts/get",
                    "params": {
                        "name": name.replace(f"{server_name}_", ""),  # Remove prefix
                        "arguments": arguments
                    }
                })
                
                if response and "result" in response:
                    return response["result"]
                elif response and "error" in response:
                    raise Exception(f"Server error: {response['error'].get('message', 'Unknown error')}")
                else:
                    raise Exception(f"No response from {server_name}")
        
        raise Exception(f"Prompt not found: {name}")

    async def handle_request(self, request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Handle incoming MCP request"""
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")
        
        logger.info(f"Handling request: {method}")
        
        try:
            # Route to appropriate handler
            if method == "initialize":
                result = await self.handle_initialize(params)
            elif method == "initialized":
                await self.handle_initialized(params)
                return None  # No response for notifications
            elif method == "tools/list":
                result = await self.handle_tools_list(params)
            elif method == "tools/call":
                result = await self.handle_tools_call(params)
            elif method == "resources/list":
                result = await self.handle_resources_list(params)
            elif method == "resources/read":
                result = await self.handle_resources_read(params)
            elif method == "prompts/list":
                result = await self.handle_prompts_list(params)
            elif method == "prompts/get":
                result = await self.handle_prompts_get(params)
            else:
                # Method not found
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": JsonRpcError.METHOD_NOT_FOUND.value,
                        "message": f"Method not found: {method}"
                    }
                }
            
            # Return response if it's a request (has id)
            if request_id is not None:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": result
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error handling request {method}: {e}")
            if request_id is not None:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": JsonRpcError.INTERNAL_ERROR.value,
                        "message": str(e)
                    }
                }
            return None

    async def run_stdio(self):
        """Run the MCP server in stdio mode"""
        logger.info("Starting Unified MCP Server v2 (stdio transport)")
        
        try:
            while True:
                # Read JSON-RPC request from stdin
                line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
                if not line:
                    break
                
                line = line.strip()
                if not line:
                    continue
                
                try:
                    request = json.loads(line)
                    
                    # Validate JSON-RPC request
                    if not isinstance(request, dict) or "jsonrpc" not in request:
                        error_response = {
                            "jsonrpc": "2.0",
                            "id": None,
                            "error": {
                                "code": JsonRpcError.INVALID_REQUEST.value,
                                "message": "Invalid Request"
                            }
                        }
                        print(json.dumps(error_response), flush=True)
                        continue
                    
                    response = await self.handle_request(request)
                    
                    # Send response if there is one
                    if response:
                        print(json.dumps(response), flush=True)
                    
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON: {e}")
                    error_response = {
                        "jsonrpc": "2.0",
                        "id": None,
                        "error": {
                            "code": JsonRpcError.PARSE_ERROR.value,
                            "message": "Parse error"
                        }
                    }
                    print(json.dumps(error_response), flush=True)
                    
        except KeyboardInterrupt:
            logger.info("Server stopped by user")
        except Exception as e:
            logger.error(f"Server error: {e}")
        finally:
            await self.cleanup()

    async def handle_http_request(self, request: web.Request) -> web.Response:
        """Handle HTTP POST requests for JSON-RPC"""
        try:
            data = await request.json()
            response = await self.handle_request(data)
            
            if response:
                return web.json_response(response)
            else:
                return web.Response(status=204)  # No content for notifications
                
        except json.JSONDecodeError:
            return web.json_response({
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": JsonRpcError.PARSE_ERROR.value,
                    "message": "Parse error"
                }
            }, status=400)
        except Exception as e:
            return web.json_response({
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": JsonRpcError.INTERNAL_ERROR.value,
                    "message": str(e)
                }
            }, status=500)

    async def handle_sse_connect(self, request: web.Request) -> web.StreamResponse:
        """Handle SSE connections for server-to-client messages"""
        response = web.StreamResponse()
        response.content_type = 'text/event-stream'
        response.headers['Cache-Control'] = 'no-cache'
        response.headers['X-Accel-Buffering'] = 'no'
        
        await response.prepare(request)
        
        # Send connection established event
        await response.write(b'event: connected\ndata: {"status": "connected"}\n\n')
        
        # Add to SSE clients list
        self.sse_clients.append(response)
        
        try:
            # Keep connection alive
            while True:
                await asyncio.sleep(30)
                await response.write(b': keep-alive\n\n')
        except Exception:
            pass
        finally:
            self.sse_clients.remove(response)
            
        return response

    async def broadcast_sse(self, event: str, data: Any):
        """Broadcast an event to all SSE clients"""
        message = f'event: {event}\ndata: {json.dumps(data)}\n\n'.encode()
        
        for client in self.sse_clients[:]:  # Copy list to avoid modification during iteration
            try:
                await client.write(message)
            except Exception:
                self.sse_clients.remove(client)

    async def run_http(self, host: str = "0.0.0.0", port: int = 3333):
        """Run the MCP server in HTTP/SSE mode"""
        logger.info(f"Starting Unified MCP Server v2 (HTTP/SSE transport) on {host}:{port}")
        
        app = web.Application()
        app.router.add_post('/rpc', self.handle_http_request)
        app.router.add_get('/sse', self.handle_sse_connect)
        
        # Add health check endpoint
        app.router.add_get('/health', lambda r: web.json_response({
            "status": "healthy",
            "transport": "http_sse",
            "version": self.server_info["version"]
        }))
        
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, host, port)
        
        try:
            await site.start()
            logger.info(f"HTTP server started on http://{host}:{port}")
            
            # Keep running
            await asyncio.Event().wait()
        except KeyboardInterrupt:
            logger.info("Server stopped by user")
        finally:
            await runner.cleanup()
            await self.cleanup()

    async def cleanup(self):
        """Clean up server connections"""
        logger.info("Cleaning up server connections...")
        
        # Close all server connections
        for name, conn in self.server_connections.items():
            if conn.process:
                try:
                    conn.process.terminate()
                    await asyncio.wait_for(conn.process.wait(), timeout=5.0)
                except asyncio.TimeoutError:
                    conn.process.kill()
                    await conn.process.wait()
                except Exception as e:
                    logger.error(f"Error closing {name}: {e}")
        
        self.server_connections.clear()

async def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Unified MCP Server v2")
    parser.add_argument(
        "--transport",
        choices=["stdio", "http"],
        default="stdio",
        help="Transport type (default: stdio)"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="HTTP host (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=3333,
        help="HTTP port (default: 3333)"
    )
    
    args = parser.parse_args()
    
    # Create server with specified transport
    transport = TransportType.STDIO if args.transport == "stdio" else TransportType.HTTP_SSE
    server = MCPServerV2(transport=transport)
    
    # Run server
    if transport == TransportType.STDIO:
        await server.run_stdio()
    else:
        await server.run_http(args.host, args.port)

if __name__ == "__main__":
    asyncio.run(main())