#!/usr/bin/env python3
"""
Claude Code MCP Setup Script
Helps with importing MCP servers from Claude Desktop to Claude Code
"""

import json
import os
import re
import sys
import subprocess

class ClaudeCodeSetup:
    """Setup and manage Claude Code MCP integration."""

    def __init__(self):
        self.claude_desktop_config = self.find_claude_desktop_config()

    def find_claude_desktop_config(self):
        """Find Claude Desktop configuration file."""
        # Windows path
        if os.name == 'nt':
            appdata = os.environ.get('APPDATA')
            if appdata:
                config_path = os.path.join(appdata, 'Claude', 'claude_desktop_config.json')
                if os.path.exists(config_path):
                    return config_path

        # macOS path
        home = os.path.expanduser('~')
        macos_path = os.path.join(home, 'Library', 'Application Support', 'Claude', 'claude_desktop_config.json')
        if os.path.exists(macos_path):
            return macos_path

        return None

    def validate_server_names(self):
        """Check if server names are compatible with Claude Code."""
        if not self.claude_desktop_config:
            print("❌ Claude Desktop configuration not found!")
            return False

        try:
            with open(self.claude_desktop_config, 'r') as f:
                config = json.load(f)
        except Exception as e:
            print(f"❌ Failed to load Claude Desktop config: {e}")
            return False

        servers = config.get('mcpServers', {})
        pattern = re.compile(r'^[a-zA-Z0-9_-]{1,64}$')

        print("🔍 Validating server names for Claude Code compatibility...")

        valid_names = []
        invalid_names = []

        for server_name in servers.keys():
            if pattern.match(server_name):
                valid_names.append(server_name)
            else:
                invalid_names.append(server_name)

        print(f"✅ Valid names ({len(valid_names)}):")
        for name in valid_names:
            print(f"   - {name}")

        if invalid_names:
            print(f"\n❌ Invalid names ({len(invalid_names)}):")
            for name in invalid_names:
                print(f"   - '{name}' (contains invalid characters)")
                suggested = re.sub(r'[^a-zA-Z0-9_-]', '-', name)
                suggested = re.sub(r'-+', '-', suggested)  # Remove multiple dashes
                suggested = suggested.strip('-')  # Remove leading/trailing dashes
                print(f"     Suggested: '{suggested}'")

            print(f"\n🔧 To fix invalid names:")
            print("1. Update your Claude Desktop configuration")
            print("2. Restart Claude Desktop")
            print("3. Re-run this script")
            return False

        return True

    def check_claude_code_cli(self):
        """Check if Claude Code CLI is available."""
        try:
            result = subprocess.run(['claude', '--version'],
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print(f"✅ Claude Code CLI found: {result.stdout.strip()}")
                return True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

        print("❌ Claude Code CLI not found!")
        print("📋 Installation options:")
        print("   - macOS: Download from https://claude.ai/code")
        print("   - WSL: curl -fsSL https://claude.ai/install.sh | sh")
        return False

    def import_servers(self, global_config=True):
        """Import servers from Claude Desktop to Claude Code."""
        if not self.check_claude_code_cli():
            return False

        if not self.validate_server_names():
            return False

        print("🚀 Importing MCP servers from Claude Desktop to Claude Code...")

        # Build command
        cmd = ['claude', 'mcp', 'add-from-claude-desktop']
        if global_config:
            cmd.extend(['-s', 'global'])

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

            if result.returncode == 0:
                print("✅ Import successful!")
                print(result.stdout)
                return True
            else:
                print("❌ Import failed!")
                print(result.stderr)
                return False

        except subprocess.TimeoutExpired:
            print("❌ Import timed out!")
            return False
        except Exception as e:
            print(f"❌ Import error: {e}")
            return False

    def list_servers(self):
        """List imported servers in Claude Code."""
        try:
            result = subprocess.run(['claude', 'mcp', 'list'],
                                  capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                print("📊 Claude Code MCP Servers:")
                print(result.stdout)
                return True
            else:
                print("❌ Failed to list servers!")
                print(result.stderr)
                return False

        except Exception as e:
            print(f"❌ Error listing servers: {e}")
            return False

    def show_status(self):
        """Show comprehensive status of MCP setup."""
        print("📊 Claude Code MCP Setup Status")
        print("=" * 50)

        # Check Claude Desktop config
        if self.claude_desktop_config:
            print(f"✅ Claude Desktop config: {self.claude_desktop_config}")
            try:
                with open(self.claude_desktop_config, 'r') as f:
                    config = json.load(f)
                server_count = len(config.get('mcpServers', {}))
                print(f"   📈 Servers configured: {server_count}")
            except:
                print("   ❌ Failed to read configuration")
        else:
            print("❌ Claude Desktop config: Not found")

        # Check Claude Code CLI
        print()
        self.check_claude_code_cli()

        # Check server name compatibility
        print()
        self.validate_server_names()

        # List Claude Code servers
        print()
        self.list_servers()

def main():
    """Main entry point."""
    setup = ClaudeCodeSetup()

    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == 'status':
            setup.show_status()
        elif command == 'validate':
            setup.validate_server_names()
        elif command == 'import':
            setup.import_servers()
        elif command == 'list':
            setup.list_servers()
        elif command == 'check':
            setup.check_claude_code_cli()
        else:
            print("❌ Unknown command!")
            print_usage()
    else:
        # Interactive mode
        print("🚀 Claude Code MCP Setup")
        print("=" * 30)
        setup.show_status()

        if input("\n🔄 Import servers to Claude Code? (y/N): ").lower() == 'y':
            setup.import_servers()
            print()
            setup.list_servers()

def print_usage():
    """Print usage information."""
    print("Usage: python setup-claude-code.py [command]")
    print()
    print("Commands:")
    print("  status    - Show comprehensive setup status")
    print("  validate  - Check server name compatibility")
    print("  import    - Import servers from Claude Desktop")
    print("  list      - List Claude Code servers")
    print("  check     - Check Claude Code CLI availability")
    print()
    print("Examples:")
    print("  python setup-claude-code.py status")
    print("  python setup-claude-code.py import")

if __name__ == "__main__":
    main()
