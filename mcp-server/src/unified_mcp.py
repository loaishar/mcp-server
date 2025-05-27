#!/usr/bin/env python3
"""
Unified MCP Protocol Server - A proper MCP server that bridges multiple MCP servers
Compatible with Claude Desktop and other MCP clients via JSON-RPC over stdio.
"""

import asyncio
import json
import sys
import os
import logging
import subprocess
from typing import Dict, List, Any, Optional
from datetime import datetime
import time

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mcp_server.log'),
        logging.StreamHandler(sys.stderr)  # Use stderr to avoid interfering with stdio
    ]
)
logger = logging.getLogger("unified-mcp")

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not installed, continue without it
    pass

class MCPServer:
    """Unified MCP Server that bridges multiple MCP servers."""
    
    def __init__(self):
        self.server_info = {
            "name": "unified-mcp",
            "version": "2025-05-27"
        }
        self.tools = []
        self.resources = []
        self.prompts = []
        
        # Load MCP server configurations
        self.load_mcp_config()
        
    def load_mcp_config(self):
        """Load MCP server configurations from .mcp.json"""
        try:
            with open('.mcp.json', 'r') as f:
                config = json.load(f)
                
            # Extract tools from all configured MCP servers
            for server_name, server_config in config.get('mcpServers', {}).items():
                # Add basic tools for each server
                self.tools.extend([
                    {
                        "name": f"{server_name}_status",
                        "description": f"Get status of {server_name} MCP server",
                        "inputSchema": {
                            "type": "object",
                            "properties": {},
                            "required": []
                        }
                    },
                    {
                        "name": f"{server_name}_tools",
                        "description": f"List available tools from {server_name} MCP server",
                        "inputSchema": {
                            "type": "object",
                            "properties": {},
                            "required": []
                        }
                    }
                ])
                
            # Add unified tools
            self.tools.extend([
                {
                    "name": "list_all_servers",
                    "description": "List all available MCP servers",
                    "inputSchema": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                },
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
                    "name": "git_status",
                    "description": "Get git repository status",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "Repository path",
                                "default": "."
                            }
                        },
                        "required": []
                    }
                },
                {
                    "name": "run_command",
                    "description": "Run a shell command",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "command": {
                                "type": "string",
                                "description": "Command to run"
                            },
                            "cwd": {
                                "type": "string",
                                "description": "Working directory",
                                "default": "."
                            }
                        },
                        "required": ["command"]
                    }
                }
            ])
            
            logger.info(f"Loaded {len(self.tools)} tools from MCP configuration")
            
        except Exception as e:
            logger.error(f"Failed to load MCP config: {e}")
            # Add basic tools as fallback
            self.tools = [
                {
                    "name": "health_check",
                    "description": "Check health of unified MCP server",
                    "inputSchema": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            ]

    async def handle_initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP initialize request."""
        logger.info(f"Initialize request: {params}")
        
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {},
                "resources": {},
                "prompts": {},
                "logging": {}
            },
            "serverInfo": self.server_info
        }

    async def handle_tools_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tools/list request."""
        logger.info("Tools list requested")
        return {
            "tools": self.tools
        }

    async def handle_tools_call(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tools/call request."""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        logger.info(f"Tool call: {tool_name} with args: {arguments}")
        
        try:
            if tool_name == "health_check":
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps({
                                "status": "healthy",
                                "timestamp": datetime.now().isoformat(),
                                "version": self.server_info["version"],
                                "tools_count": len(self.tools)
                            }, indent=2)
                        }
                    ]
                }
                
            elif tool_name == "list_all_servers":
                try:
                    with open('.mcp.json', 'r') as f:
                        config = json.load(f)
                    servers = list(config.get('mcpServers', {}).keys())
                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps({
                                    "servers": servers,
                                    "count": len(servers)
                                }, indent=2)
                            }
                        ]
                    }
                except Exception as e:
                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": f"Error loading server list: {e}"
                            }
                        ]
                    }
                    
            elif tool_name == "git_status":
                path = arguments.get("path", ".")
                try:
                    result = subprocess.run(
                        ["git", "status", "--porcelain"],
                        capture_output=True,
                        text=True,
                        cwd=path,
                        timeout=30
                    )
                    
                    branch_result = subprocess.run(
                        ["git", "branch", "--show-current"],
                        capture_output=True,
                        text=True,
                        cwd=path,
                        timeout=30
                    )
                    
                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps({
                                    "current_branch": branch_result.stdout.strip(),
                                    "changes": result.stdout.strip().split('\n') if result.stdout.strip() else [],
                                    "clean": len(result.stdout.strip()) == 0,
                                    "path": path
                                }, indent=2)
                            }
                        ]
                    }
                except Exception as e:
                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": f"Git status error: {e}"
                            }
                        ]
                    }
                    
            elif tool_name == "run_command":
                command = arguments.get("command")
                cwd = arguments.get("cwd", ".")
                
                if not command:
                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": "Error: command parameter is required"
                            }
                        ]
                    }
                
                try:
                    result = subprocess.run(
                        command,
                        shell=True,
                        capture_output=True,
                        text=True,
                        cwd=cwd,
                        timeout=60
                    )
                    
                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps({
                                    "command": command,
                                    "cwd": cwd,
                                    "returncode": result.returncode,
                                    "stdout": result.stdout,
                                    "stderr": result.stderr,
                                    "success": result.returncode == 0
                                }, indent=2)
                            }
                        ]
                    }
                except Exception as e:
                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": f"Command execution error: {e}"
                            }
                        ]
                    }
            
            else:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Unknown tool: {tool_name}"
                        }
                    ]
                }
                
        except Exception as e:
            logger.error(f"Error in tool call {tool_name}: {e}")
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Tool execution error: {e}"
                    }
                ]
            }

    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming MCP request."""
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")
        
        logger.info(f"Handling request: {method}")
        
        try:
            if method == "initialize":
                result = await self.handle_initialize(params)
            elif method == "tools/list":
                result = await self.handle_tools_list(params)
            elif method == "tools/call":
                result = await self.handle_tools_call(params)
            else:
                raise Exception(f"Unknown method: {method}")
                
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": result
            }
            
        except Exception as e:
            logger.error(f"Error handling request {method}: {e}")
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": str(e)
                }
            }

    async def run(self):
        """Run the MCP server."""
        logger.info("Starting Unified MCP Server")
        
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
                    response = await self.handle_request(request)
                    
                    # Write response to stdout
                    print(json.dumps(response), flush=True)
                    
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON: {e}")
                    error_response = {
                        "jsonrpc": "2.0",
                        "id": None,
                        "error": {
                            "code": -32700,
                            "message": "Parse error"
                        }
                    }
                    print(json.dumps(error_response), flush=True)
                    
        except KeyboardInterrupt:
            logger.info("Server stopped by user")
        except Exception as e:
            logger.error(f"Server error: {e}")

async def main():
    """Main entry point."""
    server = MCPServer()
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())
