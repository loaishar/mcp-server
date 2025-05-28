#!/bin/bash
# Docker Build Script for MCP Servers
# Supports multi-platform builds and local development

set -e

# Configuration
REGISTRY="${REGISTRY:-}"
TAG="${TAG:-latest}"
PLATFORMS="${PLATFORMS:-linux/amd64,linux/arm64}"
PUSH="${PUSH:-false}"
BUILD_ARGS="${BUILD_ARGS:-}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
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

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed or not in PATH"
        exit 1
    fi
    
    if ! docker buildx version &> /dev/null; then
        log_error "Docker Buildx is not available"
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

# Setup buildx
setup_buildx() {
    log_info "Setting up Docker Buildx..."
    
    # Create builder if it doesn't exist
    if ! docker buildx inspect mcp-builder &> /dev/null; then
        docker buildx create --name mcp-builder --use
        log_success "Created new buildx builder: mcp-builder"
    else
        docker buildx use mcp-builder
        log_info "Using existing buildx builder: mcp-builder"
    fi
    
    # Bootstrap the builder
    docker buildx inspect --bootstrap
}

# Build image
build_image() {
    local dockerfile=$1
    local image_name=$2
    local context=${3:-"."}
    
    log_info "Building $image_name using $dockerfile..."
    
    # Construct image tags
    local tags=""
    if [ -n "$REGISTRY" ]; then
        tags="$tags -t ${REGISTRY}${image_name}:${TAG}"
        tags="$tags -t ${REGISTRY}${image_name}:latest"
    else
        tags="$tags -t ${image_name}:${TAG}"
        tags="$tags -t ${image_name}:latest"
    fi
    
    # Build command
    local build_cmd="docker buildx build"
    build_cmd="$build_cmd --platform $PLATFORMS"
    build_cmd="$build_cmd --file $dockerfile"
    build_cmd="$build_cmd $tags"
    
    if [ "$PUSH" = "true" ]; then
        build_cmd="$build_cmd --push"
    else
        build_cmd="$build_cmd --load"
    fi
    
    if [ -n "$BUILD_ARGS" ]; then
        build_cmd="$build_cmd $BUILD_ARGS"
    fi
    
    build_cmd="$build_cmd $context"
    
    log_info "Executing: $build_cmd"
    eval $build_cmd
    
    log_success "Successfully built $image_name"
}

# Main build function
main() {
    log_info "Starting Docker build process..."
    
    # Change to script directory
    cd "$(dirname "$0")/.."
    
    check_prerequisites
    setup_buildx
    
    # Build unified MCP server
    build_image "Dockerfile" "unified-mcp"
    
    # Build Node.js MCP servers
    build_image "Dockerfile.nodejs" "mcp-nodejs"
    
    log_success "All images built successfully!"
    
    if [ "$PUSH" = "true" ]; then
        log_success "Images pushed to registry"
    else
        log_info "Images loaded locally. Use PUSH=true to push to registry"
    fi
    
    # Show built images
    log_info "Built images:"
    if [ -n "$REGISTRY" ]; then
        docker images | grep "${REGISTRY}" | head -10
    else
        docker images | grep -E "(unified-mcp|mcp-nodejs)" | head -10
    fi
}

# Help function
show_help() {
    cat << EOF
Docker Build Script for MCP Servers

Usage: $0 [OPTIONS]

Environment Variables:
  REGISTRY    Docker registry prefix (e.g., 'myregistry.com/')
  TAG         Image tag (default: latest)
  PLATFORMS   Target platforms (default: linux/amd64,linux/arm64)
  PUSH        Push to registry (default: false)
  BUILD_ARGS  Additional build arguments

Examples:
  # Build locally
  ./scripts/build-docker.sh

  # Build and push to registry
  REGISTRY=myregistry.com/ PUSH=true ./scripts/build-docker.sh

  # Build for specific platform
  PLATFORMS=linux/amd64 ./scripts/build-docker.sh

  # Build with custom tag
  TAG=v1.0.0 ./scripts/build-docker.sh

Options:
  -h, --help    Show this help message

EOF
}

# Parse command line arguments
case "${1:-}" in
    -h|--help)
        show_help
        exit 0
        ;;
    *)
        main "$@"
        ;;
esac
