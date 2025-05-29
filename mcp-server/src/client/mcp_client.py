#!/usr/bin/env python3
"""
Simple MCP Client for Linux Users
Since Claude Desktop is not available on Linux, this client allows testing MCP servers.
Based on the MCP quickstart documentation.
"""

import asyncio
import json
import sys
import subprocess
from typing import Dict, Any, List, Optional
import argparse

class MCPClient:
    """Simple MCP client for testing servers on Linux."""

    def __init__(self, server_command: List[str]):
        self.server_command = server_command
        self.process = None
        self.request_id = 0

    async def start_server(self):
        """Start the MCP server process."""
        self.process = await asyncio.create_subprocess_exec(
            *self.server_command,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        print(f"Started MCP server: {' '.join(self.server_command)}")

    async def send_request(self, method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Send a JSON-RPC request to the server."""
        if not self.process:
            raise RuntimeError("Server not started")

        self.request_id += 1
        request = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": method,
            "params": params or {}
        }

        # Send request
        request_json = json.dumps(request) + "\n"
        self.process.stdin.write(request_json.encode())
        await self.process.stdin.drain()

        # Read response
        response_line = await self.process.stdout.readline()
        if not response_line:
            raise RuntimeError("No response from server")

        response = json.loads(response_line.decode())
        return response

    async def initialize(self) -> Dict[str, Any]:
        """Initialize the MCP server."""
        return await self.send_request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "roots": {"listChanged": True},
                "sampling": {}
            },
            "clientInfo": {
                "name": "mcp-test-client",
                "version": "1.0.0"
            }
        })

    async def list_tools(self) -> Dict[str, Any]:
        """List available tools."""
        return await self.send_request("tools/list")

    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a specific tool."""
        return await self.send_request("tools/call", {
            "name": name,
            "arguments": arguments
        })

    async def list_resources(self) -> Dict[str, Any]:
        """List available resources."""
        return await self.send_request("resources/list")

    async def list_prompts(self) -> Dict[str, Any]:
        """List available prompts."""
        return await self.send_request("prompts/list")

    async def close(self):
        """Close the server connection."""
        if self.process:
            self.process.stdin.close()
            await self.process.wait()

async def interactive_session(client: MCPClient):
    """Run an interactive session with the MCP server."""
    print("\n🚀 MCP Interactive Client")
    print("=" * 50)

    try:
        # Initialize server
        print("Initializing server...")
        init_response = await client.initialize()
        print(f"✅ Server initialized: {init_response.get('result', {}).get('serverInfo', {}).get('name', 'Unknown')}")

        # List available capabilities
        print("\n📋 Available Tools:")
        tools_response = await client.list_tools()
        tools = tools_response.get('result', {}).get('tools', [])

        if not tools:
            print("  No tools available")
        else:
            for i, tool in enumerate(tools, 1):
                print(f"  {i}. {tool.get('name', 'Unknown')} - {tool.get('description', 'No description')}")

        # Interactive loop
        print("\n💬 Interactive Mode (type 'help' for commands, 'quit' to exit)")
        while True:
            try:
                command = input("\n> ").strip()

                if command.lower() in ['quit', 'exit', 'q']:
                    break
                elif command.lower() == 'help':
                    print_help()
                elif command.lower() == 'tools':
                    await list_tools_detailed(client)
                elif command.lower() == 'resources':
                    await list_resources_detailed(client)
                elif command.lower() == 'prompts':
                    await list_prompts_detailed(client)
                elif command.startswith('call '):
                    await handle_tool_call(client, command[5:])
                else:
                    print("Unknown command. Type 'help' for available commands.")

            except KeyboardInterrupt:
                print("\nUse 'quit' to exit gracefully.")
            except Exception as e:
                print(f"Error: {e}")

    finally:
        await client.close()

def print_help():
    """Print help information."""
    print("""
Available commands:
  help      - Show this help message
  tools     - List all available tools
  resources - List all available resources
  prompts   - List all available prompts
  call <tool_name> [args] - Call a tool (interactive prompt for args)
  quit      - Exit the client

Examples:
  call get_weather
  call get_alerts state=CA
""")

async def list_tools_detailed(client: MCPClient):
    """List tools with detailed information."""
    try:
        response = await client.list_tools()
        tools = response.get('result', {}).get('tools', [])

        if not tools:
            print("No tools available")
            return

        print(f"\n📋 Available Tools ({len(tools)}):")
        for tool in tools:
            print(f"\n  🔧 {tool.get('name', 'Unknown')}")
            print(f"     Description: {tool.get('description', 'No description')}")

            # Show input schema if available
            input_schema = tool.get('inputSchema', {})
            if input_schema.get('properties'):
                print("     Parameters:")
                for param, details in input_schema['properties'].items():
                    param_type = details.get('type', 'unknown')
                    param_desc = details.get('description', 'No description')
                    required = param in input_schema.get('required', [])
                    req_marker = " (required)" if required else " (optional)"
                    print(f"       - {param} ({param_type}){req_marker}: {param_desc}")

    except Exception as e:
        print(f"Error listing tools: {e}")

async def list_resources_detailed(client: MCPClient):
    """List resources with detailed information."""
    try:
        response = await client.list_resources()
        resources = response.get('result', {}).get('resources', [])

        if not resources:
            print("No resources available")
            return

        print(f"\n📁 Available Resources ({len(resources)}):")
        for resource in resources:
            print(f"  📄 {resource.get('name', 'Unknown')}")
            print(f"     URI: {resource.get('uri', 'No URI')}")
            print(f"     Description: {resource.get('description', 'No description')}")

    except Exception as e:
        print(f"Error listing resources: {e}")

async def list_prompts_detailed(client: MCPClient):
    """List prompts with detailed information."""
    try:
        response = await client.list_prompts()
        prompts = response.get('result', {}).get('prompts', [])

        if not prompts:
            print("No prompts available")
            return

        print(f"\n💭 Available Prompts ({len(prompts)}):")
        for prompt in prompts:
            print(f"  💬 {prompt.get('name', 'Unknown')}")
            print(f"     Description: {prompt.get('description', 'No description')}")

    except Exception as e:
        print(f"Error listing prompts: {e}")

async def handle_tool_call(client: MCPClient, command: str):
    """Handle tool call command."""
    parts = command.split()
    if not parts:
        print("Please specify a tool name")
        return

    tool_name = parts[0]

    # Parse arguments (simple key=value format)
    arguments = {}
    for part in parts[1:]:
        if '=' in part:
            key, value = part.split('=', 1)
            # Try to parse as number or boolean
            if value.lower() == 'true':
                arguments[key] = True
            elif value.lower() == 'false':
                arguments[key] = False
            elif value.replace('.', '').replace('-', '').isdigit():
                arguments[key] = float(value) if '.' in value else int(value)
            else:
                arguments[key] = value

    # If no arguments provided, prompt for them
    if not arguments:
        # Get tool schema to prompt for required arguments
        tools_response = await client.list_tools()
        tools = tools_response.get('result', {}).get('tools', [])
        tool_schema = next((t for t in tools if t.get('name') == tool_name), None)

        if tool_schema and tool_schema.get('inputSchema', {}).get('properties'):
            print(f"\nTool '{tool_name}' requires parameters:")
            properties = tool_schema['inputSchema']['properties']
            required = tool_schema['inputSchema'].get('required', [])

            for param, details in properties.items():
                param_type = details.get('type', 'string')
                param_desc = details.get('description', 'No description')
                is_required = param in required

                while True:
                    prompt = f"  {param} ({param_type})" + (" [required]" if is_required else " [optional]")
                    prompt += f": {param_desc}\n  > "

                    value = input(prompt).strip()

                    if not value and is_required:
                        print("    This parameter is required!")
                        continue
                    elif not value:
                        break

                    # Type conversion
                    try:
                        if param_type == 'number':
                            arguments[param] = float(value) if '.' in value else int(value)
                        elif param_type == 'boolean':
                            arguments[param] = value.lower() in ['true', 'yes', '1', 'on']
                        else:
                            arguments[param] = value
                        break
                    except ValueError:
                        print(f"    Invalid {param_type} value!")

    try:
        print(f"\n🔧 Calling tool '{tool_name}' with arguments: {arguments}")
        response = await client.call_tool(tool_name, arguments)

        if 'error' in response:
            print(f"❌ Error: {response['error']}")
        else:
            result = response.get('result', {})
            content = result.get('content', [])

            print("✅ Tool response:")
            for item in content:
                if item.get('type') == 'text':
                    print(f"   {item.get('text', '')}")
                else:
                    print(f"   {item}")

    except Exception as e:
        print(f"❌ Error calling tool: {e}")

async def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Simple MCP Client for Linux")
    parser.add_argument('--test', action='store_true', help='Run basic tests only')
    parser.add_argument('command', nargs='+', help='MCP server command to run (e.g., docker exec -i container python script.py)')

    args = parser.parse_args()

    # Debug: print the parsed command
    print(f"Parsed command: {args.command}")
    print(f"Command parts: {len(args.command)} parts")

    client = MCPClient(args.command)

    try:
        await client.start_server()

        if args.test:
            # Run basic tests
            print("Running basic MCP server tests...")
            init_response = await client.initialize()
            print(f"✅ Initialize: {init_response.get('result', {}).get('serverInfo', {})}")

            tools_response = await client.list_tools()
            tools = tools_response.get('result', {}).get('tools', [])
            print(f"✅ Tools available: {len(tools)}")

            for tool in tools:
                print(f"   - {tool.get('name')}: {tool.get('description')}")
        else:
            # Run interactive session
            await interactive_session(client)

    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())
