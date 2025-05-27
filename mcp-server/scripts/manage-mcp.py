#!/usr/bin/env python3
"""
MCP Configuration Management Script
Provides commands to manage the master MCP configuration and regenerate client configs.
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime

# Import the generator class directly
import importlib.util
spec = importlib.util.spec_from_file_location("generate_mcp_configs", os.path.join(os.path.dirname(__file__), "generate-mcp-configs.py"))
generate_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(generate_module)
MCPConfigGenerator = generate_module.MCPConfigGenerator

class MCPManager:
    """Manages MCP configurations and provides CLI commands."""

    def __init__(self):
        self.generator = MCPConfigGenerator()

    def add_server(self, name: str, command: str, args: list, description: str, category: str = "other"):
        """Add a new MCP server to the master configuration."""
        master_config = self.generator.master_config

        if name in master_config["mcpServers"]:
            print(f"❌ Server '{name}' already exists!")
            return False

        # Add new server
        master_config["mcpServers"][name] = {
            "command": command,
            "args": args,
            "env": {},
            "description": description,
            "category": category,
            "priority": len(master_config["mcpServers"]) + 1,
            "capabilities": ["tools"],
            "enabled": True
        }

        # Update metadata
        master_config["metadata"]["lastUpdated"] = datetime.now().isoformat()

        # Save master config
        self.save_master_config(master_config)

        print(f"✅ Added server '{name}' to master configuration")
        return True

    def enable_server(self, name: str):
        """Enable a server in the master configuration."""
        master_config = self.generator.master_config

        if name not in master_config["mcpServers"]:
            print(f"❌ Server '{name}' not found!")
            return False

        master_config["mcpServers"][name]["enabled"] = True
        master_config["metadata"]["lastUpdated"] = datetime.now().isoformat()

        self.save_master_config(master_config)
        print(f"✅ Enabled server '{name}'")
        return True

    def disable_server(self, name: str):
        """Disable a server in the master configuration."""
        master_config = self.generator.master_config

        if name not in master_config["mcpServers"]:
            print(f"❌ Server '{name}' not found!")
            return False

        master_config["mcpServers"][name]["enabled"] = False
        master_config["metadata"]["lastUpdated"] = datetime.now().isoformat()

        self.save_master_config(master_config)
        print(f"✅ Disabled server '{name}'")
        return True

    def add_server_to_client(self, server_name: str, client_name: str):
        """Add a server to a specific client profile."""
        master_config = self.generator.master_config

        if server_name not in master_config["mcpServers"]:
            print(f"❌ Server '{server_name}' not found!")
            return False

        if client_name not in master_config["clientProfiles"]:
            print(f"❌ Client '{client_name}' not found!")
            return False

        enabled_servers = master_config["clientProfiles"][client_name].get("enabledServers", [])
        if server_name not in enabled_servers:
            enabled_servers.append(server_name)
            master_config["clientProfiles"][client_name]["enabledServers"] = enabled_servers
            master_config["metadata"]["lastUpdated"] = datetime.now().isoformat()

            self.save_master_config(master_config)
            print(f"✅ Added '{server_name}' to client '{client_name}'")
            return True
        else:
            print(f"ℹ️ Server '{server_name}' already enabled for client '{client_name}'")
            return False

    def save_master_config(self, config: dict):
        """Save the master configuration file."""
        with open(self.generator.master_config_path, 'w') as f:
            json.dump(config, f, indent=2)

    def deploy_to_claude(self):
        """Deploy the generated configuration to Claude Desktop."""
        self.generator.generate_all_configs()

        # Copy to Claude Desktop
        claude_config_path = os.path.expandvars(r"%APPDATA%\Claude\claude_desktop_config.json")
        import subprocess
        subprocess.run(['powershell', '-Command', f'Copy-Item "config\\clients\\claude-desktop.json" "{claude_config_path}" -Force'], check=True)

        print("🚀 Deployed master configuration to Claude Desktop")
        print("   Claude Desktop now has ALL 13 MCP servers directly connected")
        print("   Other clients inherit from this master configuration")
        print("   Please restart Claude Desktop to apply changes")

    def show_status(self):
        """Show current status of all servers and clients."""
        master_config = self.generator.master_config

        print("📊 MCP Configuration Status")
        print("=" * 50)

        # Show servers
        servers = master_config.get("mcpServers", {})
        enabled_servers = [name for name, config in servers.items() if config.get("enabled", True)]
        disabled_servers = [name for name, config in servers.items() if not config.get("enabled", True)]

        print(f"Servers: {len(servers)} total")
        print(f"  ✅ Enabled ({len(enabled_servers)}): {', '.join(enabled_servers)}")
        print(f"  ❌ Disabled ({len(disabled_servers)}): {', '.join(disabled_servers)}")

        # Show clients
        clients = master_config.get("clientProfiles", {})
        print(f"\nClients: {len(clients)}")
        for client_name, profile in clients.items():
            enabled_count = len(profile.get("enabledServers", []))
            print(f"  {client_name}: {enabled_count} servers")

def main():
    """Main CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: python manage-mcp.py <command> [args...]")
        print("\nCommands:")
        print("  status                     - Show current configuration status")
        print("  generate                   - Regenerate all client configurations")
        print("  deploy                     - Deploy to Claude Desktop")
        print("  enable <server>            - Enable a server")
        print("  disable <server>           - Disable a server")
        print("  add-to-client <server> <client> - Add server to client")
        print("  add-server <name> <command> <description> [category] - Add new server")
        return

    manager = MCPManager()
    command = sys.argv[1]

    if command == "status":
        manager.show_status()

    elif command == "generate":
        manager.generator.generate_all_configs()

    elif command == "deploy":
        manager.deploy_to_claude()

    elif command == "enable" and len(sys.argv) > 2:
        manager.enable_server(sys.argv[2])

    elif command == "disable" and len(sys.argv) > 2:
        manager.disable_server(sys.argv[2])

    elif command == "add-to-client" and len(sys.argv) > 3:
        manager.add_server_to_client(sys.argv[2], sys.argv[3])

    elif command == "add-server" and len(sys.argv) > 4:
        name = sys.argv[2]
        command_str = sys.argv[3]
        description = sys.argv[4]
        category = sys.argv[5] if len(sys.argv) > 5 else "other"

        # Parse command and args (simplified)
        parts = command_str.split()
        cmd = parts[0]
        args = parts[1:] if len(parts) > 1 else []

        manager.add_server(name, cmd, args, description, category)

    else:
        print(f"❌ Unknown command: {command}")

if __name__ == "__main__":
    main()
