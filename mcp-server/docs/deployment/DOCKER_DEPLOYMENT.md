# 🐳 Docker-Based MCP Server Deployment Guide

## 🚀 Quick Start (1-Minute Deployment)

### Prerequisites
- **Docker Desktop** (Windows/macOS) or **Docker Engine** (Linux) ≥ 24.0
- **Docker Compose** V2
- **Git**

### Instant Deployment
```bash
# 1. Clone repository
git clone https://github.com/loaishar/mcp-server.git
cd mcp-server/mcp-server

# 2. Configure environment
cp .env.example .env
# Edit .env with your API keys (optional for basic functionality)

# 3. Start all services
docker compose up -d

# 4. Verify deployment
curl http://localhost:3333/health
```

**🎉 That's it! Your MCP servers are now running in Docker containers.**

---

## 📋 Architecture Overview

### Container Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                    MCP Docker Stack                         │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐  │
│  │   unified-mcp   │  │   mcp-nodejs    │  │    redis    │  │
│  │   (Python)      │  │   (Node.js)     │  │  (Optional) │  │
│  │   Port: 3333    │  │   Ports: 9323+  │  │ Port: 6379  │  │
│  └─────────────────┘  └─────────────────┘  └─────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Services Included

| Service | Description | Ports | Image Size |
|---------|-------------|-------|------------|
| **unified-mcp** | Main Python MCP server | 3333 | ~150MB |
| **mcp-nodejs** | Node.js MCP servers (Playwright, Git, etc.) | 9229, 9323-9325 | ~800MB |
| **redis** | Caching and session storage (optional) | 6379 | ~15MB |
| **nginx** | Reverse proxy (optional) | 80, 443 | ~25MB |

---

## 🛠️ Deployment Options

### Option 1: Basic Deployment (Recommended)
```bash
# Start core services only
docker compose up -d unified-mcp mcp-nodejs
```

### Option 2: Full Stack Deployment
```bash
# Start all services including Redis and Nginx
COMPOSE_PROFILES=full docker compose up -d
```

### Option 3: Development Mode
```bash
# Start with development overrides
docker compose -f docker-compose.yml -f docker-compose.override.yml up -d
```

---

## ⚙️ Configuration

### Environment Variables
Copy `.env.example` to `.env` and configure:

```bash
# Registry settings
REGISTRY=your-registry.com/
TAG=latest

# MCP server settings
MCP_PORT=3333
LOG_LEVEL=INFO

# API keys (add your own)
GITHUB_TOKEN=your_github_token
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
```

### Port Configuration
Default ports can be changed in `.env`:

```bash
# External ports (change if conflicts exist)
UNIFIED_MCP_PORT=3333
PLAYWRIGHT_VISION_PORT=9323
GIT_SERVER_PORT=9324
MEMORY_SERVER_PORT=9325
REDIS_PORT=6379
```

---

## 🔧 Client Configuration

### Claude Desktop
```json
{
  "mcpServers": {
    "unified-mcp": {
      "command": "docker",
      "args": ["exec", "-i", "unified-mcp-server", "python", "src/unified_mcp.py"],
      "env": {},
      "description": "Docker-based unified MCP server"
    }
  }
}
```

### Alternative: Direct Connection
```json
{
  "mcpServers": {
    "unified-mcp": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "--network", "mcp-network", "unified-mcp:latest"],
      "env": {},
      "description": "Direct Docker connection"
    }
  }
}
```

---

## 🚀 Multi-Platform Builds

### Local Multi-Platform Build
```bash
# Build for multiple architectures
./scripts/build-docker.sh
# or
PLATFORMS=linux/amd64,linux/arm64 ./scripts/build-docker.sh
```

### Push to Registry
```bash
# Build and push to your registry
REGISTRY=myregistry.com/ PUSH=true ./scripts/build-docker.sh
```

---

## 📊 Monitoring and Health Checks

