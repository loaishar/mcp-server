# Sequential Thinking MCP Server Docker Image
FROM node:18-alpine

# Set working directory
WORKDIR /app

# Install the sequential thinking MCP server globally
RUN npm install -g @cyanheads/sequential-thinking-mcp-server

# Create a non-root user
RUN addgroup -g 1001 -S mcp && \
    adduser -S mcp -u 1001 -G mcp

# Switch to non-root user
USER mcp

# Set the entrypoint to run the sequential thinking server
ENTRYPOINT ["npx", "@cyanheads/sequential-thinking-mcp-server"]

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"healthcheck","version":"1.0"}}}' | npx @cyanheads/sequential-thinking-mcp-server || exit 1

# Labels
LABEL org.opencontainers.image.title="Sequential Thinking MCP Server"
LABEL org.opencontainers.image.description="Enhanced reasoning and step-by-step thinking MCP server"
LABEL org.opencontainers.image.version="1.0.0"
LABEL org.opencontainers.image.source="https://github.com/cyanheads/sequential-thinking-mcp-server"
