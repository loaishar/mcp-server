#!/usr/bin/env python3
"""
Docker-Specific MCP Configuration Generator
Generates MCP client configurations that connect to the Docker-based unified MCP server.
"""

import json
import os
from datetime import datetime

def generate_docker_configs():
    """Generate Docker-specific MCP client configurations."""
    
    print("🐳 Generating Docker-specific MCP configurations...")
    
    # Ensure output directory exists
    os.makedirs("config/clients", exist_ok=True)
    
    # Docker-based unified MCP server configuration
    docker_server_config = {
        "command": "docker",
        "args": ["run", "-i", "--rm", "alpine/socat", "STDIO", "TCP:host.docker.internal:3333"],
        "env": {},
        "description": "Unified MCP server running in Docker container"
    }
    
    # Alternative: Direct connection to Docker container
    docker_direct_config = {
        "command": "docker",
        "args": ["exec", "-i", "unified-mcp-server", "python", "unified_mcp.py"],
        "env": {},
        "description": "Direct connection to Docker-based unified MCP server"
    }
    
    # Client configurations for Docker deployment
    clients = {
        "claude-desktop-docker": {
            "description": "Claude Desktop connecting to Docker-based MCP server",
            "servers": {
                "unified-mcp-docker": docker_server_config
            }
        },
        "cursor-docker": {
            "description": "Cursor connecting to Docker-based MCP server", 
            "servers": {
                "unified-mcp-docker": docker_server_config
            }
        },
        "windsurf-docker": {
            "description": "Windsurf connecting to Docker-based MCP server",
            "servers": {
                "unified-mcp-docker": docker_server_config
            }
        },
        "vs-copilot-docker": {
            "description": "VS Code Copilot connecting to Docker-based MCP server",
            "servers": {
                "unified-mcp-docker": docker_server_config
            }
        }
    }
    
    # Generate configuration files
    for client_name, client_config in clients.items():
        config = {
            "mcpServers": client_config["servers"],
            "_metadata": {
                "generated_from": "Docker deployment script",
                "generated_at": datetime.now().isoformat(),
                "client": client_name,
                "description": client_config["description"],
                "deployment_type": "docker",
                "server_endpoint": "http://localhost:3333"
            }
        }
        
        output_file = f"config/clients/{client_name}.json"
        with open(output_file, 'w') as f:
            json.dump(config, f, indent=2)
            
        print(f"   ✅ {output_file}")
    
    # Generate Docker Compose override for development
    compose_override = {
        "version": "3.8",
        "services": {
            "unified-mcp": {
                "volumes": [
                    "./src:/app/src:ro",
                    "./config:/app/config:ro",
                    "./.mcp.json:/app/.mcp.json:ro"
                ],
                "environment": [
                    "MCP_DEV_MODE=true",
                    "MCP_RELOAD=true"
                ]
            }
        }
    }
    
    with open("docker-compose.override.yml", 'w') as f:
        import yaml
        try:
            yaml.dump(compose_override, f, default_flow_style=False)
            print("   ✅ docker-compose.override.yml (development)")
        except ImportError:
            # Fallback to JSON if PyYAML not available
            json.dump(compose_override, f, indent=2)
            print("   ✅ docker-compose.override.yml (JSON format)")
    
    # Generate environment template for Docker
    env_template = """# =============================================================================
# MCP Configuration Management System - Docker Environment
# =============================================================================

# MCP Server Configuration
MCP_SERVER_HOST=0.0.0.0
MCP_SERVER_PORT=3333
MCP_SERVER_LOG_LEVEL=INFO

# API Keys (Required for full functionality)
GITHUB_PERSONAL_ACCESS_TOKEN=your_github_token_here
SUPABASE_ACCESS_TOKEN=your_supabase_token_here
FIGMA_API_KEY=your_figma_api_key_here
HYPERBROWSER_API_KEY=your_hyperbrowser_api_key_here

# Optional: Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/mcp_db

# Optional: Redis Configuration (for caching)
REDIS_URL=redis://localhost:6379

# Development Settings
MCP_DEV_MODE=false
MCP_RELOAD=false
MCP_DEBUG=false

# Security Settings
MCP_CORS_ORIGINS=http://localhost:3000,http://localhost:8080
MCP_MAX_CONNECTIONS=100
MCP_TIMEOUT=30

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_FILE=/app/logs/mcp_server.log
"""
    
    with open(".env.docker", 'w') as f:
        f.write(env_template)
        print("   ✅ .env.docker (environment template)")
    
    print("🎉 Docker-specific configurations generated successfully!")
    
    # Show usage instructions
    print("\n📋 Usage Instructions:")
    print("=" * 50)
    print("1. Configure environment:")
    print("   cp .env.docker .env")
    print("   # Edit .env with your API keys")
    print("")
    print("2. Start Docker deployment:")
    print("   docker-compose up -d")
    print("")
    print("3. Configure AI clients:")
    print("   # Claude Desktop")
    print("   cp config/clients/claude-desktop-docker.json %APPDATA%\\Claude\\claude_desktop_config.json")
    print("")
    print("   # Cursor")
    print("   cp config/clients/cursor-docker.json ~/.cursor/mcp.json")
    print("")
    print("   # Windsurf")
    print("   cp config/clients/windsurf-docker.json ~/.codeium/windsurf/mcp_config.json")
    print("")
    print("4. Verify deployment:")
    print("   curl http://localhost:3333/health")
    print("")
    print("5. Check logs:")
    print("   docker-compose logs -f unified-mcp")

def main():
    """Main entry point."""
    generate_docker_configs()

if __name__ == "__main__":
    main()
