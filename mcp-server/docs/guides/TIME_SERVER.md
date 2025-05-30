# Time MCP Server

## Overview

The Time MCP Server provides comprehensive time and timezone conversion capabilities. This server enables LLMs to get current time information and perform timezone conversions using IANA timezone names, with automatic system timezone detection.

## Core Features

### Time Operations
- **Current Time Retrieval**: Get current time in any timezone
- **Timezone Conversion**: Convert time between different timezones
- **IANA Timezone Support**: Uses standard timezone names
- **System Timezone Detection**: Automatic detection of local timezone
- **DST Awareness**: Handles daylight saving time automatically

## Available Tools

### 1. get_current_time
Get current time in a specific timezone or system timezone.

**Parameters:**
- `timezone` (string, required): IANA timezone name
  - Examples: 'America/New_York', 'Europe/London', 'Asia/Tokyo'
  - Use 'UTC' as default if no timezone provided

**Response Format:**
```json
{
  "timezone": "Europe/Warsaw",
  "datetime": "2024-01-01T13:00:00+01:00",
  "is_dst": false
}
```

### 2. convert_time
Convert time between timezones.

**Parameters:**
- `source_timezone` (string, required): Source IANA timezone name
- `time` (string, required): Time in 24-hour format (HH:MM)
- `target_timezone` (string, required): Target IANA timezone name

**Response Format:**
```json
{
  "source": {
    "timezone": "America/New_York",
    "datetime": "2024-01-01T12:30:00-05:00",
    "is_dst": false
  },
  "target": {
    "timezone": "Asia/Tokyo",
    "datetime": "2024-01-01T12:30:00+09:00",
    "is_dst": false
  },
  "time_difference": "+13.0h"
}
```

## Docker Configuration

### Current Setup
The Time server is configured to run as a Docker container:

```json
{
  "time": {
    "command": "docker",
    "args": ["run", "-i", "--rm", "mcp/time"],
    "env": {},
    "description": "Time and timezone conversion capabilities (Docker-based)"
  }
}
```

### Key Features
- **Containerized**: Runs in isolated Docker environment
- **Auto-cleanup**: Container removes itself after use (`--rm`)
- **Version**: 1.0.0 (latest)
- **Protocol**: MCP 2024-11-05 (latest)

## Usage Examples

### Example 1: Get Current Time
**Request:**
```json
{
  "name": "get_current_time",
  "arguments": {
    "timezone": "Europe/Warsaw"
  }
}
```

**Response:**
```json
{
  "timezone": "Europe/Warsaw",
  "datetime": "2024-01-01T13:00:00+01:00",
  "is_dst": false
}
```

### Example 2: Convert Time Between Timezones
**Request:**
```json
{
  "name": "convert_time",
  "arguments": {
    "source_timezone": "America/New_York",
    "time": "16:30",
    "target_timezone": "Asia/Tokyo"
  }
}
```

**Response:**
```json
{
  "source": {
    "timezone": "America/New_York",
    "datetime": "2024-01-01T16:30:00-05:00",
    "is_dst": false
  },
  "target": {
    "timezone": "Asia/Tokyo",
    "datetime": "2024-01-02T06:30:00+09:00",
    "is_dst": false
  },
  "time_difference": "+14.0h"
}
```

## Common IANA Timezone Names

### Major Cities
- **Americas**: America/New_York, America/Los_Angeles, America/Chicago, America/Toronto
- **Europe**: Europe/London, Europe/Paris, Europe/Berlin, Europe/Rome, Europe/Madrid
- **Asia**: Asia/Tokyo, Asia/Shanghai, Asia/Mumbai, Asia/Dubai, Asia/Singapore
- **Australia**: Australia/Sydney, Australia/Melbourne, Australia/Perth
- **Africa**: Africa/Cairo, Africa/Johannesburg, Africa/Lagos

### Special Timezones
- **UTC**: Coordinated Universal Time
- **GMT**: Greenwich Mean Time (equivalent to UTC)

## Integration Status

✅ **Docker Image**: `mcp/time:latest` (305MB) - Downloaded and ready
✅ **Configuration**: Added to `.mcp.json` and Claude Desktop config
✅ **Testing**: Verified both tools are available and functional
✅ **Server Integration**: Loaded in unified MCP server (13 servers total)
✅ **Protocol Compliance**: Uses correct MCP 2024-11-05 protocol

## Example Questions for Claude

### Basic Time Queries
1. "What time is it now?" (uses system timezone)
2. "What time is it in Tokyo?"
3. "What's the current time in London?"
4. "Show me the time in New York and Los Angeles"

### Time Conversion Queries
1. "When it's 4 PM in New York, what time is it in London?"
2. "Convert 9:30 AM Tokyo time to New York time"
3. "If it's 2:00 PM in Paris, what time is it in Sydney?"
4. "What time is 6:00 AM EST in Pacific time?"

### Business Use Cases
1. "What time should I schedule a meeting for 3 PM EST in other timezones?"
2. "When is 9 AM business hours in London for someone in California?"
3. "Convert this meeting time to all major business timezones"

## Customization Options

### System Timezone Override
You can override the default system timezone by adding the `--local-timezone` argument:

```json
{
  "command": "docker",
  "args": ["run", "-i", "--rm", "mcp/time", "--local-timezone=America/New_York"],
  "env": {},
  "description": "Time server with custom local timezone"
}
```

## Benefits

- **Global Time Awareness**: Handle international time coordination
- **Business Scheduling**: Schedule meetings across timezones
- **Travel Planning**: Convert times for travel itineraries
- **Event Coordination**: Coordinate global events and deadlines
- **Development**: Handle timezone-aware applications
- **Communication**: Clear time communication across regions

## Troubleshooting

### Common Issues
1. **Invalid Timezone**: Ensure IANA timezone names are correct
2. **Time Format**: Use 24-hour format (HH:MM) for conversions
3. **Container Issues**: Check Docker daemon is running

### Verification Commands
```bash
# Test time server directly
docker run -i --rm mcp/time

# Check available timezones (common ones)
# America/New_York, Europe/London, Asia/Tokyo, etc.

# Verify Docker image
docker images | grep mcp/time
```

## Next Steps

1. **Test Integration**: Verify time functions work in Claude Desktop
2. **Explore Timezones**: Try different IANA timezone names
3. **Business Use**: Use for scheduling and coordination tasks
4. **Integration**: Combine with calendar and scheduling workflows
