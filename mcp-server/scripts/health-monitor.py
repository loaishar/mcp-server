#!/usr/bin/env python3
"""
MCP Server Health Monitor
Real-time monitoring of MCP server health and performance
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime
from typing import Dict, Any

class MCPHealthMonitor:
    def __init__(self, http_port: int = 3333):
        self.http_port = http_port
        self.base_url = f"http://localhost:{http_port}"
        
    async def check_server_health(self) -> Dict[str, Any]:
        """Check the health of the unified MCP server"""
        try:
            async with aiohttp.ClientSession() as session:
                # Check health endpoint
                async with session.get(f"{self.base_url}/health") as response:
                    if response.status == 200:
                        health_data = await response.json()
                        return {
                            "status": "healthy",
                            "response_time": response.headers.get("X-Response-Time", "N/A"),
                            "data": health_data
                        }
                    else:
                        return {
                            "status": "unhealthy",
                            "error": f"HTTP {response.status}"
                        }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def get_server_statistics(self) -> Dict[str, Any]:
        """Get detailed server statistics via JSON-RPC"""
        try:
            async with aiohttp.ClientSession() as session:
                rpc_request = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/call",
                    "params": {
                        "name": "server_statistics",
                        "arguments": {}
                    }
                }
                
                async with session.post(
                    f"{self.base_url}/rpc",
                    json=rpc_request,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        if "result" in result:
                            # Parse the JSON content from the text response
                            content = result["result"]["content"][0]["text"]
                            return json.loads(content)
                        else:
                            return {"error": "No result in response"}
                    else:
                        return {"error": f"HTTP {response.status}"}
        except Exception as e:
            return {"error": str(e)}
    
    async def get_connected_servers(self) -> Dict[str, Any]:
        """Get list of connected MCP servers"""
        try:
            async with aiohttp.ClientSession() as session:
                rpc_request = {
                    "jsonrpc": "2.0",
                    "id": 2,
                    "method": "tools/call",
                    "params": {
                        "name": "list_connected_servers",
                        "arguments": {}
                    }
                }
                
                async with session.post(
                    f"{self.base_url}/rpc",
                    json=rpc_request,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        if "result" in result:
                            content = result["result"]["content"][0]["text"]
                            return json.loads(content)
                        else:
                            return {"error": "No result in response"}
                    else:
                        return {"error": f"HTTP {response.status}"}
        except Exception as e:
            return {"error": str(e)}
    
    def format_health_report(self, health: Dict, stats: Dict, servers: Dict) -> str:
        """Format a comprehensive health report"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        report = f"""
🔍 MCP Server Health Report - {timestamp}
{'=' * 60}

🏥 Overall Health: {health.get('status', 'unknown').upper()}
📊 Server Version: {health.get('data', {}).get('version', 'N/A')}
🚀 Transport: {health.get('data', {}).get('transport', 'N/A')}

📈 Performance Statistics:
"""
        
        if "unified_server" in stats:
            unified = stats["unified_server"]
            report += f"""  • Initialized: {unified.get('initialized', 'N/A')}
  • Total Tools: {unified.get('total_tools', 0)}
  • Total Resources: {unified.get('total_resources', 0)}
  • Total Prompts: {unified.get('total_prompts', 0)}
"""
        
        if "summary" in stats:
            summary = stats["summary"]
            report += f"""
🔗 Connected Servers Summary:
  • Total Servers: {summary.get('total_servers', 0)}
  • Healthy: {summary.get('healthy_servers', 0)}
  • Unhealthy: {summary.get('unhealthy_servers', 0)}
  • Total Requests: {summary.get('total_requests', 0)}
  • Total Errors: {summary.get('total_errors', 0)}
"""
        
        report += "\n🖥️  Individual Server Status:\n"
        
        if isinstance(servers, dict):
            for name, info in servers.items():
                status = "🟢" if info.get('connected', False) and info.get('initialized', False) else "🔴"
                report += f"  {status} {name}: "
                report += f"Tools({info.get('tools_count', 0)}) "
                report += f"Resources({info.get('resources_count', 0)}) "
                report += f"Prompts({info.get('prompts_count', 0)})\n"
        
        return report
    
    async def monitor_continuous(self, interval: int = 30):
        """Continuously monitor server health"""
        print("🔍 Starting continuous MCP server monitoring...")
        print(f"📊 Checking every {interval} seconds")
        print("Press Ctrl+C to stop\n")
        
        try:
            while True:
                health = await self.check_server_health()
                stats = await self.get_server_statistics()
                servers = await self.get_connected_servers()
                
                # Clear screen (works on most terminals)
                print("\033[2J\033[H", end="")
                
                report = self.format_health_report(health, stats, servers)
                print(report)
                
                await asyncio.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n👋 Monitoring stopped by user")

async def main():
    import sys
    
    monitor = MCPHealthMonitor()
    
    if len(sys.argv) > 1 and sys.argv[1] == "continuous":
        interval = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        await monitor.monitor_continuous(interval)
    else:
        # Single check
        print("🔍 Checking MCP server health...")
        
        health = await monitor.check_server_health()
        stats = await monitor.get_server_statistics()
        servers = await monitor.get_connected_servers()
        
        report = monitor.format_health_report(health, stats, servers)
        print(report)
        
        print("\n💡 Use 'python health-monitor.py continuous [interval]' for continuous monitoring")

if __name__ == "__main__":
    asyncio.run(main())
