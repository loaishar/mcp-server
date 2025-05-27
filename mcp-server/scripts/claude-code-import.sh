#!/bin/bash
# Claude Code MCP Import Script
# Run this in WSL to import MCP servers from Claude Desktop

set -e

echo "🚀 Claude Code MCP Server Import"
echo "================================="

# Check if Claude Code CLI is available
if ! command -v claude &> /dev/null; then
    echo "❌ Claude Code CLI not found!"
    echo "📋 Install with: curl -fsSL https://claude.ai/install.sh | sh"
    exit 1
fi

echo "✅ Claude Code CLI found"

# Check Claude Desktop config (Windows path via WSL)
CLAUDE_CONFIG="/mnt/c/Users/$USER/AppData/Roaming/Claude/claude_desktop_config.json"
if [ ! -f "$CLAUDE_CONFIG" ]; then
    # Try alternative path
    CLAUDE_CONFIG="/mnt/c/Users/$(whoami)/AppData/Roaming/Claude/claude_desktop_config.json"
    if [ ! -f "$CLAUDE_CONFIG" ]; then
        echo "❌ Claude Desktop config not found!"
        echo "Expected: $CLAUDE_CONFIG"
        exit 1
    fi
fi

echo "✅ Claude Desktop config found: $CLAUDE_CONFIG"

# Count servers
SERVER_COUNT=$(jq '.mcpServers | length' "$CLAUDE_CONFIG" 2>/dev/null || echo "0")
echo "📊 Found $SERVER_COUNT MCP servers in Claude Desktop"

# Import servers
echo ""
echo "🔄 Importing MCP servers to Claude Code..."
if claude mcp add-from-claude-desktop -s global; then
    echo "✅ Import successful!"
else
    echo "❌ Import failed!"
    exit 1
fi

# List imported servers
echo ""
echo "📋 Imported servers:"
claude mcp list

echo ""
echo "🎉 Claude Code MCP setup complete!"
echo "💡 Your MCP servers are now available in Claude Code sessions"
