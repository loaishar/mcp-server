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
from typing import Dict, List, Any, Optional
from enum import Enum
from dataclasses import dataclass, field
import aiohttp
from aiohttp import web

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
    """Manages a persistent connection to an MCP server with health monitoring"""
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

    # Performance and health monitoring
    last_heartbeat: float = 0.0
    request_count: int = 0
    error_count: int = 0
    avg_response_time: float = 0.0
    connection_attempts: int = 0
    last_error: Optional[str] = None

    def is_healthy(self) -> bool:
        """Check if the connection is healthy"""
        import time
        if not self.process or self.process.returncode is not None:
            return False
        if not self.initialized:
            return False
        # Consider unhealthy if no heartbeat in last 60 seconds
        return (time.time() - self.last_heartbeat) < 60.0

    def update_stats(self, response_time: float, success: bool = True):
        """Update connection statistics"""
        import time
        self.request_count += 1
        if not success:
            self.error_count += 1

        # Update average response time (exponential moving average)
        if self.avg_response_time == 0:
            self.avg_response_time = response_time
        else:
            self.avg_response_time = 0.9 * self.avg_response_time + 0.1 * response_time

        self.last_heartbeat = time.time()

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

        # Health monitoring
        self.health_check_task: Optional[asyncio.Task] = None
        self.health_check_interval = 30.0  # seconds

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
                },
                {
                    "name": "server_statistics",
                    "description": "Get comprehensive performance statistics for all servers",
                    "inputSchema": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                },
                {
                    "name": "reconnect_server",
                    "description": "Manually reconnect to a specific server",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "server_name": {
                                "type": "string",
                                "description": "Name of the server to reconnect"
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
                            "required": True
                        }
                    ]
                }
            ]

            logger.info(f"Loaded configuration with {len(self.mcp_servers)} servers")

        except Exception as e:
            logger.error(f"Failed to load MCP config: {e}")
            self.mcp_servers = {}

    async def start_server_connection(self, server_name: str, server_config: Dict[str, Any]) -> ServerConnection:
        """Start and initialize a connection to an MCP server with enhanced error handling"""
        max_retries = 3
        retry_delay = 1.0

        for attempt in range(max_retries):
            try:
                # Skip if it's ourselves
                if server_name == "unified-mcp":
                    return None

                # Validate configuration
                command = server_config.get('command')
                if not command:
                    logger.error(f"No command specified for server {server_name}")
                    return None

                args = server_config.get('args', [])
                env = {**os.environ, **server_config.get('env', {})}

                # Expand environment variables in args
                expanded_args = []
                for arg in args:
                    if isinstance(arg, str) and arg.startswith("$env:"):
                        env_var = arg[5:]
                        expanded_value = env.get(env_var)
                        if not expanded_value:
                            logger.warning(f"Environment variable {env_var} not set for {server_name}")
                            expanded_args.append(arg)  # Keep original if not found
                        else:
                            expanded_args.append(expanded_value)
                    else:
                        expanded_args.append(str(arg))

                conn = ServerConnection(
                    name=server_name,
                    command=[command] + expanded_args,
                    env=env
                )

                logger.info(f"Starting server {server_name} (attempt {attempt + 1}/{max_retries})")
                logger.debug(f"Command: {command} {' '.join(expanded_args)}")

                # Start the process with timeout
                conn.process = await asyncio.wait_for(
                    asyncio.create_subprocess_exec(
                        *conn.command,
                        stdin=asyncio.subprocess.PIPE,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE,
                        env=conn.env
                    ),
                    timeout=10.0
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

                # Send initialization request with timeout
                response = await asyncio.wait_for(
                    self.send_server_request(conn, init_request),
                    timeout=15.0
                )

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

                    logger.info(f"Successfully connected to {server_name} with {len(conn.tools)} tools")
                    return conn
                else:
                    logger.error(f"Failed to initialize {server_name}: Invalid response")
                    if conn.process:
                        conn.process.terminate()

                    if attempt < max_retries - 1:
                        logger.info(f"Retrying connection to {server_name} in {retry_delay}s...")
                        await asyncio.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                        continue
                    return None

            except asyncio.TimeoutError:
                logger.error(f"Timeout connecting to {server_name} (attempt {attempt + 1})")
                if 'conn' in locals() and conn.process:
                    conn.process.terminate()
            except FileNotFoundError:
                logger.error(f"Command not found for {server_name}: {command}")
                return None  # Don't retry for missing commands
            except PermissionError:
                logger.error(f"Permission denied for {server_name}: {command}")
                return None  # Don't retry for permission issues
            except Exception as e:
                logger.error(f"Failed to start server {server_name} (attempt {attempt + 1}): {e}")
                if 'conn' in locals() and conn.process:
                    try:
                        conn.process.terminate()
                    except:
                        pass

            if attempt < max_retries - 1:
                logger.info(f"Retrying connection to {server_name} in {retry_delay}s...")
                await asyncio.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff

        logger.error(f"Failed to connect to {server_name} after {max_retries} attempts")
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
        """Send a request to a server and wait for response with performance monitoring"""
        if not conn.process or conn.process.returncode is not None:
            return None

        import time
        start_time = time.time()
        success = False

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
                response = await asyncio.wait_for(future, timeout=30.0)
                success = True
                return response

            success = True
            return None

        except asyncio.TimeoutError:
            logger.error(f"Request timeout for {conn.name}")
            conn.last_error = "Request timeout"
            if request_id in conn.pending_requests:
                conn.pending_requests.pop(request_id)
            return None
        except Exception as e:
            logger.error(f"Error sending request to {conn.name}: {e}")
            conn.last_error = str(e)
            return None
        finally:
            # Update performance statistics
            response_time = time.time() - start_time
            conn.update_stats(response_time, success)

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

        # Start health monitoring
        if not self.health_check_task:
            self.health_check_task = asyncio.create_task(self.health_monitor_loop())

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

    async def handle_initialized(self, _params: Dict[str, Any]) -> None:
        """Handle initialized notification from client"""
        logger.info("Client initialized notification received")
        self.initialized = True

    async def handle_tools_list(self, _params: Dict[str, Any]) -> Dict[str, Any]:
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

        elif tool_name == "server_statistics":
            stats = await self.get_server_stats()
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(stats, indent=2)
                    }
                ]
            }

        elif tool_name == "reconnect_server":
            server_name = arguments.get("server_name")
            if not server_name:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": "Error: server_name is required"
                        }
                    ]
                }

            if server_name not in self.mcp_servers:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Error: Server '{server_name}' not found in configuration"
                        }
                    ]
                }

            # Clean up existing connection
            if server_name in self.server_connections:
                old_conn = self.server_connections[server_name]
                if old_conn.reader_task:
                    old_conn.reader_task.cancel()
                if old_conn.process:
                    old_conn.process.terminate()

            # Attempt reconnection
            server_config = self.mcp_servers[server_name]
            new_conn = await self.start_server_connection(server_name, server_config)

            if new_conn:
                self.server_connections[server_name] = new_conn
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Successfully reconnected to {server_name}"
                        }
                    ]
                }
            else:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Failed to reconnect to {server_name}"
                        }
                    ]
                }

        # Proxy to appropriate server
        for server_name, conn in self.server_connections.items():
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

    async def handle_resources_list(self, _params: Dict[str, Any]) -> Dict[str, Any]:
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

    async def handle_prompts_list(self, _params: Dict[str, Any]) -> Dict[str, Any]:
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
        app.router.add_get('/health', lambda _r: web.json_response({
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

    async def health_monitor_loop(self):
        """Monitor health of connected servers and attempt reconnection"""
        while True:
            try:
                await asyncio.sleep(self.health_check_interval)

                unhealthy_servers = []
                for name, conn in self.server_connections.items():
                    if not conn.is_healthy():
                        logger.warning(f"Server {name} is unhealthy: {conn.last_error}")
                        unhealthy_servers.append(name)

                # Attempt to reconnect unhealthy servers
                for server_name in unhealthy_servers:
                    logger.info(f"Attempting to reconnect to {server_name}")
                    old_conn = self.server_connections[server_name]

                    # Clean up old connection
                    if old_conn.reader_task:
                        old_conn.reader_task.cancel()
                    if old_conn.process:
                        old_conn.process.terminate()

                    # Attempt reconnection
                    server_config = self.mcp_servers.get(server_name)
                    if server_config:
                        new_conn = await self.start_server_connection(server_name, server_config)
                        if new_conn:
                            self.server_connections[server_name] = new_conn
                            logger.info(f"Successfully reconnected to {server_name}")
                        else:
                            logger.error(f"Failed to reconnect to {server_name}")

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in health monitor: {e}")

    async def get_server_stats(self) -> Dict[str, Any]:
        """Get comprehensive server statistics"""
        stats = {
            "unified_server": {
                "version": self.server_info["version"],
                "initialized": self.initialized,
                "transport": self.transport.value,
                "total_tools": len(self.tools),
                "total_resources": len(self.resources),
                "total_prompts": len(self.prompts)
            },
            "connected_servers": {},
            "summary": {
                "total_servers": len(self.server_connections),
                "healthy_servers": 0,
                "unhealthy_servers": 0,
                "total_requests": 0,
                "total_errors": 0
            }
        }

        for name, conn in self.server_connections.items():
            is_healthy = conn.is_healthy()
            stats["connected_servers"][name] = {
                "healthy": is_healthy,
                "initialized": conn.initialized,
                "tools_count": len(conn.tools),
                "resources_count": len(conn.resources),
                "prompts_count": len(conn.prompts),
                "request_count": conn.request_count,
                "error_count": conn.error_count,
                "avg_response_time": round(conn.avg_response_time, 3),
                "last_error": conn.last_error,
                "connection_attempts": conn.connection_attempts
            }

            if is_healthy:
                stats["summary"]["healthy_servers"] += 1
            else:
                stats["summary"]["unhealthy_servers"] += 1

            stats["summary"]["total_requests"] += conn.request_count
            stats["summary"]["total_errors"] += conn.error_count

        return stats

    async def cleanup(self):
        """Clean up server connections"""
        logger.info("Cleaning up server connections...")

        # Stop health monitoring
        if self.health_check_task:
            self.health_check_task.cancel()
            try:
                await self.health_check_task
            except asyncio.CancelledError:
                pass

        # Close all server connections
        for name, conn in self.server_connections.items():
            if conn.reader_task:
                conn.reader_task.cancel()
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