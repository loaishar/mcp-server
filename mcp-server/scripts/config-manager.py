#!/usr/bin/env python3
"""
MCP Server Configuration Manager
Easily switch between different MCP server configurations
"""

import json
import shutil
import os
import sys
from pathlib import Path

class MCPConfigManager:
    def __init__(self):
        self.root_dir = Path(__file__).parent.parent
        self.config_dir = self.root_dir / "config" / "expansion"
        self.current_config = self.root_dir / ".mcp.json"
        
    def list_configs(self):
        """List all available configurations"""
        configs = []
        if self.config_dir.exists():
            for config_file in self.config_dir.glob("*.json"):
                configs.append(config_file.stem)
        return configs
    
    def get_current_config(self):
        """Get current configuration info"""
        if not self.current_config.exists():
            return None
            
        with open(self.current_config, 'r') as f:
            config = json.load(f)
            
        server_count = len(config.get('mcpServers', {}))
        return {
            'servers': server_count,
            'names': list(config.get('mcpServers', {}).keys())
        }
    
    def switch_config(self, config_name):
        """Switch to a different configuration"""
        config_file = self.config_dir / f"{config_name}.json"
        
        if not config_file.exists():
            print(f"❌ Configuration '{config_name}' not found!")
            return False
            
        # Backup current config
        if self.current_config.exists():
            backup_file = self.current_config.with_suffix('.json.backup')
            shutil.copy2(self.current_config, backup_file)
            print(f"📦 Backed up current config to {backup_file}")
        
        # Copy new config
        shutil.copy2(config_file, self.current_config)
        print(f"✅ Switched to '{config_name}' configuration")
        
        # Show new config info
        new_config = self.get_current_config()
        print(f"📊 New configuration: {new_config['servers']} servers")
        print(f"🔧 Servers: {', '.join(new_config['names'])}")
        
        return True
    
    def create_config(self, name, servers):
        """Create a new configuration"""
        config_file = self.config_dir / f"{name}.json"
        
        if config_file.exists():
            print(f"❌ Configuration '{name}' already exists!")
            return False
            
        config = {"mcpServers": servers}
        
        # Ensure config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
            
        print(f"✅ Created configuration '{name}'")
        return True

def main():
    manager = MCPConfigManager()
    
    if len(sys.argv) < 2:
        print("🔧 MCP Configuration Manager")
        print("\nUsage:")
        print("  python config-manager.py list")
        print("  python config-manager.py current")
        print("  python config-manager.py switch <config-name>")
        print("  python config-manager.py create-basic-plus")
        return
    
    command = sys.argv[1]
    
    if command == "list":
        configs = manager.list_configs()
        print("📋 Available configurations:")
        for config in configs:
            print(f"  • {config}")
            
    elif command == "current":
        current = manager.get_current_config()
        if current:
            print(f"📊 Current configuration: {current['servers']} servers")
            print(f"🔧 Servers: {', '.join(current['names'])}")
        else:
            print("❌ No current configuration found")
            
    elif command == "switch":
        if len(sys.argv) < 3:
            print("❌ Please specify configuration name")
            return
        config_name = sys.argv[2]
        manager.switch_config(config_name)
        
    elif command == "create-basic-plus":
        # Create a basic-plus configuration
        servers = {
            "git": {
                "command": "npx",
                "args": ["-y", "@cyanheads/git-mcp-server"],
                "env": {},
                "description": "Git operations and repository management"
            },
            "memory": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-memory"],
                "env": {},
                "description": "Persistent memory for conversations"
            },
            "sequential-thinking": {
                "command": "npx",
                "args": ["-y", "@cyanheads/sequential-thinking-mcp-server"],
                "env": {},
                "description": "Enhanced reasoning and step-by-step thinking"
            },
            "playwright": {
                "command": "npx",
                "args": ["-y", "@cyanheads/playwright-mcp-server"],
                "env": {},
                "description": "Web automation and browser control"
            }
        }
        manager.create_config("basic-plus", servers)
        
    else:
        print(f"❌ Unknown command: {command}")

if __name__ == "__main__":
    main()
