# winterm2 Command Cheat Sheet

Quick reference for all winterm2 commands.

## Installation

```powershell
# pip
pip install winterm2

# pipx
pipx install winterm2

# Scoop
scoop install winterm2

# Chocolatey
choco install winterm2
```

---

## Window Management

| Command | Description |
|---------|-------------|
| `wt2 window new --profile <name>` | Create new window |
| `wt2 window new --profile PowerShell --maximize` | Create maximized window |
| `wt2 window new --profile Ubuntu --cwd /home/user` | Create window with WSL |
| `wt2 window list` | List all windows |

---

## Tab Management

| Command | Description |
|---------|-------------|
| `wt2 tab new --profile <name>` | Create new tab |
| `wt2 tab new --window 2 --profile Ubuntu` | Create tab in specific window |
| `wt2 tab new --profile PowerShell --title "Server"` | Create tab with custom title |
| `wt2 tab list` | List all tabs |

---

## Pane Management

### Splitting

| Command | Description |
|---------|-------------|
| `wt2 pane split` | Split horizontally (pane below) |
| `wt2 pane vsplit` | Split vertically (pane right) |
| `wt2 pane split --size 30` | Split with 30% size |
| `wt2 pane vsplit --profile Ubuntu` | Split with specific profile |

### Resizing

| Command | Description |
|---------|-------------|
| `wt2 resize --width 120 --height 40` | Resize to specific cells |
| `wt2 resize --width 50% --height 50%` | Resize to percentage |
| `wt2 resize --width 80 --pane 3` | Resize specific pane |

### Closing

| Command | Description |
|---------|-------------|
| `wt2 pane close` | Close current pane |
| `wt2 pane close --pane 3` | Close specific pane |
| `wt2 pane close --force` | Force close without prompt |

---

## Navigation

| Command | Description |
|---------|-------------|
| `wt2 focus up` | Focus pane above |
| `wt2 focus down` | Focus pane below |
| `wt2 focus left` | Focus pane left |
| `wt2 focus right` | Focus pane right |

---

## Session Control

### Running Commands

| Command | Description |
|---------|-------------|
| `wt2 run "<command>"` | Run command in new pane |
| `wt2 run "npm test"` | Run npm test |
| `wt2 run "dir" --wait` | Run and wait for completion |
| `wt2 run "script.py" --cwd D:\Scripts` | Run in specific directory |

### Sending Commands

| Command | Description |
|---------|-------------|
| `wt2 send "dir"` | Send text to pane |
| `wt2 send "git status"` | Send git command |
| `wt2 send "Ctrl+C"` | Send Ctrl+C |

### Clearing

| Command | Description |
|---------|-------------|
| `wt2 clear` | Clear visible content |
| `wt2 clear --scrollback` | Clear and erase history |

### Listing

| Command | Description |
|---------|-------------|
| `wt2 list` | List all windows/tabs/panes |
| `wt2 list --format json` | Output as JSON |
| `wt2 list --filter tabs` | List only tabs |
| `wt2 list --filter panes` | List only panes |

---

## Broadcasting

| Command | Description |
|---------|-------------|
| `wt2 broadcast on` | Enable broadcast mode |
| `wt2 broadcast off` | Disable broadcast mode |
| `wt2 broadcast send "cmd"` | Send to broadcast targets |
| `wt2 broadcast send "npm test" --all` | Send to all windows |

---

## Monitoring

| Command | Description |
|---------|-------------|
| `wt2 follow` | Follow current pane output |
| `wt2 follow --keyword ERROR` | Filter output by keyword |
| `wt2 follow --pane 3` | Follow specific pane |
| `wt2 follow --timeout 60` | Follow for 60 seconds |

---

## Configuration

| Command | Description |
|---------|-------------|
| `wt2 load <profile>` | Load configuration profile |
| `wt2 save <profile>` | Save current layout |
| `wt2 save my-setup --description "My setup"` | Save with description |
| `wt2 save team-config --global` | Save to global config |
| `wt2 config --edit` | Edit configuration file |
| `wt2 config --path` | Show config file path |

