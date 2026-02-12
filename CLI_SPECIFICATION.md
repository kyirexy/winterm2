# winterm2 CLI Specification

A Windows-native CLI tool for automating Windows Terminal, PowerShell 7+, CMD, and WSL2.

## Command Syntax

winterm2 uses a hierarchical command structure inspired by iterm2 (it2) but adapted for Windows Terminal.

### Global Options

| Option | Description |
|--------|-------------|
| `--help, -h` | Show help message |
| `--version, -v` | Show version information |
| `--profile <name>` | Specify the terminal profile to use |
| `--cwd <path>` | Set working directory for new sessions |
| `--wait` | Wait for pane/window to close before returning |

---

## Window Management

### wt2 window new

Create a new Windows Terminal window.

```bash
wt2 window new --profile <name> [--cwd <path>] [--maximize] [--fullscreen]
```

**Arguments:**

| Argument | Description |
|----------|-------------|
| `--profile, -p` | Terminal profile name (e.g., PowerShell, Command Prompt, Ubuntu) |
| `--cwd, -d` | Starting working directory |
| `--maximize, -m` | Open window maximized |
| `--fullscreen, -f` | Open window in fullscreen mode |

**Examples:**

```bash
# Open new window with PowerShell profile
wt2 window new --profile "PowerShell"

# Open new window with WSL2 Ubuntu
wt2 window new --profile "Ubuntu" --cwd "/home/user"

# Open maximized window
wt2 window new --profile "Command Prompt" --maximize
```

---

## Tab Management

### wt2 tab new

Create a new tab in the current or specified window.

```bash
wt2 tab new [--window <id>] --profile <name> [--cwd <path>] [--title <title>]
```

**Arguments:**

| Argument | Description |
|----------|-------------|
| `--window, -w` | Target window ID (default: current window) |
| `--profile, -p` | Terminal profile name |
| `--cwd, -d` | Starting working directory |
| `--title, -t` | Custom tab title |

**Examples:**

```bash
# Create new tab in current window
wt2 tab new --profile "PowerShell"

# Create tab in specific window
wt2 tab new --window 1 --profile "Ubuntu"

# Create tab with custom title
wt2 tab new --profile "Command Prompt" --title "Build Server"
```

---

## Pane Management

### wt2 pane split

Split the current pane horizontally.

```bash
wt2 pane split [--profile <name>] [--cwd <path>]
```

**Arguments:**

| Argument | Description |
|----------|-------------|
| `--profile, -p` | Profile for new pane |
| `--cwd, -d` | Working directory for new pane |
| `--size, -s` | Size percentage or rows (default: 50) |

**Examples:**

```bash
# Split horizontally (creates pane below)
wt2 pane split --profile "PowerShell"

# Split with specific size
wt2 pane split --size 30
```

### wt2 pane vsplit

Split the current pane vertically.

```bash
wt2 pane vsplit [--profile <name>] [--cwd <path>]
```

**Arguments:**

| Argument | Description |
|----------|-------------|
| `--profile, -p` | Profile for new pane |
| `--cwd, -d` | Working directory for new pane |
| `--size, -s` | Size percentage or columns (default: 50) |

**Examples:**

```bash
# Split vertically (creates pane to the right)
wt2 pane vsplit --profile "PowerShell"

# Split with specific size
wt2 pane vsplit --size 40
```

### wt2 pane close

Close the current pane or specified pane.

```bash
wt2 pane close [--pane <id>] [--force]
```

**Arguments:**

| Argument | Description |
|----------|-------------|
| `--pane, -p` | Specific pane ID to close |
| `--force, -f` | Force close without confirmation |

**Examples:**

```bash
# Close current pane
wt2 pane close

# Close specific pane
wt2 pane close --pane 2

# Force close without confirmation
wt2 pane close --force
```

### wt2 focus

Focus on a pane in the specified direction.

```bash
wt2 focus <direction>
```

**Arguments:**

| Argument | Description |
|----------|-------------|
| `direction` | Target direction: `up`, `down`, `left`, `right` |

**Examples:**

```bash
# Focus pane above
wt2 focus up

# Focus pane to the right
wt2 focus right
```

### wt2 resize

Resize the current pane.

```bash
wt2 resize --width <size> --height <size> [--pane <id>]
```

**Arguments:**

| Argument | Description |
|----------|-------------|
| `--width, -w` | Width in cells or percentage (e.g., `80`, `50%`) |
| `--height, -h` | Height in cells or percentage (e.g., `40`, `50%`) |
| `--pane, -p` | Specific pane to resize |

**Examples:**

```bash
# Resize to specific dimensions
wt2 resize --width 120 --height 40

# Resize using percentages
wt2 resize --width 50% --height 50%
```

---

## Session Control

### wt2 send

Send a command to the focused pane without sending Enter.

```bash
wt2 send "<command>"
```

**Arguments:**

| Argument | Description |
|----------|-------------|
| `<command>` | Command text to send |

**Examples:**

```bash
# Send simple command
wt2 send "dir"

# Send command with special characters
wt2 send "git commit -m 'fix: update'"
```

### wt2 run