### Health Check Endpoints
```bash
# Check unified MCP server
curl http://localhost:3333/health

# Check Node.js services
curl http://localhost:9323/health

# Check Redis (if enabled)
docker exec mcp-redis redis-cli ping
```

### View Logs
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f unified-mcp

# Last 100 lines
docker compose logs --tail=100 unified-mcp
```

### Resource Usage
```bash
# Container stats
docker stats

# Detailed resource usage
docker compose top
```

---

## 🔒 Security Best Practices

### Container Security
- ✅ **Non-root users**: All containers run as non-root (UID 1000/1001)
- ✅ **Minimal base images**: Using slim/alpine variants
- ✅ **Multi-stage builds**: Separate build and runtime stages
- ✅ **Read-only filesystems**: Where possible
- ✅ **Resource limits**: CPU and memory constraints

### Network Security
```yaml
# Custom network isolation
networks:
  mcp-network:
    driver: bridge
    internal: true  # No external access
```

### Secrets Management
```bash
# Use Docker secrets for production
echo "your_api_key" | docker secret create github_token -
```

---

## 🔄 CI/CD Pipeline

### GitHub Actions
The repository includes automated CI/CD:

1. **Multi-platform builds** on every tag
2. **Security scanning** with Trivy
3. **Push to multiple registries** (Docker Hub + GHCR)
4. **Automated testing** and validation

### Manual Release
```bash
# Tag and push for automated build
git tag v1.0.0
git push origin v1.0.0

# Images will be built and pushed automatically
```

---

## 🛠️ Troubleshooting

### Common Issues

**Port Conflicts**
```bash
# Check what's using the port
netstat -tulpn | grep :3333

# Change port in .env
echo "UNIFIED_MCP_PORT=3334" >> .env
```

**Permission Issues**
```bash
# Fix log directory permissions
sudo chown -R 1000:1000 logs/
```

**Build Failures**
```bash
# Clean build cache
docker builder prune -a

# Rebuild without cache
docker compose build --no-cache
```

### Debug Mode
```bash
# Start in debug mode
MCP_DEBUG=true docker compose up

# Access container shell
docker exec -it unified-mcp-server bash
```

---

## 📈 Scaling and Production

### Horizontal Scaling
```yaml
# Scale specific services
services:
  unified-mcp:
    deploy:
      replicas: 3
```

### Load Balancing
```yaml
# Nginx load balancer configuration
upstream mcp_backend {
    server unified-mcp-1:3333;
    server unified-mcp-2:3333;
    server unified-mcp-3:3333;
}
```

### Production Checklist
- [ ] Configure proper logging aggregation
- [ ] Set up monitoring (Prometheus/Grafana)
- [ ] Configure backup strategies
- [ ] Implement proper secret management
- [ ] Set resource limits and requests
- [ ] Configure auto-restart policies

---

## 🤝 Team Distribution

### For Teammates
1. **Install Docker Desktop**
2. **Clone repository**: `git clone <repo-url>`
3. **Start services**: `docker compose up -d`
4. **Configure clients**: Copy provided client configs

### For CI/CD Runners
```yaml
# .github/workflows/deploy.yml
- name: Deploy MCP Stack
  run: |
    docker compose pull
    docker compose up -d
```

### Air-Gapped Environments
```bash
# Export images
docker save unified-mcp:latest | gzip > unified-mcp.tar.gz

# Import on target system
gunzip -c unified-mcp.tar.gz | docker load
```

---

## 📚 Additional Resources

- [Docker MCP Best Practices](https://docs.docker.com/mcp/)
- [Multi-Stage Build Guide](https://docs.docker.com/build/building/multi-stage/)
- [Docker Compose Reference](https://docs.docker.com/compose/)
- [Container Security Guide](https://docs.docker.com/engine/security/)

---

**🎯 Result**: A production-ready, portable MCP server stack that runs identically on any machine with Docker!
