# Docker Build Script for MCP Servers (PowerShell)
# Supports multi-platform builds and local development

param(
    [string]$Registry = $env:REGISTRY,
    [string]$Tag = $env:TAG,
    [string]$Platforms = $env:PLATFORMS,
    [switch]$Push = $env:PUSH -eq "true",
    [string]$BuildArgs = $env:BUILD_ARGS,
    [switch]$Help
)

# Set defaults
if (-not $Tag) { $Tag = "latest" }
if (-not $Platforms) { $Platforms = "linux/amd64,linux/arm64" }

# Helper functions
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    
    $colorMap = @{
        "Red" = "Red"
        "Green" = "Green"
        "Yellow" = "Yellow"
        "Blue" = "Blue"
        "White" = "White"
    }
    
    Write-Host $Message -ForegroundColor $colorMap[$Color]
}

function Log-Info {
    param([string]$Message)
    Write-ColorOutput "[INFO] $Message" "Blue"
}

function Log-Success {
    param([string]$Message)
    Write-ColorOutput "[SUCCESS] $Message" "Green"
}

function Log-Warning {
    param([string]$Message)
    Write-ColorOutput "[WARNING] $Message" "Yellow"
}

function Log-Error {
    param([string]$Message)
    Write-ColorOutput "[ERROR] $Message" "Red"
}

function Show-Help {
    @"
Docker Build Script for MCP Servers (PowerShell)

Usage: .\scripts\deploy\build-docker.ps1 [OPTIONS]

Parameters:
  -Registry    Docker registry prefix (e.g., 'myregistry.com/')
  -Tag         Image tag (default: latest)
  -Platforms   Target platforms (default: linux/amd64,linux/arm64)
  -Push        Push to registry (switch)
  -BuildArgs   Additional build arguments
  -Help        Show this help message

Environment Variables (alternative to parameters):
  REGISTRY, TAG, PLATFORMS, PUSH, BUILD_ARGS

Examples:
  # Build locally
  .\scripts\deploy\build-docker.ps1

  # Build and push to registry
  .\scripts\deploy\build-docker.ps1 -Registry "myregistry.com/" -Push

  # Build for specific platform
  .\scripts\deploy\build-docker.ps1 -Platforms "linux/amd64"

  # Build with custom tag
  .\scripts\deploy\build-docker.ps1 -Tag "v1.0.0"

"@
}

function Test-Prerequisites {
    Log-Info "Checking prerequisites..."
    
    # Check Docker
    try {
        $dockerVersion = docker --version
        Log-Info "Found Docker: $dockerVersion"
    }
    catch {
        Log-Error "Docker is not installed or not in PATH"
        exit 1
    }
    
    # Check Docker Buildx
    try {
        $buildxVersion = docker buildx version
        Log-Info "Found Docker Buildx: $buildxVersion"
    }
    catch {
        Log-Error "Docker Buildx is not available"
        exit 1
    }
    
    Log-Success "Prerequisites check passed"
}

function Initialize-Buildx {
    Log-Info "Setting up Docker Buildx..."
    
    # Check if builder exists
    $builderExists = docker buildx inspect mcp-builder 2>$null
    if ($LASTEXITCODE -ne 0) {
        Log-Info "Creating new buildx builder: mcp-builder"
        docker buildx create --name mcp-builder --use
        if ($LASTEXITCODE -ne 0) {
            Log-Error "Failed to create buildx builder"
            exit 1
        }
        Log-Success "Created new buildx builder: mcp-builder"
    }
    else {
        Log-Info "Using existing buildx builder: mcp-builder"
        docker buildx use mcp-builder
    }
    
    # Bootstrap the builder
    docker buildx inspect --bootstrap
    if ($LASTEXITCODE -ne 0) {
        Log-Error "Failed to bootstrap buildx builder"
        exit 1
    }
}

function Build-Image {
    param(
        [string]$Dockerfile,
        [string]$ImageName,
        [string]$Context = "."
    )
    
    Log-Info "Building $ImageName using $Dockerfile..."
    
    # Construct image tags
    $tags = @()
    if ($Registry) {
        $tags += "-t", "${Registry}${ImageName}:${Tag}"
        $tags += "-t", "${Registry}${ImageName}:latest"
    }
    else {
        $tags += "-t", "${ImageName}:${Tag}"
        $tags += "-t", "${ImageName}:latest"
    }
    
    # Build command arguments
    $buildArgs = @(
        "buildx", "build",
        "--platform", $Platforms,
        "--file", $Dockerfile
    )
    
    $buildArgs += $tags
    
    if ($Push) {
        $buildArgs += "--push"
    }
    else {
        $buildArgs += "--load"
    }
    
    if ($BuildArgs) {
        $buildArgs += $BuildArgs.Split(" ")
    }
    
    $buildArgs += $Context
    
    Log-Info "Executing: docker $($buildArgs -join ' ')"
    
    & docker @buildArgs
    if ($LASTEXITCODE -ne 0) {
        Log-Error "Failed to build $ImageName"
        exit 1
    }
    
    Log-Success "Successfully built $ImageName"
}

function Main {
    Log-Info "Starting Docker build process..."
    
    # Change to project root directory
    $scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
    $deployDir = Split-Path -Parent $scriptDir
    $projectDir = Split-Path -Parent $deployDir
    Set-Location $projectDir
    
    Test-Prerequisites
    Initialize-Buildx
    
    # Build unified MCP server
    Build-Image -Dockerfile "docker/Dockerfile" -ImageName "unified-mcp"
    
    # Build Node.js MCP servers
    Build-Image -Dockerfile "docker/Dockerfile.nodejs" -ImageName "mcp-nodejs"
    
    Log-Success "All images built successfully!"
    
    if ($Push) {
        Log-Success "Images pushed to registry"
    }
    else {
        Log-Info "Images loaded locally. Use -Push to push to registry"
    }
    
    # Show built images
    Log-Info "Built images:"
    if ($Registry) {
        docker images | Select-String $Registry | Select-Object -First 10
    }
    else {
        docker images | Select-String "(unified-mcp|mcp-nodejs)" | Select-Object -First 10
    }
}

# Main execution
if ($Help) {
    Show-Help
    exit 0
}

try {
    Main
}
catch {
    Log-Error "Build failed: $_"
    exit 1
}
