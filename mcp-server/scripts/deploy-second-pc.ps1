#!/usr/bin/env pwsh
# =============================================================================
# Deploy MCP Configuration Management System to Second PC
# =============================================================================

param(
    [string]$Mode = "docker",  # "docker" or "direct"
    [switch]$Help
)

if ($Help) {
    Write-Host @"
🚀 Deploy MCP Configuration Management System to Second PC

Usage: .\scripts\deploy-second-pc.ps1 [-Mode <docker|direct>] [-Help]

Modes:
  docker  - Deploy using Docker (recommended for second PC)
  direct  - Deploy direct configuration sync (for development)

Examples:
  .\scripts\deploy-second-pc.ps1 -Mode docker
  .\scripts\deploy-second-pc.ps1 -Mode direct

"@
    exit 0
}

Write-Host "🚀 Deploying MCP Configuration Management System" -ForegroundColor Green
Write-Host "Mode: $Mode" -ForegroundColor Cyan

# =============================================================================
# Docker Deployment (Recommended for Second PC)
# =============================================================================
if ($Mode -eq "docker") {
    Write-Host "`n🐳 Docker Deployment Mode" -ForegroundColor Yellow
    
    # Check Docker
    Write-Host "📋 Checking Docker installation..."
    try {
        $dockerVersion = docker --version
        Write-Host "✅ Docker found: $dockerVersion" -ForegroundColor Green
    } catch {
        Write-Host "❌ Docker not found! Please install Docker Desktop first." -ForegroundColor Red
        exit 1
    }
    
    # Check Docker Compose
    try {
        $composeVersion = docker-compose --version
        Write-Host "✅ Docker Compose found: $composeVersion" -ForegroundColor Green
    } catch {
        Write-Host "❌ Docker Compose not found! Please install Docker Compose." -ForegroundColor Red
        exit 1
    }
    
    # Create environment file if not exists
    if (-not (Test-Path ".env")) {
        Write-Host "📝 Creating environment file..."
        Copy-Item ".env.example" ".env" -Force
        Write-Host "⚠️  Please edit .env file with your API keys before continuing!" -ForegroundColor Yellow
        Write-Host "   Required: GITHUB_PERSONAL_ACCESS_TOKEN, SUPABASE_ACCESS_TOKEN, etc." -ForegroundColor Yellow
        
        $continue = Read-Host "Press Enter when you've configured .env file, or 'q' to quit"
        if ($continue -eq 'q') {
            Write-Host "❌ Deployment cancelled." -ForegroundColor Red
            exit 1
        }
    }
    
    # Build and start Docker containers
    Write-Host "`n🔨 Building Docker image..."
    docker-compose build
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Docker build failed!" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "🚀 Starting Docker containers..."
    docker-compose up -d
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Docker startup failed!" -ForegroundColor Red
        exit 1
    }
    
    # Wait for service to be ready
    Write-Host "⏳ Waiting for MCP server to be ready..."
    $maxAttempts = 30
    $attempt = 0
    
    do {
        Start-Sleep -Seconds 2
        $attempt++
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:3333/health" -TimeoutSec 5 -ErrorAction SilentlyContinue
            if ($response.StatusCode -eq 200) {
                Write-Host "✅ MCP server is ready!" -ForegroundColor Green
                break
            }
        } catch {
            # Continue waiting
        }
        
        if ($attempt -ge $maxAttempts) {
            Write-Host "❌ MCP server failed to start within timeout!" -ForegroundColor Red
            Write-Host "Check logs with: docker-compose logs unified-mcp" -ForegroundColor Yellow
            exit 1
        }
        
        Write-Host "." -NoNewline
    } while ($true)
    
    # Configure AI clients for Docker deployment
    Write-Host "`n📱 Configuring AI clients for Docker deployment..."
    
    # Generate Docker-specific client configurations
    python scripts/generate-docker-configs.py
    
    # Deploy to Claude Desktop
    $claudeConfigPath = "$env:APPDATA\Claude\claude_desktop_config.json"
    Copy-Item "config\clients\claude-desktop-docker.json" $claudeConfigPath -Force
    Write-Host "✅ Claude Desktop configured for Docker deployment" -ForegroundColor Green
    
    # Copy other client configs
    Write-Host "📋 Other client configurations available in config/clients/:"
    Get-ChildItem "config\clients\*-docker.json" | ForEach-Object {
        Write-Host "   - $($_.Name)" -ForegroundColor Cyan
    }
    
    Write-Host "`n🎉 Docker deployment complete!" -ForegroundColor Green
    Write-Host @"
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
   - Cursor: Copy config\clients\cursor-docker.json to ~/.cursor/mcp.json
   - Windsurf: Copy config\clients\windsurf-docker.json to ~/.codeium/windsurf/mcp_config.json

"@ -ForegroundColor Cyan
}

# =============================================================================
# Direct Configuration Sync (For Development)
# =============================================================================
elseif ($Mode -eq "direct") {
    Write-Host "`n🔗 Direct Configuration Sync Mode" -ForegroundColor Yellow
    
    # Check Python
    Write-Host "📋 Checking Python installation..."
    try {
        $pythonVersion = python --version
        Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
    } catch {
        Write-Host "❌ Python not found! Please install Python 3.11+." -ForegroundColor Red
        exit 1
    }
    
    # Install dependencies
    Write-Host "📦 Installing Python dependencies..."
    pip install -r requirements.txt
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to install dependencies!" -ForegroundColor Red
        exit 1
    }
    
    # Generate configurations
    Write-Host "⚙️ Generating MCP configurations..."
    python scripts/generate-mcp-configs.py
    
    # Deploy to Claude Desktop
    Write-Host "🚀 Deploying master configuration to Claude Desktop..."
    python scripts/manage-mcp.py deploy
    
    # Start unified MCP server for other clients
    Write-Host "🔧 Starting unified MCP server for other clients..."
    Write-Host "   Run in separate terminal: python src/unified_mcp.py" -ForegroundColor Yellow
    
    Write-Host "`n🎉 Direct deployment complete!" -ForegroundColor Green
    Write-Host @"
📊 Configuration Status:
   - Claude Desktop: 13 direct MCP servers
   - Other clients: 1 unified MCP server (bridge)
   - Master config: config/master-mcp-config.json

🔧 Management Commands:
   - Status: python scripts/manage-mcp.py status
   - Deploy: python scripts/manage-mcp.py deploy
   - Test:   python tests/test_mcp_connection.py

📱 AI Client Setup:
   - Claude Desktop: Already configured
   - Cursor: Copy config\clients\cursor.json to ~/.cursor/mcp.json
   - Windsurf: Copy config\clients\windsurf.json to ~/.codeium/windsurf/mcp_config.json

"@ -ForegroundColor Cyan
}

else {
    Write-Host "❌ Invalid mode: $Mode" -ForegroundColor Red
    Write-Host "Use 'docker' or 'direct'. Run with -Help for more information." -ForegroundColor Yellow
    exit 1
}

Write-Host "`n✨ Deployment complete! Restart your AI tools to apply changes." -ForegroundColor Green