---

## Command Shorthands

| Full Command | Alias | Description |
|--------------|-------|-------------|
| `wt2 window new` | `wt2 wn` | New window |
| `wt2 tab new` | `wt2 tn` | New tab |
| `wt2 pane split` | `wt2 ps` | Horizontal split |
| `wt2 pane vsplit` | `wt2 pvs` | Vertical split |
| `wt2 pane close` | `wt2 pc` | Close pane |
| `wt2 focus up` | `wt2 fu` | Focus up |
| `wt2 focus down` | `wt2 fd` | Focus down |
| `wt2 focus left` | `wt2 fl` | Focus left |
| `wt2 focus right` | `wt2 fr` | Focus right |
| `wt2 broadcast on` | `wt2 bon` | Broadcast on |
| `wt2 broadcast off` | `wt2 boff` | Broadcast off |
| `wt2 list` | `wt2 ls` | List sessions |

---

## Global Options

| Option | Description |
|--------|-------------|
| `--help, -h` | Show help |
| `--version, -v` | Show version |
| `--debug` | Enable debug output |
| `--profile <name>` | Specify profile |
| `--cwd <path>` | Set working directory |
| `--wait` | Wait for completion |

---

## Error Codes

| Code | Name | Meaning |
|------|------|---------|
| 0 | SUCCESS | Operation succeeded |
| 1 | GENERAL_ERROR | Unspecified error |
| 2 | CONNECTION_ERROR | Cannot connect to WT |
| 3 | TARGET_NOT_FOUND | Window/tab/pane missing |
| 4 | INVALID_ARGUMENT | Bad command syntax |
| 5 | PERMISSION_DENIED | Admin required |
| 6 | TIMEOUT_ERROR | Operation timed out |
| 7 | CONFIG_ERROR | Config file error |

---

## Common Workflows

### Create Development Environment

```powershell
wt2 window new --profile PowerShell --title "Dev"
wt2 pane vsplit --profile Ubuntu
wt2 focus right
wt2 pane split --profile PowerShell
```

### Multi-Pane Git Operations

```powershell
wt2 broadcast on
wt2 broadcast send "git status"
wt2 broadcast send "git pull"
wt2 broadcast off
```

### Monitor Server Logs

```powershell
wt2 follow --keyword "ERROR" --timeout 120
```

### Save and Load Layouts

```powershell
# Save current setup
wt2 save full-dev --description "Full dev layout"

# Later, restore
wt2 load full-dev
```

---

## File Locations

| Path | Purpose |
|------|---------|
| `%APPDATA%\winterm2\config.json` | User configuration |
| `%LOCALAPPDATA%\winterm2\logs\` | Log files |
| `%LOCALAPPDATA%\winterm2\cache\` | Cache directory |

---

## Keyboard Shortcuts (Windows Terminal)

| Shortcut | Action |
|----------|--------|
| `Ctrl+Shift+T` | New tab |
| `Ctrl+Shift+N` | New window |
| `Ctrl+Shift+D` | Split pane (horizontal) |
| `Ctrl+Shift+E` | Split pane (vertical) |
| `Alt+Arrow` | Move focus |
| `Ctrl+Shift+W` | Close pane |

---

## Quick Examples

### Open and split
```powershell
wt2 wn -p PowerShell && wt2 pvs && wt2 ps
```

### Broadcast update
```powershell
wt2 bon && wt2 bsend "npm test" && wt2 boff
```

### Follow logs
```powershell
wt2 follow -k "ERROR" -t 60
```

### Save/load setup
```powershell
wt2 save my-layout && wt2 load my-layout
```

---

## Getting Help

```powershell
# General help
wt2 --help

# Command-specific help
wt2 window --help
wt2 tab --help
wt2 pane --help
wt2 broadcast --help
```
