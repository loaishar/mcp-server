# Quick Start Script for Docker-based MCP Server Deployment (PowerShell)
# This script automates the entire setup process for Windows users

param(
    [switch]$SkipApiKeys,
    [string]$Profile = "basic",
    [switch]$Help
)

# Configuration
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectDir = Split-Path -Parent $ScriptDir
$ComposeFile = Join-Path $ProjectDir "docker-compose.yml"
$EnvFile = Join-Path $ProjectDir ".env"
$EnvExample = Join-Path $ProjectDir ".env.example"

# Helper functions
function Write-Header {
    Write-Host "╔══════════════════════════════════════════════════════════════════════════════╗" -ForegroundColor Magenta
    Write-Host "║                    🐳 MCP Server Docker Quick Start                          ║" -ForegroundColor Magenta
    Write-Host "║                                                                              ║" -ForegroundColor Magenta
    Write-Host "║  This script will set up and deploy your MCP servers in Docker containers   ║" -ForegroundColor Magenta
    Write-Host "╚══════════════════════════════════════════════════════════════════════════════╝" -ForegroundColor Magenta
}

function Write-Step {
    param([string]$Message)
    Write-Host "[STEP] $Message" -ForegroundColor Cyan
}

function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

function Show-Help {
    @"
Quick Start Script for Docker-based MCP Server Deployment

Usage: .\scripts\quick-start.ps1 [OPTIONS]

Parameters:
  -SkipApiKeys    Skip API key configuration
  -Profile        Deployment profile (basic, full, dev) [default: basic]
  -Help           Show this help message

Examples:
  .\scripts\quick-start.ps1                    # Interactive setup
  .\scripts\quick-start.ps1 -SkipApiKeys       # Skip API key setup
  .\scripts\quick-start.ps1 -Profile full      # Full deployment
  .\scripts\quick-start.ps1 -Profile dev       # Development mode

"@
}

function Test-Prerequisites {
    Write-Step "Checking prerequisites..."
    
    # Check Docker
    try {
        $dockerVersion = docker --version
        Write-Info "Found Docker: $dockerVersion"
    }
    catch {
        Write-Error "Docker is not installed. Please install Docker Desktop."
        Write-Host "Visit: https://docs.docker.com/desktop/install/windows-install/" -ForegroundColor Yellow
        exit 1
    }
    
    # Check Docker Compose
    try {
        $composeVersion = docker compose version
        Write-Info "Found Docker Compose: $composeVersion"
    }
    catch {
        Write-Error "Docker Compose V2 is not available. Please update Docker Desktop."
        exit 1
    }
    
    # Check Docker daemon
    try {
        docker info | Out-Null
        Write-Success "Docker daemon is running"
    }
    catch {
        Write-Error "Docker daemon is not running. Please start Docker Desktop."
        exit 1
    }
    
    Write-Success "All prerequisites are met"
}

function Initialize-Environment {
    Write-Step "Setting up environment configuration..."
    
    Set-Location $ProjectDir
    
    if (-not (Test-Path $EnvFile)) {
        if (Test-Path $EnvExample) {
            Copy-Item $EnvExample $EnvFile
            Write-Success "Created .env file from template"
        }
        else {
            Write-Warning ".env.example not found, creating basic .env file"
            @"
# Basic MCP Server Configuration
REGISTRY=
TAG=latest
MCP_PORT=3333
LOG_LEVEL=INFO
COMPOSE_PROFILES=default
"@ | Out-File -FilePath $EnvFile -Encoding UTF8
        }
    }
    else {
        Write-Info ".env file already exists"
    }
    
    if (-not $SkipApiKeys) {
        Write-Host "┌─────────────────────────────────────────────────────────────────────────────┐" -ForegroundColor Yellow
        Write-Host "│                           API Key Configuration                             │" -ForegroundColor Yellow
        Write-Host "│                                                                             │" -ForegroundColor Yellow
        Write-Host "│  You can add API keys now or skip and add them later to the .env file      │" -ForegroundColor Yellow
        Write-Host "└─────────────────────────────────────────────────────────────────────────────┘" -ForegroundColor Yellow
        
        $configureKeys = Read-Host "Do you want to configure API keys now? (y/N)"
        
        if ($configureKeys -match "^[Yy]$") {
            Set-ApiKeys
        }
        else {
            Write-Info "Skipping API key configuration. You can add them later to .env file"
        }
    }
}

