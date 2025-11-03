# Configuration Fix for Testing Device

## Root Cause Identified
The setup.py file had a critical bug using relative paths that caused silent failures during `pip install`. This has been **FIXED** in the latest commit.

## Problem
Your `.claude.json` has outdated crypto-skills-mcp configuration from before the fixes were implemented.

## Current Broken Configuration
```json
"crypto-skills-mcp": {
  "command": "C:\\Users\\trist\\AppData\\Local\\Programs\\Python\\Python313\\python.exe",
  "args": ["-m", "mcp_client"],  // ← WRONG
  "cwd": "C:\\Users\\trist\\crypto-skills-mcp",
  "env": {
    "MODE": "hybrid"
  }
  // ← MISSING "type": "stdio" and "PYTHONUNBUFFERED": "1"
}
```

## Solution: Reinstall with Fixed setup.py

The latest commit includes fixes to setup.py that resolve the silent installation failure.

### What Was Fixed

**Before (BROKEN):**
- setup.py used relative paths: `subprocess.call([sys.executable, 'scripts/post_install.py'])`
- During `pip install`, working directory changes caused path resolution to fail
- Script never ran, but installation appeared successful
- Result: `.claude.json` never updated

**After (FIXED):**
- setup.py uses absolute paths: `Path(__file__).parent / 'scripts' / 'post_install.py'`
- Explicit exit code checking raises exceptions on failure
- Clear success/failure messages with troubleshooting steps
- Configuration now updates reliably during installation

### Steps to Fix

```bash
# 1. Navigate to crypto-skills-mcp directory
cd C:\Users\trist\crypto-skills-mcp

# 2. Pull latest changes with setup.py fixes
git pull origin main

# 3. Reinstall package to trigger configuration update
pip install -e .
```

### Expected Output
With the fixed setup.py, you should now see:
```
======================================================================
🔧 Running post-installation MCP configuration...
======================================================================
[INFO] Updating crypto-skills-mcp configuration...
[INFO] Old args: ['-m', 'mcp_client']
[INFO] New args: ['server.py']
[OK] crypto-skills-mcp configuration updated

✅ MCP configuration successful!
   Restart Claude Code to use crypto-skills-mcp
======================================================================
```

### Verify Installation

Run the validation script to confirm everything is configured correctly:
```bash
python scripts/validate_install.py
```

This will check:
- Package installation
- FastMCP dependency
- .claude.json configuration
- Server compilation

### After Installation

1. **Restart Claude Code** (critical - must restart for config changes to take effect)
2. **Verify Connection**:
   - Open MCP server status panel
   - crypto-skills-mcp should show: `Status: ✓ connected`

## What Gets Fixed

The reinstall will automatically update your `.claude.json` to:
```json
"crypto-skills-mcp": {
  "type": "stdio",           // ← ADDED (CRITICAL)
  "command": "C:\\Users\\trist\\AppData\\Local\\Programs\\Python\\Python313\\python.exe",
  "args": ["server.py"],     // ← FIXED
  "cwd": "C:\\Users\\trist\\crypto-skills-mcp",
  "env": {
    "MODE": "hybrid",
    "PYTHONUNBUFFERED": "1"  // ← ADDED
  }
}
```

## Alternative: Manual Fix

If reinstall doesn't work for any reason, you can manually edit `C:\Users\trist\.claude.json`:

1. Open `C:\Users\trist\.claude.json` in a text editor
2. Find the `"crypto-skills-mcp"` section
3. Replace it with the correct configuration shown above
4. Save the file
5. Restart Claude Code

## Verification

After fixing, verify the server works:

```bash
# Test server starts correctly
cd C:\Users\trist\crypto-skills-mcp
python server.py

# Should show FastMCP server starting without errors
# Press Ctrl+C to stop
```

## Troubleshooting

If connection still fails after reinstall and restart:

1. Check the configuration was actually updated:
   ```powershell
   # View crypto-skills-mcp config
   Get-Content C:\Users\trist\.claude.json | Select-String -Context 0,10 "crypto-skills-mcp"
   ```

2. Verify it has all required fields:
   - ✅ `"type": "stdio"`
   - ✅ `"args": ["server.py"]`
   - ✅ `"PYTHONUNBUFFERED": "1"` in env

3. Check Claude Code logs for error messages

4. If all else fails, use the manual fix method above

## Questions?

If you encounter any issues, report:
- Output from `pip install -e .`
- Content of crypto-skills-mcp section in `.claude.json`
- Any error messages from Claude Code MCP server panel
