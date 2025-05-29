#!/bin/bash
# =============================================================================
# Deploy MCP Configuration Management System to Second PC (Linux/macOS)
# =============================================================================

set -e

MODE="docker"
HELP=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        docker|direct)
            MODE="$1"
            shift
            ;;
        --help|-h)
            HELP=true
            shift
            ;;
        *)
            echo "❌ Unknown option: $1"
            echo "Usage: $0 [docker|direct] [--help]"
            exit 1
            ;;
    esac
done

if [ "$HELP" = true ]; then
    cat << 'EOF'
🚀 Deploy MCP Configuration Management System to Second PC

Usage: ./scripts/deploy-second-pc.sh [docker|direct] [--help]

Modes:
  docker  - Deploy using Docker (recommended for second PC)
  direct  - Deploy direct configuration sync (for development)

Examples:
  ./scripts/deploy-second-pc.sh docker
  ./scripts/deploy-second-pc.sh direct

EOF
    exit 0
fi

echo "🚀 Deploying MCP Configuration Management System"
echo "Mode: $MODE"

# =============================================================================
# Docker Deployment (Recommended for Second PC)
# =============================================================================
if [ "$MODE" = "docker" ]; then
    echo ""
    echo "🐳 Docker Deployment Mode"
    
    # Check Docker
    echo "📋 Checking Docker installation..."
    if command -v docker &> /dev/null; then
        DOCKER_VERSION=$(docker --version)
        echo "✅ Docker found: $DOCKER_VERSION"
    else
        echo "❌ Docker not found! Please install Docker first."
        exit 1
    fi
    
    # Check Docker Compose
    if command -v docker-compose &> /dev/null; then
        COMPOSE_VERSION=$(docker-compose --version)
        echo "✅ Docker Compose found: $COMPOSE_VERSION"
    else
        echo "❌ Docker Compose not found! Please install Docker Compose."
        exit 1
    fi
    
    # Create environment file if not exists
    if [ ! -f ".env" ]; then
        echo "📝 Creating environment file..."
        cp ".env.example" ".env"
        echo "⚠️  Please edit .env file with your API keys before continuing!"
        echo "   Required: GITHUB_PERSONAL_ACCESS_TOKEN, SUPABASE_ACCESS_TOKEN, etc."
        
        read -p "Press Enter when you've configured .env file, or 'q' to quit: " continue
        if [ "$continue" = "q" ]; then
            echo "❌ Deployment cancelled."
            exit 1
        fi
    fi
    
    # Build and start Docker containers
    echo ""
    echo "🔨 Building Docker image..."
    docker-compose build
    
    echo "🚀 Starting Docker containers..."
    docker-compose up -d
    
    # Wait for service to be ready
    echo "⏳ Waiting for MCP server to be ready..."
    MAX_ATTEMPTS=30
    ATTEMPT=0
    
    while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
        sleep 2
        ATTEMPT=$((ATTEMPT + 1))
        
        if curl -f http://localhost:3333/health &> /dev/null; then
            echo "✅ MCP server is ready!"
            break
        fi
        
        if [ $ATTEMPT -ge $MAX_ATTEMPTS ]; then
            echo "❌ MCP server failed to start within timeout!"
            echo "Check logs with: docker-compose logs unified-mcp"
            exit 1
        fi
        
        echo -n "."
    done
    
    # Configure AI clients for Docker deployment
    echo ""
    echo "📱 Configuring AI clients for Docker deployment..."
    
    # Generate Docker-specific client configurations
    python3 scripts/generate-docker-configs.py
    
    # Deploy to Claude Desktop (Linux/macOS path)
    CLAUDE_CONFIG_DIR="$HOME/.config/Claude"
    mkdir -p "$CLAUDE_CONFIG_DIR"
    cp "config/clients/claude-desktop-docker.json" "$CLAUDE_CONFIG_DIR/claude_desktop_config.json"
    echo "✅ Claude Desktop configured for Docker deployment"
    
    # Show other client configs
    echo "📋 Other client configurations available in config/clients/:"
    ls config/clients/*-docker.json | sed 's/^/   - /'
    
    echo ""
    echo "🎉 Docker deployment complete!"
    cat << 'EOF'
📊 Service Status:
   - MCP Server: http://localhost:3333/health
   - Docker Container: unified-mcp-server
   - Logs: docker-compose logs -f unified-mcp

🔧 Management Commands:
   - Stop:    docker-compose down
   - Restart: docker-compose restart
   - Logs:    docker-compose logs -f
   - Status:  docker-compose ps

📱 AI Client Setup:
   - Claude Desktop: Already configured
   - Cursor: Copy config/clients/cursor-docker.json to ~/.cursor/mcp.json
   - Windsurf: Copy config/clients/windsurf-docker.json to ~/.codeium/windsurf/mcp_config.json

EOF

# =============================================================================
# Direct Configuration Sync (For Development)
# =============================================================================
elif [ "$MODE" = "direct" ]; then
    echo ""
    echo "🔗 Direct Configuration Sync Mode"
    
    # Check Python
    echo "📋 Checking Python installation..."
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version)
        echo "✅ Python found: $PYTHON_VERSION"
    else
        echo "❌ Python not found! Please install Python 3.11+."
        exit 1
    fi
    
    # Install dependencies
    echo "📦 Installing Python dependencies..."
    pip3 install -r requirements.txt
    
    # Generate configurations
    echo "⚙️ Generating MCP configurations..."
    python3 scripts/generate-mcp-configs.py
    
    # Deploy to Claude Desktop
    echo "🚀 Deploying master configuration to Claude Desktop..."
    python3 scripts/manage-mcp.py deploy
    
    # Start unified MCP server for other clients
    echo "🔧 Starting unified MCP server for other clients..."
    echo "   Run in separate terminal: python3 src/unified_mcp.py"
    
    echo ""
    echo "🎉 Direct deployment complete!"
    cat << 'EOF'
📊 Configuration Status:
   - Claude Desktop: 13 direct MCP servers
   - Other clients: 1 unified MCP server (bridge)
   - Master config: config/master-mcp-config.json

🔧 Management Commands:
   - Status: python3 scripts/manage-mcp.py status
   - Deploy: python3 scripts/manage-mcp.py deploy
   - Test:   python3 tests/test_mcp_connection.py

📱 AI Client Setup:
   - Claude Desktop: Already configured
   - Cursor: Copy config/clients/cursor.json to ~/.cursor/mcp.json
   - Windsurf: Copy config/clients/windsurf.json to ~/.codeium/windsurf/mcp_config.json

EOF

else
    echo "❌ Invalid mode: $MODE"
    echo "Use 'docker' or 'direct'. Run with --help for more information."
    exit 1
fi

echo ""
echo "✨ Deployment complete! Restart your AI tools to apply changes."