Run a command in a new pane and optionally wait for completion.

```bash
wt2 run "<command>" [--profile <name>] [--cwd <path>] [--wait]
```

**Arguments:**

| Argument | Description |
|----------|-------------|
| `<command>` | Command to execute |
| `--profile, -p` | Profile to use |
| `--cwd, -d` | Working directory |
| `--wait, -w` | Wait for command to complete |

**Examples:**

```bash
# Run command in new pane
wt2 run "npm test"

# Run and wait for completion
wt2 run "pip install -r requirements.txt" --wait
```

### wt2 clear

Clear the buffer in the current pane.

```bash
wt2 clear [--scrollback]
```

**Arguments:**

| Argument | Description |
|----------|-------------|
| `--scrollback, -s` | Also clear scrollback history |

**Examples:**

```bash
# Clear visible content
wt2 clear

# Clear entire scrollback
wt2 clear --scrollback
```

### wt2 list

List all windows, tabs, and panes.

```bash
wt2 list [--format <json|table>] [--filter <type>]
```

**Arguments:**

| Argument | Description |
|----------|-------------|
| `--format, -f` | Output format: `json` or `table` (default: table) |
| `--filter, -t` | Filter by type: `windows`, `tabs`, `panes` |

**Examples:**

```bash
# List all (default table format)
wt2 list

# List in JSON format
wt2 list --format json

# List only tabs
wt2 list --filter tabs
```

---

## Batch Broadcasting

### wt2 broadcast on

Enable broadcast mode for synchronized input.

```bash
wt2 broadcast on [--groups <group1,group2>]
```

**Arguments:**

| Argument | Description |
|----------|-------------|
| `--groups, -g` | Specific pane groups to broadcast to |

### wt2 broadcast off

Disable broadcast mode.

```bash
wt2 broadcast off
```

### wt2 broadcast send

Send command to all broadcast targets.

```bash
wt2 broadcast send "<command>" [--all] [--groups <group1,group2>]
```

**Arguments:**

| Argument | Description |
|----------|-------------|
| `--all, -a` | Send to all panes in all windows |
| `--groups, -g` | Send to specific pane groups |

**Examples:**

```bash
# Broadcast to all panes
wt2 broadcast send "git status" --all

# Broadcast to specific groups
wt2 broadcast send "npm test" --groups "frontend,backend"
```

---

## Real-time Monitoring

### wt2 follow

Follow output in real-time from the current or specified pane.

```bash
wt2 follow [--pane <id>] [--keyword <pattern>] [--timeout <seconds>]
```

**Arguments:**

| Argument | Description |
|----------|-------------|
| `--pane, -p` | Target pane ID |
| `--keyword, -k` | Filter output by keyword pattern |
| `--timeout, -t` | Stop after specified seconds |

**Examples:**

```bash
# Follow current pane output
wt2 follow

# Follow with keyword filter
wt2 follow --keyword "ERROR"

# Follow specific pane
wt2 follow --pane 2
```

---

## Configuration Management

### wt2 load

Load a saved configuration profile.

```bash
wt2 load <profile> [--global]
```

**Arguments:**

| Argument | Description |
|----------|-------------|
| `<profile>` | Profile name to load |
| `--global, -g` | Load from global configuration |

**Examples:**

```bash
# Load user profile
wt2 load dev

# Load global profile
wt2 load production --global
```

### wt2 save

Save current terminal layout or settings as a named profile.

```bash
wt2 save <profile> [--global] [--description <text>]
```

**Arguments:**

| Argument | Description |
|----------|-------------|
| `<profile>` | Profile name to save |
| `--global, -g` | Save to global configuration |
| `--description, -d` | Profile description |

**Examples:**

```bash
# Save current layout as user profile
wt2 save my-dev-setup --description "My development layout"

# Save to global profiles
wt2 save team-config --global
```

### wt2 config

Edit the winterm2 configuration file.

```bash
wt2 config --edit [--path <path>]
```

**Arguments:**

| Argument | Description |
|----------|-------------|
| `--edit, -e` | Open config file in editor |
| `--path, -p` | Show path to config file |

**Examples:**

```bash
# Edit configuration
wt2 config --edit

# Show config file path
wt2 config --path
```

---

## Command Shorthands

For frequent operations, winterm2 supports short aliases:

| Command | Alias | Description |
|---------|-------|-------------|
| `wt2 window new` | `wt2 wn` | Create new window |
| `wt2 tab new` | `wt2 tn` | Create new tab |
| `wt2 pane split` | `wt2 ps` | Horizontal split |
| `wt2 pane vsplit` | `wt2 pvs` | Vertical split |
| `wt2 pane close` | `wt2 pc` | Close pane |
| `wt2 focus up/down/left/right` | `wt2 fu/fd/fl/fr` | Focus direction |
| `wt2 broadcast on/off` | `wt2 bon/boff` | Broadcast mode |
| `wt2 list` | `wt2 ls` | List sessions |

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `WINTERM2_PROFILE` | Default profile to use |
| `WINTERM2_CONFIG` | Path to configuration file |
| `WTERM_PROPID` | Windows Terminal PID (auto-detected) |
