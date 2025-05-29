#!/usr/bin/env python3
"""
Test script to verify MCP server connection
"""

import subprocess
import json
import sys

def test_mcp_server():
    """Test the MCP server connection"""
    print("🔍 Testing MCP Server Connection...")

    try:
        # Start the MCP server
        process = subprocess.Popen(
            ["python", "src/server/unified_mcp_v2.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd="C:\\Users\\loai1\\Documents\\GitHub\\mcp-server\\mcp-server"
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

                    # Send initialized notification
                    initialized_notification = {
                        "jsonrpc": "2.0",
                        "method": "initialized",
                        "params": {}
                    }
                    print("📤 Sending initialized notification...")
                    process.stdin.write(json.dumps(initialized_notification) + "\n")
                    process.stdin.flush()

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
                            assert True
                            return
                        else:
                            print(f"❌ Tools list failed: {tools_response}")
                            assert False, "Tools list failed"
                    else:
                        print("❌ No response to tools/list request")
                        assert False, "No response to tools/list request"
                else:
                    print(f"❌ Initialize failed: {response}")
                    assert False, "Initialize failed"
            except json.JSONDecodeError as e:
                print(f"❌ Invalid JSON response: {e}")
                print(f"   Raw response: {response_line}")
                assert False, f"Invalid JSON response: {e}"
        else:
            print("❌ No response from server")
            assert False, "No response from server"

    except Exception as e:
        print(f"❌ Error testing MCP server: {e}")
        assert False, f"Error testing MCP server: {e}"

    finally:
        try:
            process.terminate()
            process.wait(timeout=5)
        except:
            process.kill()

if __name__ == "__main__":
    try:
        test_mcp_server()
        print("✅ All tests passed!")
        sys.exit(0)
    except AssertionError as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)
