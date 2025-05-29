# Makefile for MCP Server Project
# Provides common development and deployment tasks

.PHONY: help setup test clean build deploy docker-build docker-run lint format check install dev-install

# Default target
help:
	@echo "🛠️  MCP Server Development Commands"
	@echo "=================================="
	@echo ""
	@echo "📦 Setup & Installation:"
	@echo "  setup          - Complete environment setup"
	@echo "  install        - Install production dependencies"
	@echo "  dev-install    - Install development dependencies"
	@echo ""
	@echo "🧪 Testing & Quality:"
	@echo "  test           - Run all tests"
	@echo "  test-unit      - Run unit tests only"
	@echo "  test-integration - Run integration tests"
	@echo "  lint           - Run code linting"
	@echo "  format         - Format code with black"
	@echo "  check          - Run all quality checks"
	@echo ""
	@echo "🐳 Docker:"
	@echo "  docker-build   - Build Docker images"
	@echo "  docker-run     - Run with Docker Compose"
	@echo "  docker-clean   - Clean Docker resources"
	@echo ""
	@echo "🚀 Deployment:"
	@echo "  build          - Build for production"
	@echo "  deploy         - Deploy to production"
	@echo ""
	@echo "🧹 Maintenance:"
	@echo "  clean          - Clean build artifacts"
	@echo "  clean-all      - Deep clean (includes cache)"
	@echo "  logs           - View server logs"

# Setup and Installation
setup:
	@echo "🚀 Setting up MCP Server environment..."
	python scripts/setup/setup-environment.py

install:
	@echo "📦 Installing production dependencies..."
	pip install -r requirements.txt

dev-install: install
	@echo "🔧 Installing development dependencies..."
	pip install pytest pytest-cov black flake8 mypy

# Testing
test:
	@echo "🧪 Running all tests..."
	python -m pytest tests/ -v --cov=src --cov-report=html

test-unit:
	@echo "🧪 Running unit tests..."
	python -m pytest tests/test_mcp_connection.py -v

test-integration:
	@echo "🧪 Running integration tests..."
	python -m pytest tests/test_comprehensive.py -v

test-compliance:
	@echo "🧪 Running MCP compliance tests..."
	python -m pytest tests/test_mcp_compliance.py -v

# Code Quality
lint:
	@echo "🔍 Running code linting..."
	flake8 src/ tests/ --max-line-length=100 --ignore=E203,W503

format:
	@echo "✨ Formatting code..."
	black src/ tests/ --line-length=100

type-check:
	@echo "🔍 Running type checking..."
	mypy src/ --ignore-missing-imports

check: lint type-check
	@echo "✅ All quality checks completed"

# Docker
docker-build:
	@echo "🐳 Building Docker images..."
	./scripts/deploy/build-docker.sh

docker-run:
	@echo "🐳 Running with Docker Compose..."
	docker-compose -f docker/docker-compose.yml up

docker-clean:
	@echo "🧹 Cleaning Docker resources..."
	docker-compose -f docker/docker-compose.yml down
	docker system prune -f

# Build and Deployment
build:
	@echo "🏗️  Building for production..."
	python -m py_compile src/server/unified_mcp_v2.py
	python -m py_compile src/client/mcp_client.py

deploy: build test
	@echo "🚀 Deploying to production..."
	./scripts/deploy/deploy-second-pc.sh

# Configuration
config-generate:
	@echo "⚙️  Generating configurations..."
	python scripts/config/generate-mcp-configs.py

config-verify:
	@echo "✅ Verifying configurations..."
	python scripts/config/verify-claude-config.py

# Maintenance
clean:
	@echo "🧹 Cleaning build artifacts..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/

clean-all: clean
	@echo "🧹 Deep cleaning..."
	rm -rf logs/*.log
	rm -rf .mypy_cache/
	rm -rf .tox/
	docker system prune -af

logs:
	@echo "📋 Viewing server logs..."
	tail -f logs/mcp_server_v2.log 2>/dev/null || echo "No log file found"

# Development helpers
dev-server:
	@echo "🔧 Starting development server..."
	python src/server/unified_mcp_v2.py --transport stdio

dev-server-http:
	@echo "🔧 Starting development server (HTTP)..."
	python src/server/unified_mcp_v2.py --transport http --port 3333

dev-test:
	@echo "🧪 Running development tests..."
	python tests/test_mcp_connection.py

# Documentation
docs-serve:
	@echo "📚 Serving documentation..."
	@echo "Documentation available in docs/ directory"
	@echo "Open docs/guides/GETTING_STARTED.md to begin"

# Quick commands
quick-start: setup test
	@echo "🎉 Quick start completed!"
	@echo "Run 'make dev-server' to start the server"

quick-test:
	@echo "⚡ Quick test..."
	python tests/test_mcp_connection.py

# Environment info
info:
	@echo "ℹ️  Environment Information"
	@echo "=========================="
	@echo "Python version: $$(python --version)"
	@echo "Pip version: $$(pip --version)"
	@echo "Docker version: $$(docker --version 2>/dev/null || echo 'Not installed')"
	@echo "Project root: $$(pwd)"
	@echo "Git branch: $$(git branch --show-current 2>/dev/null || echo 'Not a git repo')"

# Aliases for common tasks
start: dev-server
run: docker-run
tests: test
fmt: format
