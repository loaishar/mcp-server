#!/bin/bash
# Quick Start Script for Docker-based MCP Server Deployment
# This script automates the entire setup process

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
COMPOSE_FILE="$PROJECT_DIR/docker-compose.yml"
ENV_FILE="$PROJECT_DIR/.env"
ENV_EXAMPLE="$PROJECT_DIR/.env.example"

# Helper functions
print_header() {
    echo -e "${PURPLE}"
    echo "╔══════════════════════════════════════════════════════════════════════════════╗"
    echo "║                    🐳 MCP Server Docker Quick Start                          ║"
    echo "║                                                                              ║"
    echo "║  This script will set up and deploy your MCP servers in Docker containers   ║"
    echo "╚══════════════════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${CYAN}[STEP]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_step "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker Desktop or Docker Engine."
        echo "Visit: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    # Check Docker Compose
    if ! docker compose version &> /dev/null; then
        log_error "Docker Compose V2 is not available. Please update Docker."
        exit 1
    fi
    
    # Check Docker daemon
    if ! docker info &> /dev/null; then
        log_error "Docker daemon is not running. Please start Docker."
        exit 1
    fi
    
    log_success "All prerequisites are met"
}

# Setup environment
setup_environment() {
    log_step "Setting up environment configuration..."
    
    cd "$PROJECT_DIR"
    
    if [ ! -f "$ENV_FILE" ]; then
        if [ -f "$ENV_EXAMPLE" ]; then
            cp "$ENV_EXAMPLE" "$ENV_FILE"
            log_success "Created .env file from template"
        else
            log_warning ".env.example not found, creating basic .env file"
            cat > "$ENV_FILE" << EOF
# Basic MCP Server Configuration
REGISTRY=
TAG=latest
MCP_PORT=3333
LOG_LEVEL=INFO
COMPOSE_PROFILES=default
EOF
        fi
    else
        log_info ".env file already exists"
    fi
    
    # Prompt for API keys
    echo -e "${YELLOW}"
    echo "┌─────────────────────────────────────────────────────────────────────────────┐"
    echo "│                           API Key Configuration                             │"
    echo "│                                                                             │"
    echo "│  You can add API keys now or skip and add them later to the .env file      │"
    echo "└─────────────────────────────────────────────────────────────────────────────┘"
    echo -e "${NC}"
    
    read -p "Do you want to configure API keys now? (y/N): " configure_keys
    
    if [[ $configure_keys =~ ^[Yy]$ ]]; then
        configure_api_keys
    else
        log_info "Skipping API key configuration. You can add them later to .env file"
    fi
}

# Configure API keys
configure_api_keys() {
    echo -e "${CYAN}Configuring API keys...${NC}"
    
    # GitHub Token
    read -p "GitHub Token (optional): " github_token
    if [ -n "$github_token" ]; then
        if grep -q "GITHUB_TOKEN=" "$ENV_FILE"; then
            sed -i "s/GITHUB_TOKEN=.*/GITHUB_TOKEN=$github_token/" "$ENV_FILE"
        else
            echo "GITHUB_TOKEN=$github_token" >> "$ENV_FILE"
        fi
    fi
    
    # OpenAI API Key
    read -p "OpenAI API Key (optional): " openai_key
    if [ -n "$openai_key" ]; then
        if grep -q "OPENAI_API_KEY=" "$ENV_FILE"; then
            sed -i "s/OPENAI_API_KEY=.*/OPENAI_API_KEY=$openai_key/" "$ENV_FILE"
        else
            echo "OPENAI_API_KEY=$openai_key" >> "$ENV_FILE"
        fi
    fi
    
    # Anthropic API Key
    read -p "Anthropic API Key (optional): " anthropic_key
    if [ -n "$anthropic_key" ]; then
        if grep -q "ANTHROPIC_API_KEY=" "$ENV_FILE"; then
            sed -i "s/ANTHROPIC_API_KEY=.*/ANTHROPIC_API_KEY=$anthropic_key/" "$ENV_FILE"
        else
            echo "ANTHROPIC_API_KEY=$anthropic_key" >> "$ENV_FILE"
        fi
    fi
    
    log_success "API keys configured"
}

# Build or pull images
setup_images() {
    log_step "Setting up Docker images..."
    
    cd "$PROJECT_DIR"
    
    # Check if we should build locally or pull from registry
    if [ -f "Dockerfile" ] && [ -f "Dockerfile.nodejs" ]; then
        echo -e "${YELLOW}"
        echo "┌─────────────────────────────────────────────────────────────────────────────┐"
        echo "│                            Image Setup Options                             │"
        echo "│                                                                             │"
        echo "│  1. Build images locally (recommended for development)                     │"
        echo "│  2. Pull pre-built images from registry (faster)                          │"
        echo "└─────────────────────────────────────────────────────────────────────────────┘"
        echo -e "${NC}"
        
        read -p "Choose option (1/2) [1]: " image_option
        image_option=${image_option:-1}
        
        if [ "$image_option" = "1" ]; then
            log_info "Building images locally..."
            docker compose build
            log_success "Images built successfully"
        else
            log_info "Pulling pre-built images..."
            docker compose pull || {
                log_warning "Failed to pull images, falling back to local build"
                docker compose build
            }
        fi
    else
        log_info "Pulling images from registry..."
        docker compose pull
    fi
}

