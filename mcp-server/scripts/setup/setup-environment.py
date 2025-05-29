#!/usr/bin/env python3
"""
MCP Server Environment Setup Script
Helps users set up their environment variables and configuration files.
"""

import os
import sys
import shutil
from pathlib import Path

class MCPEnvironmentSetup:
    """Setup environment for MCP server."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.env_example = self.project_root / ".env.example"
        self.env_file = self.project_root / ".env"
        
    def check_prerequisites(self):
        """Check if all prerequisites are installed."""
        print("🔍 Checking prerequisites...")
        
        # Check Python
        try:
            import sys
            python_version = sys.version_info
            if python_version.major >= 3 and python_version.minor >= 8:
                print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
            else:
                print(f"❌ Python {python_version.major}.{python_version.minor} (requires 3.8+)")
                return False
        except Exception as e:
            print(f"❌ Python check failed: {e}")
            return False
            
        # Check required packages
        required_packages = ['aiohttp', 'mcp', 'pytest']
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package)
                print(f"✅ {package}")
            except ImportError:
                missing_packages.append(package)
                print(f"❌ {package} (missing)")
        
        if missing_packages:
            print(f"\n📦 Install missing packages:")
            print(f"pip install {' '.join(missing_packages)}")
            return False
            
        # Check Docker (optional)
        if shutil.which('docker'):
            print("✅ Docker")
        else:
            print("⚠️  Docker (optional, for containerized deployment)")
            
        return True
    
    def setup_environment_file(self):
        """Create .env file from template."""
        print("\n🔧 Setting up environment file...")
        
        if self.env_file.exists():
            response = input(f"📄 {self.env_file} already exists. Overwrite? (y/N): ")
            if response.lower() != 'y':
                print("⏭️  Skipping environment file setup")
                return True
        
        if not self.env_example.exists():
            print(f"❌ Template file {self.env_example} not found")
            return False
            
        try:
            shutil.copy2(self.env_example, self.env_file)
            print(f"✅ Created {self.env_file}")
            print(f"📝 Edit {self.env_file} to add your API keys")
            return True
        except Exception as e:
            print(f"❌ Failed to create environment file: {e}")
            return False
    
    def validate_configuration(self):
        """Validate the MCP configuration files."""
        print("\n🔍 Validating configuration...")
        
        config_files = [
            self.project_root / ".mcp.json",
            self.project_root / "config" / "mcp-config.json",
            self.project_root / "config" / "clients" / "claude-desktop.json"
        ]
        
        all_valid = True
        for config_file in config_files:
            if config_file.exists():
                try:
                    import json
                    with open(config_file, 'r') as f:
                        json.load(f)
                    print(f"✅ {config_file.name}")
                except json.JSONDecodeError as e:
                    print(f"❌ {config_file.name}: Invalid JSON - {e}")
                    all_valid = False
                except Exception as e:
                    print(f"❌ {config_file.name}: {e}")
                    all_valid = False
            else:
                print(f"❌ {config_file.name}: File not found")
                all_valid = False
        
        return all_valid
    
    def test_server_startup(self):
        """Test if the MCP server can start."""
        print("\n🧪 Testing server startup...")
        
        server_file = self.project_root / "src" / "server" / "unified_mcp_v2.py"
        if not server_file.exists():
            print(f"❌ Server file not found: {server_file}")
            return False
        
        try:
            import subprocess
            result = subprocess.run([
                sys.executable, str(server_file), "--help"
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                print("✅ Server can start successfully")
                return True
            else:
                print(f"❌ Server startup failed: {result.stderr}")
                return False
        except subprocess.TimeoutExpired:
            print("❌ Server startup timed out")
            return False
        except Exception as e:
            print(f"❌ Server test failed: {e}")
            return False
    
    def show_next_steps(self):
        """Show next steps to the user."""
        print("\n🎉 Setup Complete!")
        print("\n📋 Next Steps:")
        print("1. Edit .env file with your API keys:")
        print(f"   - {self.env_file}")
        print("\n2. Test the server:")
        print("   python src/server/unified_mcp_v2.py --help")
        print("\n3. Run tests:")
        print("   python -m pytest tests/test_mcp_connection.py -v")
        print("\n4. Configure Claude Desktop:")
        print("   - Copy config/clients/claude-desktop.json to Claude Desktop config")
        print("\n5. Start with Docker (optional):")
        print("   docker-compose -f docker/docker-compose.yml up")
        print("\n📚 Documentation:")
        print("   - README.md - Getting started guide")
        print("   - docs/guides/ - Detailed guides")
        print("   - docs/deployment/ - Deployment options")
    
    def run_setup(self):
        """Run the complete setup process."""
        print("🚀 MCP Server Environment Setup")
        print("=" * 40)
        
        # Check prerequisites
        if not self.check_prerequisites():
            print("\n❌ Prerequisites check failed")
            print("Please install missing dependencies and try again")
            return False
        
        # Setup environment file
        if not self.setup_environment_file():
            print("\n❌ Environment setup failed")
            return False
        
        # Validate configuration
        if not self.validate_configuration():
            print("\n⚠️  Configuration validation failed")
            print("Some configuration files have issues")
        
        # Test server startup
        if not self.test_server_startup():
            print("\n⚠️  Server startup test failed")
            print("The server may have issues starting")
        
        # Show next steps
        self.show_next_steps()
        return True

def main():
    """Main entry point."""
    setup = MCPEnvironmentSetup()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'check':
            setup.check_prerequisites()
        elif command == 'env':
            setup.setup_environment_file()
        elif command == 'validate':
            setup.validate_configuration()
        elif command == 'test':
            setup.test_server_startup()
        else:
            print("❌ Unknown command!")
            print("Usage: python setup-environment.py [check|env|validate|test]")
    else:
        # Run full setup
        setup.run_setup()

if __name__ == "__main__":
    main()
