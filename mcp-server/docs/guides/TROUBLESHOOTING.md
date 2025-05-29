# 🔧 MCP Configuration Troubleshooting Guide

## 🚨 **Current Issue: "run_unified_mcp.bat not found"**

### **Problem**
Claude Desktop shows error: `'C:\Users\loai1\mcp-server\run_unified_mcp.bat' is not recognized`

### **Root Cause**
Claude Desktop is using a **cached configuration** from before our cleanup. The current configuration is correct, but Claude Desktop hasn't reloaded it.

### **✅ Verified Facts**
- ✅ Configuration file has **all 13 MCP servers**
- ✅ Paths are correct (`src/unified_mcp.py`)
- ✅ No batch file references in current config
- ✅ Unified MCP server starts correctly when run directly

---

## 🛠️ **Solution Steps**

### **Step 1: Complete Claude Desktop Restart**

1. **Close Claude Desktop completely**:
   - Close all Claude Desktop windows
   - Check system tray (bottom-right corner) and close if running
   - Open Task Manager (Ctrl+Shift+Esc)
   - Look for "Claude Desktop" processes and **End Task**

2. **Clear Claude Desktop cache** (if restart doesn't work):
   ```powershell
   # Stop Claude Desktop completely first, then:
   Remove-Item "$env:APPDATA\Claude\logs" -Recurse -Force -ErrorAction SilentlyContinue
   Remove-Item "$env:LOCALAPPDATA\Claude" -Recurse -Force -ErrorAction SilentlyContinue
   ```

3. **Restart Claude Desktop**:
   - Open Claude Desktop from Start Menu
   - Go to Settings → Developer
   - Check MCP servers list

### **Step 2: Force Configuration Reload**

If restart doesn't work, force a fresh configuration:

```powershell
# Remove old config and deploy fresh
Remove-Item "$env:APPDATA\Claude\claude_desktop_config.json" -Force
python scripts/manage-mcp.py deploy
```

### **Step 3: Verify Configuration**

```powershell
# Check configuration is correct
python scripts/verify-claude-config.py
```

**Expected output**: ✅ SUCCESS: Claude Desktop has all 13 MCP servers!

---

## 🔍 **Debugging Steps**

### **Check 1: Verify File Paths**
```powershell
# Check if unified MCP server exists and runs
Test-Path "src\unified_mcp.py"
python src\unified_mcp.py  # Should start without errors
```

### **Check 2: Verify Configuration Content**
```powershell
# Check deployed configuration
Get-Content "$env:APPDATA\Claude\claude_desktop_config.json" | ConvertFrom-Json | Select-Object -ExpandProperty mcpServers | Get-Member -MemberType NoteProperty
```

**Expected**: Should show all 13 server names.

### **Check 3: Test Individual MCP Servers**
```powershell
# Test git server (example)
npx -y @modelcontextprotocol/server-git
```

**Expected**: Should start without errors.

---

## 🎯 **Common Issues & Solutions**

### **Issue 1: "Server disconnected immediately"**
**Cause**: Path or dependency issues
**Solution**:
```powershell
# Check Python path
where python
python --version

# Check dependencies
pip install python-dotenv psutil

# Test server directly
python src/unified_mcp.py
```

### **Issue 2: "Only 2 servers showing in UI"**
**Cause**: Claude Desktop using cached configuration
**Solution**: Complete restart (see Step 1 above)

### **Issue 3: "npx command not found"**
**Cause**: Node.js not installed or not in PATH
**Solution**:
```powershell
# Install Node.js from https://nodejs.org
# Or check if it's in PATH
where npx
node --version
npm --version
```

### **Issue 4: "Docker command not found"**
**Cause**: Docker not installed (for GitHub MCP server)
**Solution**: Install Docker Desktop or disable GitHub server temporarily

---

## 🚀 **Quick Fix Commands**

### **Complete Reset & Redeploy**
```powershell
# 1. Stop Claude Desktop completely
# 2. Run this:
Remove-Item "$env:APPDATA\Claude\claude_desktop_config.json" -Force -ErrorAction SilentlyContinue
python scripts/manage-mcp.py deploy
# 3. Start Claude Desktop
# 4. Check Settings → Developer
```

### **Verify Everything Works**
```powershell
# Check configuration
python scripts/verify-claude-config.py

# Test MCP server
python tests/test_mcp_connection.py

# Check status
python scripts/manage-mcp.py status
```

---

## 📊 **Expected Results After Fix**

### **In Claude Desktop Developer Settings:**
```
✅ unified-mcp          (Connected)
✅ playwright-vision    (Connected)  
✅ git                  (Connected)
✅ memory               (Connected)
✅ sequential-thinking  (Connected)
✅ playwright           (Connected)
✅ puppeteer            (Connected)
✅ browser-tools        (Connected)
✅ neon                 (Connected)
✅ supabase             (Connected)
✅ github               (Connected)
✅ figma                (Connected)
✅ hyperbrowser         (Connected)
```

### **Total: 13 MCP servers connected**

---

## 🆘 **If Nothing Works**

### **Nuclear Option: Complete Reset**
```powershell
# 1. Close Claude Desktop completely
# 2. Clear all Claude data
Remove-Item "$env:APPDATA\Claude" -Recurse -Force
Remove-Item "$env:LOCALAPPDATA\Claude" -Recurse -Force

# 3. Redeploy configuration
python scripts/manage-mcp.py deploy

# 4. Restart Claude Desktop
# 5. Reconfigure settings (you'll need to log in again)
```

### **Alternative: Use Docker Deployment**
If direct configuration continues to have issues:
```powershell
# Switch to Docker-based deployment
.\scripts\deploy-second-pc.ps1 -Mode docker
```

---

## 📞 **Getting Help**

1. **Check logs**: Claude Desktop → Settings → Developer → Open Logs Folder
2. **Run diagnostics**: `python scripts/verify-claude-config.py`
3. **Test server**: `python src/unified_mcp.py`
4. **Check dependencies**: `pip list | findstr "dotenv\|psutil"`

**The configuration is correct - this is just a Claude Desktop caching issue that requires a complete restart!** 🚀