# Deploy services
deploy_services() {
    log_step "Deploying MCP services..."
    
    cd "$PROJECT_DIR"
    
    # Choose deployment profile
    echo -e "${YELLOW}"
    echo "┌─────────────────────────────────────────────────────────────────────────────┐"
    echo "│                          Deployment Profiles                               │"
    echo "│                                                                             │"
    echo "│  1. Basic (unified-mcp + mcp-nodejs) - Recommended                         │"
    echo "│  2. Full (includes Redis, Nginx) - Production ready                        │"
    echo "│  3. Development (with debugging and file watching)                         │"
    echo "└─────────────────────────────────────────────────────────────────────────────┘"
    echo -e "${NC}"
    
    read -p "Choose deployment profile (1/2/3) [1]: " profile_option
    profile_option=${profile_option:-1}
    
    case $profile_option in
        1)
            log_info "Starting basic deployment..."
            docker compose up -d unified-mcp mcp-nodejs
            ;;
        2)
            log_info "Starting full deployment..."
            COMPOSE_PROFILES=full docker compose up -d
            ;;
        3)
            log_info "Starting development deployment..."
            docker compose -f docker-compose.yml -f docker-compose.override.yml up -d
            ;;
        *)
            log_warning "Invalid option, using basic deployment"
            docker compose up -d unified-mcp mcp-nodejs
            ;;
    esac
    
    log_success "Services deployed successfully"
}

# Verify deployment
verify_deployment() {
    log_step "Verifying deployment..."
    
    # Wait for services to start
    log_info "Waiting for services to start..."
    sleep 10
    
    # Check unified MCP server
    if curl -f -s http://localhost:3333/health > /dev/null 2>&1; then
        log_success "Unified MCP server is healthy"
    else
        log_warning "Unified MCP server health check failed (this might be normal if no health endpoint exists)"
    fi
    
    # Check container status
    log_info "Container status:"
    docker compose ps
    
    # Show logs if there are issues
    failed_containers=$(docker compose ps --filter "status=exited" --format "table {{.Service}}" | tail -n +2)
    if [ -n "$failed_containers" ]; then
        log_warning "Some containers failed to start. Showing logs:"
        echo "$failed_containers" | while read -r container; do
            echo -e "${RED}Logs for $container:${NC}"
            docker compose logs --tail=20 "$container"
        done
    fi
}

# Show next steps
show_next_steps() {
    echo -e "${GREEN}"
    echo "╔══════════════════════════════════════════════════════════════════════════════╗"
    echo "║                            🎉 Deployment Complete!                           ║"
    echo "╚══════════════════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    echo -e "${CYAN}Your MCP servers are now running! Here's what you can do next:${NC}"
    echo ""
    echo -e "${YELLOW}📊 Monitor Services:${NC}"
    echo "  docker compose logs -f                    # View all logs"
    echo "  docker compose ps                         # Check service status"
    echo "  docker stats                              # Monitor resource usage"
    echo ""
    echo -e "${YELLOW}🔧 Configure AI Clients:${NC}"
    echo "  # Claude Desktop configuration example:"
    echo '  {
    "mcpServers": {
      "unified-mcp": {
        "command": "docker",
        "args": ["exec", "-i", "unified-mcp-server", "python", "src/unified_mcp.py"],
        "env": {}
      }
    }
  }'
    echo ""
    echo -e "${YELLOW}🛠️ Management Commands:${NC}"
    echo "  docker compose stop                       # Stop all services"
    echo "  docker compose restart                    # Restart all services"
    echo "  docker compose down                       # Stop and remove containers"
    echo "  docker compose pull && docker compose up -d  # Update to latest images"
    echo ""
    echo -e "${YELLOW}📚 Documentation:${NC}"
    echo "  cat DOCKER_DEPLOYMENT.md                  # Full deployment guide"
    echo "  cat .env                                   # Environment configuration"
    echo ""
    echo -e "${GREEN}🚀 Your MCP server stack is ready for use!${NC}"
}

# Main execution
main() {
    print_header
    
    check_prerequisites
    setup_environment
    setup_images
    deploy_services
    verify_deployment
    show_next_steps
    
    log_success "Quick start completed successfully!"
}

# Handle script interruption
trap 'log_error "Script interrupted"; exit 1' INT TERM

# Run main function
main "$@"
