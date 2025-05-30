# Knowledge Graph Memory Server

## Overview

The Knowledge Graph Memory Server provides persistent memory capabilities using a local knowledge graph. This allows Claude to remember information about users, relationships, and context across multiple conversations.

## Core Concepts

### Entities
Entities are the primary nodes in the knowledge graph. Each entity has:
- **Unique name**: Identifier for the entity
- **Entity type**: Classification (e.g., "person", "organization", "event")
- **Observations**: List of facts about the entity

Example:
```json
{
  "name": "John_Smith",
  "entityType": "person",
  "observations": ["Speaks fluent Spanish", "Graduated in 2019"]
}
```

### Relations
Relations define directed connections between entities in active voice.

Example:
```json
{
  "from": "John_Smith",
  "to": "Anthropic",
  "relationType": "works_at"
}
```

### Observations
Discrete pieces of information about entities:
- Stored as strings
- Attached to specific entities
- Can be added or removed independently
- Should be atomic (one fact per observation)

## Available Tools

### Core Operations
1. **create_entities** - Create new entities with observations
2. **create_relations** - Establish relationships between entities
3. **add_observations** - Add new facts to existing entities
4. **delete_entities** - Remove entities and their relations
5. **delete_observations** - Remove specific facts from entities
6. **delete_relations** - Remove specific relationships

### Query Operations
7. **read_graph** - Read the entire knowledge graph
8. **search_nodes** - Search entities by name, type, or observation content
9. **open_nodes** - Retrieve specific entities by name

## Docker Configuration

### Current Setup
The memory server is configured to run as a Docker container with persistent storage:

```json
{
  "memory": {
    "command": "docker",
    "args": ["run", "-i", "-v", "claude-memory:/app/dist", "--rm", "mcp/memory"],
    "env": {},
    "description": "Knowledge Graph Memory Server - Persistent memory using local knowledge graph"
  }
}
```

### Key Features
- **Persistent Storage**: Uses Docker volume `claude-memory:/app/dist`
- **Containerized**: Runs in isolated Docker environment
- **Auto-cleanup**: Container removes itself after use (`--rm`)
- **Version**: 0.6.3 (latest)

## Usage Examples

### Creating Entities
```json
{
  "tool": "create_entities",
  "entities": [
    {
      "name": "default_user",
      "entityType": "person",
      "observations": ["Prefers Docker-based solutions", "Works with MCP servers"]
    }
  ]
}
```

### Adding Relationships
```json
{
  "tool": "create_relations",
  "relations": [
    {
      "from": "default_user",
      "to": "MCP_Project",
      "relationType": "maintains"
    }
  ]
}
```

### Searching Memory
```json
{
  "tool": "search_nodes",
  "query": "Docker"
}
```

## Integration Status

✅ **Docker Image**: `mcp/memory:latest` - Downloaded and ready
✅ **Configuration**: Added to `.mcp.json` and Claude Desktop config
✅ **Testing**: Verified all 9 tools are available and functional
✅ **Persistence**: Docker volume configured for data persistence
✅ **Server Integration**: Loaded in unified MCP server (12 servers total)

## Recommended System Prompt

For optimal memory utilization, use this system prompt:

```
Follow these steps for each interaction:

1. User Identification:
   - Assume you are interacting with default_user
   - If you haven't identified default_user, proactively try to do so

2. Memory Retrieval:
   - Always begin by saying "Remembering..." and retrieve relevant information
   - Refer to your knowledge graph as your "memory"

3. Memory Categories:
   - Basic Identity (age, gender, location, job, education)
   - Behaviors (interests, habits)
   - Preferences (communication style, language)
   - Goals (targets, aspirations)
   - Relationships (personal and professional, up to 3 degrees)

4. Memory Update:
   - Create entities for recurring organizations, people, events
   - Connect them using relations
   - Store facts as observations
```

## Benefits

- **Persistent Context**: Remembers information across conversations
- **Relationship Mapping**: Tracks connections between entities
- **Searchable Memory**: Query by content, names, or types
- **Structured Data**: Organized knowledge graph format
- **Docker Security**: Isolated execution environment
- **Data Persistence**: Survives container restarts

## Troubleshooting

### Common Issues
1. **Volume Permissions**: Ensure Docker has access to create volumes
2. **Memory Conflicts**: Only one memory server should be active
3. **Data Loss**: Check if volume is properly mounted

### Verification Commands
```bash
# Check if memory server is working
docker run -i -v claude-memory:/app/dist --rm mcp/memory

# Verify volume exists
docker volume ls | grep claude-memory

# Check volume data
docker run --rm -v claude-memory:/data alpine ls -la /data
```

## Next Steps

1. **Test Integration**: Verify memory works in Claude Desktop
2. **Create Initial Entities**: Set up user profile and preferences
3. **Monitor Usage**: Check memory growth and performance
4. **Backup Strategy**: Consider volume backup procedures