function Set-ApiKeys {
    Write-Host "Configuring API keys..." -ForegroundColor Cyan
    
    # GitHub Token
    $githubToken = Read-Host "GitHub Token (optional)"
    if ($githubToken) {
        Update-EnvVariable "GITHUB_TOKEN" $githubToken
    }
    
    # OpenAI API Key
    $openaiKey = Read-Host "OpenAI API Key (optional)"
    if ($openaiKey) {
        Update-EnvVariable "OPENAI_API_KEY" $openaiKey
    }
    
    # Anthropic API Key
    $anthropicKey = Read-Host "Anthropic API Key (optional)"
    if ($anthropicKey) {
        Update-EnvVariable "ANTHROPIC_API_KEY" $anthropicKey
    }
    
    Write-Success "API keys configured"
}

function Update-EnvVariable {
    param(
        [string]$Key,
        [string]$Value
    )
    
    $envContent = Get-Content $EnvFile -Raw
    if ($envContent -match "$Key=.*") {
        $envContent = $envContent -replace "$Key=.*", "$Key=$Value"
    }
    else {
        $envContent += "`n$Key=$Value"
    }
    $envContent | Out-File -FilePath $EnvFile -Encoding UTF8 -NoNewline
}

function Initialize-Images {
    Write-Step "Setting up Docker images..."
    
    Set-Location $ProjectDir
    
    if ((Test-Path "Dockerfile") -and (Test-Path "Dockerfile.nodejs")) {
        Write-Host "┌─────────────────────────────────────────────────────────────────────────────┐" -ForegroundColor Yellow
        Write-Host "│                            Image Setup Options                             │" -ForegroundColor Yellow
        Write-Host "│                                                                             │" -ForegroundColor Yellow
        Write-Host "│  1. Build images locally (recommended for development)                     │" -ForegroundColor Yellow
        Write-Host "│  2. Pull pre-built images from registry (faster)                          │" -ForegroundColor Yellow
        Write-Host "└─────────────────────────────────────────────────────────────────────────────┘" -ForegroundColor Yellow
        
        $imageOption = Read-Host "Choose option (1/2) [1]"
        if (-not $imageOption) { $imageOption = "1" }
        
        if ($imageOption -eq "1") {
            Write-Info "Building images locally..."
            docker compose build
            if ($LASTEXITCODE -eq 0) {
                Write-Success "Images built successfully"
            }
            else {
                Write-Error "Failed to build images"
                exit 1
            }
        }
        else {
            Write-Info "Pulling pre-built images..."
            docker compose pull
            if ($LASTEXITCODE -ne 0) {
                Write-Warning "Failed to pull images, falling back to local build"
                docker compose build
            }
        }
    }
    else {
        Write-Info "Pulling images from registry..."
        docker compose pull
    }
}

