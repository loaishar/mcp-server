# 📊 Performance Monitoring Guide

## Overview

The Unified MCP Server v2 includes comprehensive performance monitoring and health management features to ensure optimal operation and reliability.

## 🔍 Health Monitoring Features

### **Automatic Health Checks**
- **Heartbeat Monitoring**: Tracks last activity for each connected server
- **Connection Status**: Monitors process health and initialization state
- **Error Tracking**: Records and counts errors for each server
- **Response Time Metrics**: Tracks average response times with exponential moving average

### **Automatic Recovery**
- **Connection Retry**: Automatic reconnection with exponential backoff
- **Health Monitor Loop**: Runs every 30 seconds to check server health
- **Graceful Degradation**: Continues operating even if some servers fail

## 📈 Performance Metrics

### **Server Statistics**
Each connected server tracks:
- `request_count`: Total number of requests processed
- `error_count`: Number of failed requests
- `avg_response_time`: Average response time in seconds
- `last_heartbeat`: Timestamp of last successful communication
- `connection_attempts`: Number of connection attempts made
- `last_error`: Most recent error message

### **Built-in Tools for Monitoring**

#### 1. **health_check**
```json
{
  "name": "health_check",
  "description": "Check health of unified MCP server"
}
```
Returns comprehensive health status including:
- Server version and initialization status
- Connected servers count
- Total tools, resources, and prompts
- Transport type

#### 2. **server_statistics**
```json
{
  "name": "server_statistics", 
  "description": "Get comprehensive performance statistics for all servers"
}
```
Returns detailed statistics for all servers including:
- Health status for each server
- Performance metrics (requests, errors, response times)
- Connection status and capabilities count

#### 3. **list_connected_servers**
```json
{
  "name": "list_connected_servers",
  "description": "List all connected MCP servers and their status"
}
```
Shows status of all configured servers with tool/resource counts.

#### 4. **reconnect_server**
```json
{
  "name": "reconnect_server",
  "description": "Manually reconnect to a specific server",
  "inputSchema": {
    "properties": {
      "server_name": {"type": "string"}
    }
  }
}
```
Manually trigger reconnection to a specific server.

## 🚨 Error Handling

### **Retry Logic**
- **Maximum Retries**: 3 attempts per connection
- **Exponential Backoff**: 1s, 2s, 4s delays between retries
- **Timeout Handling**: 10s for process start, 15s for initialization

### **Error Categories**
1. **FileNotFoundError**: Command not found (no retry)
2. **PermissionError**: Permission denied (no retry)
3. **TimeoutError**: Connection/response timeout (retry with backoff)
4. **General Exceptions**: Unexpected errors (retry with backoff)

### **Graceful Degradation**
- Server continues operating even if some MCP servers fail
- Failed servers are excluded from tool routing
- Health monitor attempts automatic recovery

## 📊 Monitoring Dashboard

### **HTTP Health Endpoint**
When running in HTTP mode, access health information at:
```
GET /health
```
Returns:
```json
{
  "status": "healthy",
  "transport": "http_sse", 
  "version": "2.0.0"
}
```

### **Real-time Statistics**
Use the `server_statistics` tool to get real-time performance data:

```bash
# Example output
{
  "unified_server": {
    "version": "2.0.0",
    "initialized": true,
    "transport": "stdio",
    "total_tools": 56,
    "total_resources": 15,
    "total_prompts": 8
  },
  "connected_servers": {
    "github": {
      "healthy": true,
      "initialized": true,
      "tools_count": 12,
      "request_count": 45,
      "error_count": 2,
      "avg_response_time": 0.234
    }
  },
  "summary": {
    "total_servers": 5,
    "healthy_servers": 4,
    "unhealthy_servers": 1,
    "total_requests": 156,
    "total_errors": 8
  }
}
```

## 🔧 Configuration

### **Health Check Interval**
Modify the health check frequency:
```python
server.health_check_interval = 60.0  # Check every 60 seconds
```

### **Timeout Settings**
Adjust timeout values in the server configuration:
- Process start timeout: 10 seconds
- Initialization timeout: 15 seconds  
- Request timeout: 30 seconds

## 🚀 Best Practices

### **Monitoring**
1. **Regular Health Checks**: Use `health_check` tool periodically
2. **Statistics Review**: Monitor `server_statistics` for performance trends
3. **Error Analysis**: Check `last_error` fields for troubleshooting

### **Performance Optimization**
1. **Connection Pooling**: Reuse persistent connections
2. **Async Operations**: All operations are non-blocking
3. **Resource Management**: Automatic cleanup on shutdown

### **Troubleshooting**
1. **Check Logs**: Review `mcp_server_v2.log` for detailed information
2. **Manual Reconnection**: Use `reconnect_server` tool for problematic servers
3. **Statistics Analysis**: Use performance metrics to identify bottlenecks

## 📝 Logging

### **Log Levels**
- `INFO`: Normal operations, connections, disconnections
- `WARNING`: Unhealthy servers, retry attempts
- `ERROR`: Connection failures, request errors
- `DEBUG`: Detailed request/response information

### **Log Files**
- **Main Log**: `mcp_server_v2.log`
- **Format**: `timestamp - logger - level - message`
- **Rotation**: Manual (implement logrotate if needed)

## 🔍 Troubleshooting Common Issues

### **Server Not Connecting**
1. Check if command exists and is executable
2. Verify environment variables are set
3. Check network connectivity for remote servers
4. Review error logs for specific failure reasons

### **High Response Times**
1. Check server load and resource usage
2. Monitor network latency for remote servers
3. Consider increasing timeout values
4. Review server-specific performance metrics

### **Frequent Disconnections**
1. Check server stability and resource usage
2. Monitor network connectivity
3. Review server logs for crash reasons
4. Consider adjusting health check intervals

This monitoring system ensures your MCP server operates reliably and provides visibility into performance characteristics.
