#!/usr/bin/env python3
"""
MCP Configuration Generator
Generates client-specific MCP configurations from the master configuration file.
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

class MCPConfigGenerator:
    """Generates MCP configurations for different clients from master config."""
    
    def __init__(self, master_config_path: str = "config/master-mcp-config.json"):
        self.master_config_path = master_config_path
        self.master_config = self.load_master_config()
        
    def load_master_config(self) -> Dict[str, Any]:
        """Load the master configuration file."""
        try:
            with open(self.master_config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ Master config file not found: {self.master_config_path}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in master config: {e}")
            sys.exit(1)
            
    def get_enabled_servers(self, client_name: str) -> List[str]:
        """Get list of enabled servers for a specific client."""
        client_profile = self.master_config.get("clientProfiles", {}).get(client_name, {})
        enabled_servers = client_profile.get("enabledServers", [])
        
        # If no specific servers listed, use all enabled servers
        if not enabled_servers:
            enabled_servers = [
                name for name, config in self.master_config["mcpServers"].items()
                if config.get("enabled", True)  # Default to enabled if not specified
            ]
            
        return enabled_servers
        
    def generate_client_config(self, client_name: str) -> Dict[str, Any]:
        """Generate configuration for a specific client."""
        enabled_servers = self.get_enabled_servers(client_name)
        client_profile = self.master_config.get("clientProfiles", {}).get(client_name, {})
        
        # Build the client configuration
        client_config = {
            "mcpServers": {}
        }
        
        # Add enabled servers
        for server_name in enabled_servers:
            if server_name in self.master_config["mcpServers"]:
                server_config = self.master_config["mcpServers"][server_name].copy()
                
                # Remove metadata fields that clients don't need
                for field in ["category", "priority", "capabilities", "toolCount", "enabled", "note"]:
                    server_config.pop(field, None)
                    
                client_config["mcpServers"][server_name] = server_config
                
        return client_config
        
    def generate_all_configs(self):
        """Generate configurations for all defined clients."""
        print("🔧 Generating MCP configurations from master config...")
        
        # Ensure output directories exist
        os.makedirs("config/clients", exist_ok=True)
        
        clients = self.master_config.get("clientProfiles", {})
        
        for client_name, client_profile in clients.items():
            print(f"📝 Generating config for {client_name}...")
            
            # Generate client config
            client_config = self.generate_client_config(client_name)
            
            # Add metadata comment
            enabled_servers = self.get_enabled_servers(client_name)
            client_config["_metadata"] = {
                "generated_from": "master-mcp-config.json",
                "generated_at": datetime.now().isoformat(),
                "client": client_name,
                "description": client_profile.get("description", ""),
                "enabled_servers": enabled_servers,
                "server_count": len(enabled_servers)
            }
            
            # Write client config file
            output_file = f"config/clients/{client_name}.json"
            with open(output_file, 'w') as f:
                json.dump(client_config, f, indent=2)
                
            print(f"   ✅ {output_file} ({len(enabled_servers)} servers)")
            
        # Generate legacy files for backward compatibility
        self.generate_legacy_files()
        
        print("🎉 All MCP configurations generated successfully!")
        
    def generate_legacy_files(self):
        """Generate legacy configuration files for backward compatibility."""
        print("📄 Generating legacy configuration files...")
        
        # Generate .mcp.json (for unified MCP server)
        mcp_config = {
            "mcpServers": {},
            "version": self.master_config["metadata"]["version"],
            "description": "Generated from master configuration",
            "author": self.master_config["metadata"]["author"]
        }
        
        # Include all servers (enabled and disabled) for unified server
        for server_name, server_config in self.master_config["mcpServers"].items():
            clean_config = server_config.copy()
            for field in ["category", "priority", "capabilities", "toolCount", "enabled", "note"]:
                clean_config.pop(field, None)
            mcp_config["mcpServers"][server_name] = clean_config
            
        with open(".mcp.json", 'w') as f:
            json.dump(mcp_config, f, indent=2)
            
        # Copy Claude Desktop config to the expected location
        claude_config = self.generate_client_config("claude-desktop")
        with open("config/clients/claude-desktop.json", 'w') as f:
            json.dump(claude_config, f, indent=2)
            
        print("   ✅ .mcp.json (for unified MCP server)")
        print("   ✅ config/clients/claude-desktop.json")
        
    def show_summary(self):
        """Show a summary of the master configuration."""
        print("\n📊 Master MCP Configuration Summary")
        print("=" * 50)
        
        metadata = self.master_config.get("metadata", {})
        print(f"Version: {metadata.get('version', 'Unknown')}")
        print(f"Last Updated: {metadata.get('lastUpdated', 'Unknown')}")
        
        # Count servers by category and status
        servers = self.master_config.get("mcpServers", {})
        enabled_count = sum(1 for s in servers.values() if s.get("enabled", True))
        disabled_count = len(servers) - enabled_count
        
        print(f"\nServers: {len(servers)} total ({enabled_count} enabled, {disabled_count} disabled)")
        
        # Group by category
        categories = {}
        for name, config in servers.items():
            category = config.get("category", "other")
            if category not in categories:
                categories[category] = []
            categories[category].append(name)
            
        for category, server_list in categories.items():
            print(f"  {category.title()}: {', '.join(server_list)}")
            
        # Show client profiles
        clients = self.master_config.get("clientProfiles", {})
        print(f"\nClient Profiles: {len(clients)}")
        for client_name, profile in clients.items():
            enabled_servers = profile.get("enabledServers", [])
            print(f"  {client_name}: {len(enabled_servers)} servers")

def main():
    """Main entry point."""
    if len(sys.argv) > 1 and sys.argv[1] == "--summary":
        generator = MCPConfigGenerator()
        generator.show_summary()
    else:
        generator = MCPConfigGenerator()
        generator.generate_all_configs()
        generator.show_summary()

if __name__ == "__main__":
    main()
