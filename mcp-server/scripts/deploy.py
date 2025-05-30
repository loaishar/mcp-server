#!/usr/bin/env python3
"""
MCP Server Deployment Manager
Automated deployment and management of MCP server infrastructure
"""

import subprocess
import json
import time
import sys
from pathlib import Path

class MCPDeploymentManager:
    def __init__(self):
        self.root_dir = Path(__file__).parent.parent
        self.docker_dir = self.root_dir / "docker"
        
    def run_command(self, command: str, cwd=None):
        """Run a shell command and return the result"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=cwd or self.docker_dir,
                capture_output=True,
                text=True,
                check=True
            )
            return True, result.stdout
        except subprocess.CalledProcessError as e:
            return False, e.stderr
    
    def check_docker_status(self):
        """Check if Docker is running"""
        success, output = self.run_command("docker --version")
        if not success:
            print("❌ Docker is not installed or not running")
            return False
        print(f"✅ Docker is available: {output.strip()}")
        return True
    
    def build_images(self):
        """Build MCP server Docker images"""
        print("🔨 Building MCP server images...")
        
        # Build unified MCP server
        success, output = self.run_command("docker-compose build unified-mcp-stdio unified-mcp-http")
        if not success:
            print(f"❌ Failed to build images: {output}")
            return False
        
        print("✅ Successfully built MCP server images")
        return True
    
    def deploy_servers(self):
        """Deploy MCP servers"""
        print("🚀 Deploying MCP servers...")
        
        # Start services
        success, output = self.run_command("docker-compose up -d unified-mcp-stdio unified-mcp-http")
        if not success:
            print(f"❌ Failed to deploy servers: {output}")
            return False
        
        print("✅ MCP servers deployed successfully")
        
        # Wait for health check
        print("⏳ Waiting for servers to become healthy...")
        time.sleep(10)
        
        # Check status
        success, output = self.run_command("docker-compose ps unified-mcp-stdio unified-mcp-http")
        if success:
            print("📊 Server status:")
            print(output)
        
        return True
    
    def check_health(self):
        """Check server health"""
        print("🏥 Checking server health...")
        
        # Check container status
        success, output = self.run_command("docker-compose ps --format json")
        if success:
            try:
                containers = [json.loads(line) for line in output.strip().split('\n') if line]
                for container in containers:
                    name = container.get('Name', 'Unknown')
                    state = container.get('State', 'Unknown')
                    health = container.get('Health', 'N/A')
                    
                    status_icon = "✅" if state == "running" and health in ["healthy", "N/A"] else "❌"
                    print(f"  {status_icon} {name}: {state} ({health})")
            except:
                print("📊 Container status (raw):")
                print(output)
        
        # Test HTTP endpoint
        success, output = self.run_command("curl -s http://localhost:3333/health")
        if success:
            print("✅ HTTP endpoint is responding")
            try:
                health_data = json.loads(output)
                print(f"   Status: {health_data.get('status', 'unknown')}")
                print(f"   Version: {health_data.get('version', 'unknown')}")
            except:
                print(f"   Raw response: {output}")
        else:
            print("❌ HTTP endpoint is not responding")
    
    def stop_servers(self):
        """Stop MCP servers"""
        print("🛑 Stopping MCP servers...")
        
        success, output = self.run_command("docker-compose down")
        if not success:
            print(f"❌ Failed to stop servers: {output}")
            return False
        
        print("✅ MCP servers stopped successfully")
        return True
    
    def restart_servers(self):
        """Restart MCP servers"""
        print("🔄 Restarting MCP servers...")
        
        success, output = self.run_command("docker-compose restart unified-mcp-stdio unified-mcp-http")
        if not success:
            print(f"❌ Failed to restart servers: {output}")
            return False
        
        print("✅ MCP servers restarted successfully")
        time.sleep(5)  # Wait for restart
        self.check_health()
        return True
    
    def show_logs(self, service=None, tail=50):
        """Show server logs"""
        if service:
            command = f"docker-compose logs --tail={tail} {service}"
        else:
            command = f"docker-compose logs --tail={tail}"
        
        success, output = self.run_command(command)
        if success:
            print(f"📋 Server logs (last {tail} lines):")
            print(output)
        else:
            print(f"❌ Failed to get logs: {output}")
    
    def full_deployment(self):
        """Perform a full deployment"""
        print("🚀 Starting full MCP server deployment...")
        
        if not self.check_docker_status():
            return False
        
        if not self.build_images():
            return False
        
        if not self.deploy_servers():
            return False
        
        self.check_health()
        
        print("\n🎉 Deployment completed successfully!")
        print("\n📋 Next steps:")
        print("  1. Configure Claude Desktop with the MCP server")
        print("  2. Test the connection")
        print("  3. Monitor with: python scripts/health-monitor.py")
        
        return True

def main():
    manager = MCPDeploymentManager()
    
    if len(sys.argv) < 2:
        print("🚀 MCP Server Deployment Manager")
        print("\nUsage:")
        print("  python deploy.py full        # Full deployment")
        print("  python deploy.py build       # Build images only")
        print("  python deploy.py deploy      # Deploy servers")
        print("  python deploy.py health      # Check health")
        print("  python deploy.py restart     # Restart servers")
        print("  python deploy.py stop        # Stop servers")
        print("  python deploy.py logs [service] [lines]  # Show logs")
        return
    
    command = sys.argv[1]
    
    if command == "full":
        manager.full_deployment()
    elif command == "build":
        manager.check_docker_status()
        manager.build_images()
    elif command == "deploy":
        manager.deploy_servers()
    elif command == "health":
        manager.check_health()
    elif command == "restart":
        manager.restart_servers()
    elif command == "stop":
        manager.stop_servers()
    elif command == "logs":
        service = sys.argv[2] if len(sys.argv) > 2 else None
        tail = int(sys.argv[3]) if len(sys.argv) > 3 else 50
        manager.show_logs(service, tail)
    else:
        print(f"❌ Unknown command: {command}")

if __name__ == "__main__":
    main()
