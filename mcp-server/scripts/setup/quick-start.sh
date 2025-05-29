#!/bin/bash
# Quick Start Script for Unified MCP Server v2
# Fully MCP-compliant implementation with enhanced features

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo -e "${BLUE}🚀 Unified MCP Server v2 - Quick Start${NC}"
echo "============================================"

# Function to check dependencies
check_dependencies() {
    echo -e "\n${YELLOW}Checking dependencies...${NC}"
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Python 3 not found. Please install Python 3.10+${NC}"
        exit 1
    fi
    
    # Check Python version
    PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    if [ "$(echo "$PYTHON_VERSION < 3.10" | bc)" -eq 1 ]; then
        echo -e "${RED}❌ Python $PYTHON_VERSION found. Python 3.10+ required${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Python $PYTHON_VERSION${NC}"
    
    # Check pip
    if ! python3 -m pip --version &> /dev/null; then
        echo -e "${RED}❌ pip not found. Installing pip...${NC}"
        curl https://bootstrap.pypa.io/get-pip.py | python3
    fi
}

# Function to install Python dependencies
install_dependencies() {
    echo -e "\n${YELLOW}Installing Python dependencies...${NC}"
    
    cd "$PROJECT_ROOT"
    
    # Install requirements
    python3 -m pip install -r requirements.txt
    
    # Install v2 specific dependencies
    python3 -m pip install aiohttp python-dotenv
    
    # Install test dependencies (optional)
    python3 -m pip install pytest pytest-asyncio
    
    echo -e "${GREEN}✅ Dependencies installed${NC}"
}

# Function to run tests
run_tests() {
    echo -e "\n${YELLOW}Running MCP compliance tests...${NC}"
    
    cd "$PROJECT_ROOT"
    
    if python3 -m pytest tests/test_mcp_compliance.py -v --tb=short; then
        echo -e "${GREEN}✅ All tests passed${NC}"
    else
        echo -e "${YELLOW}⚠️  Some tests failed, but continuing...${NC}"
    fi
}

# Function to start server
start_server() {
    MODE=${1:-stdio}
    
    echo -e "\n${YELLOW}Starting Unified MCP Server v2 in $MODE mode...${NC}"
    
    cd "$PROJECT_ROOT"
    
    case $MODE in
        stdio)
            echo -e "${BLUE}Starting STDIO mode (for Claude Desktop)...${NC}"
            echo -e "${YELLOW}Press Ctrl+C to stop${NC}\n"
            python3 src/server/unified_mcp_v2.py --transport stdio
            ;;
        http)
            echo -e "${BLUE}Starting HTTP/SSE mode (for remote access)...${NC}"
            echo -e "${GREEN}Server will be available at:${NC}"
            echo -e "  - JSON-RPC: http://localhost:3333/rpc"
            echo -e "  - SSE: http://localhost:3333/sse"
            echo -e "  - Health: http://localhost:3333/health"
            echo -e "${YELLOW}Press Ctrl+C to stop${NC}\n"
            python3 src/server/unified_mcp_v2.py --transport http --port 3333
            ;;
        docker)
            echo -e "${BLUE}Starting with Docker...${NC}"
            docker-compose -f docker/docker-compose.yml up
            ;;
        test)
            echo -e "${BLUE}Running in test mode...${NC}"
            python3 src/client/mcp_client.py python3 src/server/unified_mcp_v2.py --test
            ;;
        *)
            echo -e "${RED}Unknown mode: $MODE${NC}"
            echo "Usage: $0 [stdio|http|docker|test]"
            exit 1
            ;;
    esac
}

# Main menu
show_menu() {
    echo -e "\n${BLUE}Select startup mode:${NC}"
    echo "1) STDIO mode (for Claude Desktop)"
    echo "2) HTTP/SSE mode (for remote access)"
    echo "3) Docker mode (production)"
    echo "4) Test mode (run basic tests)"
    echo "5) Install dependencies only"
    echo "6) Run compliance tests"
    echo "7) Exit"
    
    read -p "Enter your choice [1-7]: " choice
    
    case $choice in
        1) MODE="stdio" ;;
        2) MODE="http" ;;
        3) MODE="docker" ;;
        4) MODE="test" ;;
        5) 
            check_dependencies
            install_dependencies
            exit 0
            ;;
        6)
            check_dependencies
            run_tests
            exit 0
            ;;
        7) exit 0 ;;
        *) 
            echo -e "${RED}Invalid choice${NC}"
            show_menu
            ;;
    esac
}

# Parse command line arguments
if [ $# -eq 0 ]; then
    # No arguments, show menu
    show_menu
else
    MODE=$1
fi

# Check and install dependencies
check_dependencies

# Check if dependencies are installed
if ! python3 -c "import aiohttp" 2>/dev/null; then
    install_dependencies
fi

# Start the server
start_server $MODE