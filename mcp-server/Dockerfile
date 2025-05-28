# Multi-stage Dockerfile for Unified MCP Server
# Based on the blueprint for portable, secure, multi-platform containers

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
RUN pip install --user --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY config/ ./config/
COPY .mcp.json .

# Compile Python files for faster startup
RUN python -m compileall -q src/

# ---- Runtime Stage ----
FROM python:3.12-slim AS runtime

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    curl \
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

# Create logs directory
RUN mkdir -p logs && chown -R mcp:mcp /app

# Switch to non-root user
USER mcp

# Set Python path to include user packages
ENV PATH="/home/mcp/.local/bin:$PATH"
ENV PYTHONPATH="/home/mcp/.local/lib/python3.12/site-packages"
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)" || exit 1

# Expose port for MCP server
EXPOSE 3333

# Default command
CMD ["python", "src/unified_mcp.py"]
