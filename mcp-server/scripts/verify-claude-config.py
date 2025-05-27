#!/usr/bin/env python3
"""
Verify Claude Desktop MCP Configuration
"""

import json
import os
import sys

def verify_claude_config():
    """Verify Claude Desktop has all 13 MCP servers configured."""
    
    # Get Claude Desktop config path
    appdata = os.environ.get('APPDATA')
    if not appdata:
        print("❌ APPDATA environment variable not found!")
        return False
        
    config_path = os.path.join(appdata, 'Claude', 'claude_desktop_config.json')
    
    print("🔍 Verifying Claude Desktop MCP Configuration...")
    print(f"📁 Config path: {config_path}")
    
    # Check if file exists
    if not os.path.exists(config_path):
        print("❌ Claude Desktop configuration file not found!")
        print("   Run: python scripts/manage-mcp.py deploy")
        return False
    
    # Load configuration
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
    except Exception as e:
        print(f"❌ Failed to load configuration: {e}")
        return False
    
    # Check structure
    if 'mcpServers' not in config:
        print("❌ Configuration missing 'mcpServers' section!")
        return False
    
    servers = config['mcpServers']
    server_names = list(servers.keys())
    server_count = len(server_names)
    
    print(f"📊 Found {server_count} MCP servers in Claude Desktop:")
    
    # Expected servers for master configuration
    expected_servers = [
        'unified-mcp',
        'playwright-vision', 
        'git',
        'memory',
        'sequential-thinking',
        'playwright',
        'puppeteer',
        'browser-tools',
        'neon',
        'supabase',
        'github',
        'figma',
        'hyperbrowser'
    ]
    
    # List all servers
    for i, server_name in enumerate(server_names, 1):
        status = "✅" if server_name in expected_servers else "⚠️"
        print(f"   {i:2d}. {status} {server_name}")
        
        # Check server configuration
        server_config = servers[server_name]
        if 'command' not in server_config:
            print(f"      ❌ Missing 'command' for {server_name}")
        if 'args' not in server_config:
            print(f"      ❌ Missing 'args' for {server_name}")
    
    # Check if we have all expected servers
    missing_servers = [s for s in expected_servers if s not in server_names]
    extra_servers = [s for s in server_names if s not in expected_servers]
    
    print(f"\n📈 Configuration Analysis:")
    print(f"   Expected servers: {len(expected_servers)}")
    print(f"   Found servers: {server_count}")
    
    if missing_servers:
        print(f"   ❌ Missing servers: {', '.join(missing_servers)}")
    
    if extra_servers:
        print(f"   ⚠️  Extra servers: {', '.join(extra_servers)}")
    
    # Overall status
    if server_count >= 13 and not missing_servers:
        print(f"\n🎉 SUCCESS: Claude Desktop has all {server_count} MCP servers!")
        print("   This is the MASTER configuration with direct connections.")
        print("   Other AI clients inherit from this configuration.")
        return True
    elif server_count == 2 and 'unified-mcp' in server_names and 'playwright-vision' in server_names:
        print(f"\n⚠️  LEGACY MODE: Claude Desktop has only 2 servers.")
        print("   This is the old configuration. Run deployment to upgrade:")
        print("   python scripts/manage-mcp.py deploy")
        return False
    else:
        print(f"\n❌ INCOMPLETE: Claude Desktop has {server_count} servers but should have 13.")
        print("   Run deployment to fix:")
        print("   python scripts/manage-mcp.py deploy")
        return False

def main():
    """Main entry point."""
    success = verify_claude_config()
    
    if success:
        print("\n✨ Claude Desktop is properly configured as the MASTER!")
        print("   Restart Claude Desktop if you don't see all servers in the UI.")
    else:
        print("\n🔧 Configuration needs to be fixed.")
        print("   Run: python scripts/manage-mcp.py deploy")
        print("   Then restart Claude Desktop.")
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
