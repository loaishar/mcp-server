# Multi-stage Dockerfile for Unified MCP Server v2
# Fully MCP-compliant implementation with stdio and HTTP/SSE transports

# ---- Build Stage ----
FROM python:3.12-slim AS build

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies to user directory
RUN pip install --user --no-cache-dir -r requirements.txt && \
    pip install --user --no-cache-dir aiohttp python-dotenv

# Copy source code (build context is project root)
COPY src/ ./src/
COPY config/ ./config/
COPY .mcp.json .

# Compile Python files for faster startup
RUN python -m compileall -q src/

# ---- Runtime Stage ----
FROM python:3.12-slim AS runtime

# Install runtime dependencies including Node.js
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    gnupg \
    && mkdir -p /etc/apt/keyrings \
    && curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg \
    && echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_20.x nodistro main" | tee /etc/apt/sources.list.d/nodesource.list \
    && apt-get update \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security
RUN groupadd -r mcp && useradd -r -g mcp -u 1000 mcp

# Set working directory
WORKDIR /app

# Copy Python packages from build stage
COPY --from=build /root/.local /home/mcp/.local

# Copy application files
COPY --from=build /app/src ./src
COPY --from=build /app/config ./config
COPY --from=build /app/.mcp.json .

# Create logs directory and fix npm permissions
RUN mkdir -p logs && \
    mkdir -p /home/mcp/.npm && \
    chown -R mcp:mcp /app /home/mcp/.npm

# Switch to non-root user
USER mcp

# Set Python path to include user packages
ENV PATH="/home/mcp/.local/bin:$PATH"
ENV PYTHONPATH="/home/mcp/.local/lib/python3.12/site-packages"
ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=utf-8

# Default transport is stdio
ENV MCP_TRANSPORT=stdio

# Health check - different for stdio vs http
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD if [ "$MCP_TRANSPORT" = "http" ]; then \
            curl -f http://localhost:3333/health || exit 1; \
        else \
            python -c "import sys; sys.exit(0)" || exit 1; \
        fi

# Expose port for HTTP transport
EXPOSE 3333

# Default command - can be overridden with --transport flag
ENTRYPOINT ["python", "src/server/unified_mcp_v2.py"]
CMD ["--transport", "stdio"]