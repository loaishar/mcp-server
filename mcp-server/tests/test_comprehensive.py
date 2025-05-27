#!/usr/bin/env python3
"""
Comprehensive test script for the MCP Server
Tests all functionality, security, and configuration
"""

import requests
import json
import os
import time
import subprocess
from typing import Dict, Any
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MCPServerTester:
    def __init__(self, base_url: str = "http://localhost:3333"):
        self.base_url = base_url
        self.api_keys = {
            "cursor": os.getenv("MCP_CURSOR_API_KEY"),
            "claude": os.getenv("MCP_CLAUDE_API_KEY"),
            "windsurf": os.getenv("MCP_WINDSURF_API_KEY")
        }
        self.test_results = []

    def log_test(self, test_name: str, success: bool, message: str = ""):
        """Log test results."""
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"{status}: {test_name} - {message}")
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message
        })

    def test_server_health(self) -> bool:
        """Test server health endpoint."""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "ok":
                    self.log_test("Server Health", True, f"Version: {data.get('version')}")
                    return True
                else:
                    self.log_test("Server Health", False, f"Status not OK: {data}")
                    return False
            else:
                self.log_test("Server Health", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Server Health", False, f"Connection failed: {str(e)}")
            return False

    def test_schema_endpoint(self) -> bool:
        """Test schema endpoint."""
        try:
            response = requests.get(f"{self.base_url}/schema", timeout=5)
            if response.status_code == 200:
                data = response.json()
                tools = data.get("tools", [])
                if len(tools) > 0:
                    self.log_test("Schema Endpoint", True, f"Found {len(tools)} tools")
                    return True
                else:
                    self.log_test("Schema Endpoint", False, "No tools found")
                    return False
            else:
                self.log_test("Schema Endpoint", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Schema Endpoint", False, f"Request failed: {str(e)}")
            return False

    def test_authentication(self) -> bool:
        """Test API key authentication."""
        results = []
        
        for client, api_key in self.api_keys.items():
            if not api_key:
                self.log_test(f"Auth - {client}", False, "API key not found in environment")
                results.append(False)
                continue
                
            try:
                headers = {"Authorization": f"Bearer {api_key}"}
                response = requests.get(f"{self.base_url}/schema", headers=headers, timeout=5)
                
                if response.status_code == 200:
                    self.log_test(f"Auth - {client}", True, "Authentication successful")
                    results.append(True)
                else:
                    self.log_test(f"Auth - {client}", False, f"HTTP {response.status_code}")
                    results.append(False)
            except Exception as e:
                self.log_test(f"Auth - {client}", False, f"Request failed: {str(e)}")
                results.append(False)
        
        return all(results)

    def test_tool_invocation(self) -> bool:
        """Test tool invocation with system_info tool."""
        api_key = self.api_keys.get("cursor") or self.api_keys.get("claude") or self.api_keys.get("windsurf")
        
        if not api_key:
            self.log_test("Tool Invocation", False, "No API key available")
            return False
            
        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "name": "system_info",
                "args": {}
            }
            
            response = requests.post(
                f"{self.base_url}/invoke",
                headers=headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    self.log_test("Tool Invocation", True, "system_info tool executed successfully")
                    return True
                else:
                    self.log_test("Tool Invocation", False, f"Tool execution failed: {data}")
                    return False
            else:
                self.log_test("Tool Invocation", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Tool Invocation", False, f"Request failed: {str(e)}")
            return False

    def test_rate_limiting(self) -> bool:
        """Test rate limiting functionality."""
        api_key = self.api_keys.get("cursor") or self.api_keys.get("claude") or self.api_keys.get("windsurf")
        
        if not api_key:
            self.log_test("Rate Limiting", False, "No API key available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {api_key}"}
            
            # Make rapid requests to trigger rate limiting
            responses = []
            for i in range(15):  # Exceed the 10 requests per second limit
                response = requests.get(f"{self.base_url}/schema", headers=headers, timeout=2)
                responses.append(response.status_code)
                
            # Check if we got rate limited (HTTP 429)
            rate_limited = any(status == 429 for status in responses)
            
            if rate_limited:
                self.log_test("Rate Limiting", True, "Rate limiting is working")
                return True
            else:
                self.log_test("Rate Limiting", False, "Rate limiting not triggered")
                return False
                
        except Exception as e:
            self.log_test("Rate Limiting", False, f"Test failed: {str(e)}")
            return False

    def test_environment_security(self) -> bool:
        """Test that environment variables are properly configured."""
        required_vars = [
            "MCP_CURSOR_API_KEY",
            "MCP_CLAUDE_API_KEY", 
            "MCP_WINDSURF_API_KEY"
        ]
        
        missing = []
        weak = []
        
        for var in required_vars:
            value = os.getenv(var)
            if not value:
                missing.append(var)
            elif len(value) < 32:
                weak.append(var)
        
        if missing:
            self.log_test("Environment Security", False, f"Missing variables: {missing}")
            return False
        elif weak:
            self.log_test("Environment Security", False, f"Weak keys (< 32 chars): {weak}")
            return False
        else:
            self.log_test("Environment Security", True, "All API keys are properly configured")
            return True

    def test_configuration_files(self) -> bool:
        """Test that configuration files are properly formatted."""
        config_files = [
            "C:\\Users\\loai1\\AppData\\Roaming\\Claude\\claude_desktop_config.json",
            "C:\\Users\\loai1\\.cursor\\mcp.json",
            "C:\\Users\\loai1\\.codeium\\windsurf\\mcp_config.json"
        ]
        
        results = []
        
        for config_file in config_files:
            if os.path.exists(config_file):
                try:
                    with open(config_file, 'r') as f:
                        json.load(f)  # This will raise an exception if JSON is invalid
                    self.log_test(f"Config - {os.path.basename(config_file)}", True, "Valid JSON")
                    results.append(True)
                except json.JSONDecodeError as e:
                    self.log_test(f"Config - {os.path.basename(config_file)}", False, f"Invalid JSON: {str(e)}")
                    results.append(False)
            else:
                self.log_test(f"Config - {os.path.basename(config_file)}", False, "File not found")
                results.append(False)
        
        return all(results)

    def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests and return results."""
        logger.info("=== Starting Comprehensive MCP Server Tests ===")
        
        # Wait for server to be ready
        time.sleep(2)
        
        tests = [
            self.test_server_health,
            self.test_environment_security,
            self.test_configuration_files,
            self.test_schema_endpoint,
            self.test_authentication,
            self.test_tool_invocation,
            self.test_rate_limiting
        ]
        
        for test in tests:
            test()
        
        # Summary
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        success_rate = (passed / total) * 100 if total > 0 else 0
        
        logger.info(f"\n=== Test Results Summary ===")
        logger.info(f"Tests Passed: {passed}/{total} ({success_rate:.1f}%)")
        
        if success_rate < 100:
            logger.warning("Some tests failed. Check the logs above for details.")
        else:
            logger.info("All tests passed! ✅")
        
        return {
            "passed": passed,
            "total": total,
            "success_rate": success_rate,
            "results": self.test_results
        }

if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    tester = MCPServerTester()
    results = tester.run_all_tests()
    
    # Exit with appropriate code
    exit(0 if results["success_rate"] == 100 else 1)
