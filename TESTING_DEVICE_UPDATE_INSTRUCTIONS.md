# Testing Device Update Instructions

## Critical Issue Found and Fixed

The validation script had a bug that caused it to crash. This has been **FIXED** in commit `b1b48d1`.

Additionally, your `.claude.json` is missing the required `"type": "stdio"` field, which is why the MCP server shows "Status: ✘ failed".

## Root Causes

### 1. Validation Script Bug (FIXED)
- **Bug:** Line 77 used `"type": "stdio"` (string value) instead of `"type": str` (type class)
- **Error:** `isinstance() arg 2 must be a type, a tuple of types, or a union`
- **Status:** ✅ Fixed in latest commit

### 2. Missing "type" Field in .claude.json
- **Current config:** Missing `"type": "stdio"` field
- **Also missing:** `"PYTHONUNBUFFERED": "1"` in env
- **Has wrong args:** `["-m", "mcp_client"]` instead of `["server.py"]`
- **Status:** ⚠️ Needs manual fix

## Your Current Configuration

```json
"crypto-skills-mcp": {
  "command": "C:\\Python314\\python.exe",
  "args": ["-m", "mcp_client"],  // ← WRONG
  "cwd": "C:\\Users\\User\\crypto-skills-mcp",
  "env": {"MODE": "hybrid"}  // ← MISSING PYTHONUNBUFFERED
  // ← MISSING "type": "stdio" FIELD
}
```

## Required Configuration

```json
"crypto-skills-mcp": {
  "type": "stdio",  // ← REQUIRED - ADD THIS
  "command": "C:\\Users\\trist\\AppData\\Local\\Programs\\Python\\Python313\\python.exe",
  "args": ["server.py"],  // ← CORRECT
  "cwd": "C:\\Users\\trist\\crypto-skills-mcp",
  "env": {
    "MODE": "hybrid",
    "PYTHONUNBUFFERED": "1"  // ← RECOMMENDED - ADD THIS
  }
}
```

## Fix Instructions

### Step 1: Pull Latest Changes
```powershell
cd C:\Users\trist\crypto-skills-mcp
git pull origin main
```

### Step 2: Run Post-Install Script
```powershell
python scripts/post_install.py
```

**Expected output:**
```
======================================================================
Configuring crypto-skills-mcp for Claude Code
======================================================================
[BACKUP] Created backup: C:\Users\trist\.claude.json.backup
[INFO] Updating crypto-skills-mcp configuration...
[INFO] Old args: ['-m', 'mcp_client']
[INFO] New args: ['server.py']
[INFO] Adding missing field: type
[INFO] Adding missing env variable: PYTHONUNBUFFERED
[OK] crypto-skills-mcp configuration updated

[OK] Configuration changes applied successfully
```

### Step 3: Verify with Fixed Validation Script
```powershell
python scripts/validate_install.py
```

**Expected output:**
```
======================================================================
crypto-skills-mcp Installation Validation
======================================================================

Checking Package Installation...
  ✓ Package installed at: C:\Users\trist\crypto-skills-mcp

Checking FastMCP Dependency...
  ✓ FastMCP version: 2.11.3

Checking Server File...
  ✓ server.py found at: C:\Users\trist\crypto-skills-mcp\server.py

Checking Claude Configuration...
  ✓ .claude.json configured correctly at: C:\Users\trist\.claude.json

Checking Server Compilation...
  ✓ server.py compiles successfully

======================================================================
✅ ALL CHECKS PASSED
======================================================================

Next steps:
  1. Restart Claude Code
  2. Check MCP server status panel
  3. crypto-skills-mcp should show: Status: ✓ connected
```

### Step 4: Restart Claude Code

**Critical:** You MUST restart Claude Code for configuration changes to take effect.

### Step 5: Verify Connection

Open Claude Code and check the MCP server status panel:
```
Crypto-skills-mcp MCP Server
Status: ✓ connected  // ← Should show connected
```

## Troubleshooting

### If post_install.py says "already up-to-date" but validation fails:

Your config might be in a weird state. Manually edit `.claude.json`:

1. Open `C:\Users\trist\.claude.json` in a text editor
2. Find the `"crypto-skills-mcp"` section
3. Add the missing `"type": "stdio"` field as the FIRST field
4. Update `"args"` to `["server.py"]`
5. Add `"PYTHONUNBUFFERED": "1"` to the env object
6. Save the file
7. Restart Claude Code

### If you get permission errors:

Run PowerShell as Administrator:
```powershell
# Right-click PowerShell → Run as Administrator
cd C:\Users\trist\crypto-skills-mcp
python scripts/post_install.py
```

### If validation still fails after all fixes:

Run the validation script with Python verbose mode:
```powershell
python -v scripts/validate_install.py
```

This will show detailed import information and help identify the issue.

## What Changed

**Commit `b1b48d1`:**
- Fixed validation script isinstance() bug
- Changed line 77 from `"type": "stdio"` to `"type": str`
- Validation script now works correctly without crashing

**Commit `f9d1069` (previous):**
- Fixed setup.py to use absolute paths
- Added comprehensive error handling
- Created validation script (with the bug we just fixed)

## Summary

1. ✅ Validation script bug is FIXED
2. ⚠️ Your .claude.json needs updating
3. 📋 Run `python scripts/post_install.py` to update
4. 🔄 Restart Claude Code
5. ✅ Should connect successfully

If you still have issues after following these steps, please report back with the exact error messages from the validation script.