function Start-Services {
    Write-Step "Deploying MCP services..."
    
    Set-Location $ProjectDir
    
    # Choose deployment profile if not specified
    if ($Profile -eq "basic") {
        Write-Host "┌─────────────────────────────────────────────────────────────────────────────┐" -ForegroundColor Yellow
        Write-Host "│                          Deployment Profiles                               │" -ForegroundColor Yellow
        Write-Host "│                                                                             │" -ForegroundColor Yellow
        Write-Host "│  1. Basic (unified-mcp + mcp-nodejs) - Recommended                         │" -ForegroundColor Yellow
        Write-Host "│  2. Full (includes Redis, Nginx) - Production ready                        │" -ForegroundColor Yellow
        Write-Host "│  3. Development (with debugging and file watching)                         │" -ForegroundColor Yellow
        Write-Host "└─────────────────────────────────────────────────────────────────────────────┘" -ForegroundColor Yellow
        
        $profileOption = Read-Host "Choose deployment profile (1/2/3) [1]"
        if (-not $profileOption) { $profileOption = "1" }
        
        switch ($profileOption) {
            "1" { $Profile = "basic" }
            "2" { $Profile = "full" }
            "3" { $Profile = "dev" }
            default { $Profile = "basic" }
        }
    }
    
    switch ($Profile) {
        "basic" {
            Write-Info "Starting basic deployment..."
            docker compose up -d unified-mcp mcp-nodejs
        }
        "full" {
            Write-Info "Starting full deployment..."
            $env:COMPOSE_PROFILES = "full"
            docker compose up -d
        }
        "dev" {
            Write-Info "Starting development deployment..."
            docker compose -f docker-compose.yml -f docker-compose.override.yml up -d
        }
    }
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Services deployed successfully"
    }
    else {
        Write-Error "Failed to deploy services"
        exit 1
    }
}

function Test-Deployment {
    Write-Step "Verifying deployment..."
    
    # Wait for services to start
    Write-Info "Waiting for services to start..."
    Start-Sleep -Seconds 10
    
    # Check unified MCP server
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:3333/health" -TimeoutSec 5 -ErrorAction Stop
        Write-Success "Unified MCP server is healthy"
    }
    catch {
        Write-Warning "Unified MCP server health check failed (this might be normal if no health endpoint exists)"
    }
    
    # Check container status
    Write-Info "Container status:"
    docker compose ps
    
    # Show logs if there are issues
    $failedContainers = docker compose ps --filter "status=exited" --format "table {{.Service}}" | Select-Object -Skip 1
    if ($failedContainers) {
        Write-Warning "Some containers failed to start. Showing logs:"
        foreach ($container in $failedContainers) {
            Write-Host "Logs for $container:" -ForegroundColor Red
            docker compose logs --tail=20 $container
        }
    }
}

function Show-NextSteps {
    Write-Host "╔══════════════════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║                            🎉 Deployment Complete!                           ║" -ForegroundColor Green
    Write-Host "╚══════════════════════════════════════════════════════════════════════════════╝" -ForegroundColor Green
    
    Write-Host "Your MCP servers are now running! Here's what you can do next:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "📊 Monitor Services:" -ForegroundColor Yellow
    Write-Host "  docker compose logs -f                    # View all logs"
    Write-Host "  docker compose ps                         # Check service status"
    Write-Host "  docker stats                              # Monitor resource usage"
    Write-Host ""
    Write-Host "🔧 Configure AI Clients:" -ForegroundColor Yellow
    Write-Host "  # Claude Desktop configuration example:"
    Write-Host '  {
    "mcpServers": {
      "unified-mcp": {
        "command": "docker",
        "args": ["exec", "-i", "unified-mcp-server", "python", "src/unified_mcp.py"],
        "env": {}
      }
    }
  }'
    Write-Host ""
    Write-Host "🛠️ Management Commands:" -ForegroundColor Yellow
    Write-Host "  docker compose stop                       # Stop all services"
    Write-Host "  docker compose restart                    # Restart all services"
    Write-Host "  docker compose down                       # Stop and remove containers"
    Write-Host "  docker compose pull; docker compose up -d # Update to latest images"
    Write-Host ""
    Write-Host "📚 Documentation:" -ForegroundColor Yellow
    Write-Host "  Get-Content DOCKER_DEPLOYMENT.md          # Full deployment guide"
    Write-Host "  Get-Content .env                          # Environment configuration"
    Write-Host ""
    Write-Host "🚀 Your MCP server stack is ready for use!" -ForegroundColor Green
}

function Main {
    Write-Header
    
    Test-Prerequisites
    Initialize-Environment
    Initialize-Images
    Start-Services
    Test-Deployment
    Show-NextSteps
    
    Write-Success "Quick start completed successfully!"
}

# Handle script parameters
if ($Help) {
    Show-Help
    exit 0
}

try {
    Main
}
catch {
    Write-Error "Script failed: $_"
    exit 1
}
