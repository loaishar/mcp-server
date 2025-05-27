#!/usr/bin/env python3
"""
Test script to verify MCP server connection
"""

import subprocess
import json
import time
import sys

def test_mcp_server():
    """Test the MCP server connection"""
    print("🔍 Testing MCP Server Connection...")

    try:
        # Start the MCP server
        process = subprocess.Popen(
            ["python", "src/unified_mcp.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd="C:\\Users\\loai1\\mcp-server"
        )

        # Send initialize request
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test-client", "version": "1.0"}
            }
        }

        print("📤 Sending initialize request...")
        process.stdin.write(json.dumps(init_request) + "\n")
        process.stdin.flush()

        # Read response
        response_line = process.stdout.readline()
        if response_line:
            try:
                response = json.loads(response_line.strip())
                if "result" in response:
                    print("✅ Initialize successful!")
                    print(f"   Server: {response['result']['serverInfo']['name']}")
                    print(f"   Version: {response['result']['serverInfo']['version']}")

                    # Test tools/list
                    tools_request = {
                        "jsonrpc": "2.0",
                        "id": 2,
                        "method": "tools/list",
                        "params": {}
                    }

                    print("📤 Requesting tools list...")
                    process.stdin.write(json.dumps(tools_request) + "\n")
                    process.stdin.flush()

                    tools_response_line = process.stdout.readline()
                    if tools_response_line:
                        tools_response = json.loads(tools_response_line.strip())
                        if "result" in tools_response:
                            tools_count = len(tools_response["result"]["tools"])
                            print(f"✅ Tools list successful! Found {tools_count} tools")

                            # Show first few tools
                            for i, tool in enumerate(tools_response["result"]["tools"][:5]):
                                print(f"   {i+1}. {tool['name']}: {tool['description']}")
                            if tools_count > 5:
                                print(f"   ... and {tools_count - 5} more tools")

                            print("\n🎉 MCP Server is working correctly!")
                            return True
                        else:
                            print(f"❌ Tools list failed: {tools_response}")
                    else:
                        print("❌ No response to tools/list request")
                else:
                    print(f"❌ Initialize failed: {response}")
            except json.JSONDecodeError as e:
                print(f"❌ Invalid JSON response: {e}")
                print(f"   Raw response: {response_line}")
        else:
            print("❌ No response from server")

    except Exception as e:
        print(f"❌ Error testing MCP server: {e}")

    finally:
        try:
            process.terminate()
            process.wait(timeout=5)
        except:
            process.kill()

    return False

if __name__ == "__main__":
    success = test_mcp_server()
    sys.exit(0 if success else 1)
