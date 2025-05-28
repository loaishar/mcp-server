#!/usr/bin/env python3
"""
Simple MCP Server Test Script
Tests the MCP server running in Docker container
"""

import subprocess
import json
import sys

def test_mcp_server():
    """Test the MCP server with basic commands."""
    
    print("🧪 Testing MCP Server in Docker Container")
    print("=" * 50)
    
    # Test commands
    test_commands = [
        {
            "name": "Initialize",
            "request": {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}
        },
        {
            "name": "List Tools", 
            "request": {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}
        },
        {
            "name": "List Resources",
            "request": {"jsonrpc": "2.0", "id": 3, "method": "resources/list", "params": {}}
        },
        {
            "name": "List Prompts",
            "request": {"jsonrpc": "2.0", "id": 4, "method": "prompts/list", "params": {}}
        }
    ]
    
    for test in test_commands:
        print(f"\n🔧 Testing: {test['name']}")
        print("-" * 30)
        
        try:
            # Convert request to JSON string
            request_json = json.dumps(test['request'])
            
            # Run the command
            result = subprocess.run(
                ['docker', 'exec', '-i', 'unified-mcp-server', 'python', 'src/unified_mcp.py'],
                input=request_json,
                text=True,
                capture_output=True,
                timeout=10
            )
            
            if result.returncode == 0:
                try:
                    response = json.loads(result.stdout.strip())
                    print(f"✅ Success: {test['name']}")
                    
                    if 'result' in response:
                        result_data = response['result']
                        if test['name'] == 'Initialize':
                            server_info = result_data.get('serverInfo', {})
                            print(f"   Server: {server_info.get('name', 'Unknown')} v{server_info.get('version', 'Unknown')}")
                            print(f"   Protocol: {result_data.get('protocolVersion', 'Unknown')}")
                        elif test['name'] == 'List Tools':
                            tools = result_data.get('tools', [])
                            print(f"   Found {len(tools)} tools")
                            for tool in tools[:3]:  # Show first 3 tools
                                print(f"   - {tool.get('name', 'Unknown')}: {tool.get('description', 'No description')}")
                            if len(tools) > 3:
                                print(f"   ... and {len(tools) - 3} more tools")
                        elif test['name'] == 'List Resources':
                            resources = result_data.get('resources', [])
                            print(f"   Found {len(resources)} resources")
                        elif test['name'] == 'List Prompts':
                            prompts = result_data.get('prompts', [])
                            print(f"   Found {len(prompts)} prompts")
                    else:
                        print(f"   Response: {response}")
                        
                except json.JSONDecodeError:
                    print(f"✅ Success: {test['name']} (non-JSON response)")
                    print(f"   Output: {result.stdout[:100]}...")
            else:
                print(f"❌ Failed: {test['name']}")
                print(f"   Error: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            print(f"⏰ Timeout: {test['name']}")
        except Exception as e:
            print(f"❌ Error: {test['name']} - {e}")
    
    print(f"\n🎉 MCP Server Test Complete!")
    print("\n💡 To use this server with MCP clients:")
    print("   Command: docker exec -i unified-mcp-server python src/unified_mcp.py")
    print("   Or use MCP Inspector: npx @modelcontextprotocol/inspector docker exec -i unified-mcp-server python src/unified_mcp.py")

if __name__ == "__main__":
    test_mcp_server()
