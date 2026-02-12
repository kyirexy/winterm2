# winterm2 Quick Start Guide

Get started with winterm2 in 5 minutes.

## First Steps

### 1. Verify Installation

```powershell
wt2 --version
```

Expected output:
```
winterm2 2.0.0
```

### 2. List Current Windows

```powershell
wt2 list
```

Expected output:
```
Windows Terminal Sessions

Window ID  Tab ID  Profile        Title        Status
------------------------------------------------------------
1          1       PowerShell     PowerShell   Active
```

---

## Basic Operations

### Create a New Window

```powershell
# Create new window with PowerShell (default)
wt2 window new

# Create new window with specific profile
wt2 window new --profile "Ubuntu"

# Create new window in specific directory
wt2 window new --profile "Command Prompt" --cwd "D:\Projects"
```

### Create a New Tab

```powershell
# Create new tab in current window
wt2 tab new --profile "PowerShell"

# Create new tab in different window
wt2 tab new --window 1 --profile "Ubuntu" --title "Dev"

# Create tab with custom working directory
wt2 tab new --profile "PowerShell" --cwd "D:\Projects\myapp"
```

### Split Panes

```powershell
# Horizontal split (pane below)
wt2 pane split --profile "PowerShell"

# Vertical split (pane to the right)
wt2 pane vsplit --profile "Ubuntu"

# Split with custom size
wt2 pane split --size 30
```

### Navigate Panes

```powershell
# Focus pane above/below/left/right
wt2 focus up
wt2 focus down
wt2 focus left
wt2 focus right
```

---

## Real-World Examples

### Example 1: Development Setup

Create a typical development environment with multiple panes:

```powershell
# Step 1: Create new window with PowerShell
wt2 window new --profile "PowerShell" --title "Dev"

# Step 2: Split vertically for code editor
wt2 pane vsplit --profile "PowerShell"

# Step 3: Split horizontally for terminal
wt2 focus right
wt2 pane split --profile "Ubuntu"

# Step 4: Open project in Ubuntu pane
wt2 run --cwd "D:\Projects\myapp" --profile "Ubuntu" --wait
```

### Example 2: Docker Development Environment

Set up containers and development tools:

```powershell
# Create new tab for Docker
wt2 tab new --profile "PowerShell" --title "Docker"

# Start Docker containers
wt2 run "docker-compose up -d" --wait

# Create monitoring pane
wt2 pane vsplit --profile "PowerShell"
wt2 send "docker-compose logs -f"
```

### Example 3: Multi-Service Monitoring

Monitor multiple services across panes:

```powershell
# Enable broadcast mode
wt2 broadcast on

# Send status check to all panes
wt2 broadcast send "pm2 list"

# Follow output
wt2 follow --keyword "online"
```

---

## Sending Commands

### wt2 send vs wt2 run

```powershell
# send - Sends text, waits for you to press Enter
wt2 send "git status"

# run - Executes immediately in new pane
wt2 run "git status"
```

### Sending Complex Commands

```powershell
# Command with quotes
wt2 run "python -c 'print(\"hello\")'"

# Multi-line command
wt2 send "git add . && git commit -m 'update'"

# Piped command
wt2 run "npm test | Out-File results.txt"
```

---

## Configuration Profiles

### Save Current Layout

```powershell
# Save current window setup
wt2 save dev-layout --description "My development layout"

# Save to global config (admin required)
wt2 save team-layout --global --description "Team standard"
```

### Load Saved Layout

```powershell
# Load user profile
wt2 load dev-layout

# Load global profile
wt2 load team-layout --global
```

---

## Batch Operations

### Broadcast to All Panes

```powershell
# Enable broadcast
wt2 broadcast on

# Send command to all panes
wt2 send "cd /repo/project"

# Run command in all panes
wt2 run "npm install"

# Disable broadcast
wt2 broadcast off
```

### Send to All Windows

```powershell
# Send command to all panes in all windows
wt2 broadcast send "git fetch --all" --all
```

---

## Monitoring Output

### Follow Real-time Output

```powershell
# Follow current pane
wt2 follow

# Follow with keyword filter
wt2 follow --keyword "ERROR"
wt2 follow --keyword "warning"

# Follow for specific duration
wt2 follow --timeout 30
```

### Clear Pane

```powershell
# Clear visible content
wt2 clear

# Clear with scrollback history
wt2 clear --scrollback
```

---

## Scripting Examples

### Batch Script (.bat)

```batch
@echo off
REM Create development environment

echo Creating new window...
wt2 window new --profile "PowerShell" --title "DevEnv"

echo Splitting panes...
wt2 pane vsplit --profile "PowerShell"
wt2 focus right
wt2 pane split --profile "Ubuntu"

echo Starting services...
wt2 run "npm install" --wait
wt2 run "docker-compose up -d" --wait

echo Done!
```

### PowerShell Script

```powershell
# Create development environment
param(
    [string]$ProjectPath = "D:\Projects\myapp"
)

# Create window
wt2 window new --profile "PowerShell" --title "Dev - $ProjectPath"

# Setup panes
wt2 pane vsplit --profile "PowerShell"
wt2 focus right
wt2 pane split --profile "Ubuntu"

# Navigate to project
wt2 run "cd '$ProjectPath'; pwd"

Write-Host "Development environment ready!"
```

---

## Common Tasks

### Task: Restart All Docker Containers

```powershell
wt2 broadcast on
wt2 broadcast send "docker-compose restart"
wt2 broadcast off
```

### Task: Git Pull All Repositories

```powershell
# Assuming each pane is a different project
wt2 broadcast on
wt2 broadcast send "git pull"
wt2 broadcast off
```

### Task: Quick Server Restart

```powershell
# Stop server
wt2 send "Ctrl+C"

# Wait a moment
Start-Sleep -Seconds 1

# Restart
wt2 run "npm run dev"
```

### Task: Copy File to All WSL Instances

```powershell
# Copy file to each pane's working directory
wt2 broadcast send "cp /mnt/c/temp/config.yaml ~/config/"
```

---

## Tips and Best Practices

1. **Use aliases for frequently used commands:**
   ```powershell
   # In your $PROFILE
   Set-Alias wn wt2\window\new
   Set-Alias tn wt2\tab\new
   Set-Alias ps wt2\pane_split
   ```

2. **Save complex layouts as profiles:**
   ```powershell
   wt2 save full-dev --description "Full development setup"
   ```

3. **Use broadcast for parallel operations:**
   ```powershell
   wt2 broadcast on
   wt2 broadcast send "npm test"
   ```

4. **Check connection before running commands:**
   ```powershell
   wt2 list > $null
   if ($LASTEXITCODE -ne 0) { Write-Error "WT not running" }
   ```

5. **Use --wait for long-running commands:**
   ```powershell
   wt2 run "pip install -r requirements.txt" --wait
   ```

---

## Next Steps

- Read the [CLI Specification](CLI_SPECIFICATION.md) for complete command reference
- Check [Error Codes](ERROR_CODES.md) for troubleshooting
- See [Cheat Sheet](README_CHEATSHEET.md) for quick reference
- Visit [GitHub](https://github.com/winterm2/winterm2) for updates
