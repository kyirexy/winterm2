# winterm2 Help Documentation Structure

This document defines the standardized help documentation structure for all winterm2 commands.

## Help Output Standards

All winterm2 commands must follow this consistent help structure:

```
NAME
    <command> - Brief one-line description

SYNOPSIS
    <command> [arguments] [options]

DESCRIPTION
    Detailed paragraph explaining what the command does.
    May span multiple lines.

ARGUMENTS
    <arg>       Description of positional argument (if any)

OPTIONS
    -s, --short     Short option description
    --long          Long option description
    -v, --verbose   Verbose option with value: <type>

EXAMPLES
    $ <example command>
    Output description (prefixed with #)

    $ <example command>
    Output description (prefixed with #)

SEE ALSO
    <related-command>, <related-command>
```

---

## Window Management Commands

### wt2 window new

```
NAME
    wt2 window new - Create a new Windows Terminal window

SYNOPSIS
    wt2 window new --profile <name> [--cwd <path>] [--maximize] [--fullscreen]

DESCRIPTION
    Creates and opens a new Windows Terminal window with the specified profile.
    The new window becomes the active window.

ARGUMENTS
    None (all options are flags/flags with values)

OPTIONS
    -p, --profile <name>
        Terminal profile name to use for the new window.
        Required. Available profiles: PowerShell, Command Prompt, Ubuntu, etc.

    -d, --cwd <path>
        Starting working directory for the new window.
        Optional. Default: User's home directory

    -m, --maximize
        Open the window in maximized mode.
        Optional. Default: false

    -f, --fullscreen
        Open the window in fullscreen mode.
        Optional. Default: false

EXAMPLES
    $ wt2 window new --profile "PowerShell"
    # Opens new PowerShell window

    $ wt2 window new --profile "Ubuntu" --cwd "/home/user"
    # Opens new Ubuntu WSL window in /home/user

    $ wt2 window new --profile "Command Prompt" --maximize
    # Opens new maximized CMD window

SEE ALSO
    wt2-tab-new, wt2-list
```

### wt2 tab new

```
NAME
    wt2 tab new - Create a new tab in the current or specified window

SYNOPSIS
    wt2 tab new [--window <id>] --profile <name> [--cwd <path>] [--title <title>]

DESCRIPTION
    Creates a new tab in the specified window. If no window is specified,
    the tab is created in the current active window.

ARGUMENTS
    None (all options are flags/flags with values)

OPTIONS
    -w, --window <id>
        Target window ID for the new tab.
        Optional. Default: Current active window

    -p, --profile <name>
        Terminal profile name for the new tab.
        Required.

    -d, --cwd <path>
        Starting working directory for the new tab.
        Optional. Default: Current directory or profile default

    -t, --title <title>
        Custom title displayed in the tab.
        Optional. Default: Profile name

EXAMPLES
    $ wt2 tab new --profile "PowerShell"
    # Creates new PowerShell tab

    $ wt2 tab new --window 2 --profile "Ubuntu" --title "Dev"
    # Creates new Ubuntu tab in window 2 with title "Dev"

    $ wt2 tab new --profile "Command Prompt" --cwd "D:\Projects"
    # Creates new CMD tab in D:\Projects

SEE ALSO
    wt2-window-new, wt2-list, wt2-pane-split
```

---

## Pane Management Commands

### wt2 pane split

```
NAME
    wt2 pane split - Split the current pane horizontally

SYNOPSIS
    wt2 pane split [--profile <name>] [--cwd <path>] [--size <value>]

DESCRIPTION
    Splits the current pane horizontally, creating a new pane below.
    The new pane inherits the current profile and working directory
    unless overridden.

ARGUMENTS
    None (all options are flags/flags with values)

OPTIONS
    -p, --profile <name>
        Terminal profile for the new pane.
        Optional. Default: Current pane's profile

    -d, --cwd <path>
        Working directory for the new pane.
        Optional. Default: Current pane's directory

    -s, --size <value>
        Size of the new pane as percentage or cell count.
        Optional. Default: 50

EXAMPLES
    $ wt2 pane split --profile "PowerShell"
    # Splits horizontally, opens PowerShell in new pane

    $ wt2 pane split --size 30
    # Splits with 30% size for new pane

    $ wt2 pane split --cwd "D:\Projects"
    # Splits and opens new pane in D:\Projects

SEE ALSO
    wt2-pane-vsplit, wt2-pane-close, wt2-focus
```

### wt2 pane vsplit

```
NAME
    wt2 pane vsplit - Split the current pane vertically

SYNOPSIS
    wt2 pane vsplit [--profile <name>] [--cwd <path>] [--size <value>]

DESCRIPTION
    Splits the current pane vertically, creating a new pane to the right.
    The new pane inherits the current profile and working directory
    unless overridden.

ARGUMENTS
    None (all options are flags/flags with values)

OPTIONS
    -p, --profile <name>
        Terminal profile for the new pane.
        Optional. Default: Current pane's profile

    -d, --cwd <path>
        Working directory for the new pane.
        Optional. Default: Current pane's directory

    -s, --size <value>
        Size of the new pane as percentage or cell count.
        Optional. Default: 50

EXAMPLES
    $ wt2 pane vsplit --profile "Ubuntu"
    # Splits vertically, opens Ubuntu WSL in new pane

    $ wt2 pane vsplit --size 40
    # Splits with 40% size for new pane

SEE ALSO
    wt2-pane-split, wt2-pane-close, wt2-focus
```

### wt2 pane close

```
NAME
    wt2 pane close - Close the current or specified pane

SYNOPSIS
    wt2 pane close [--pane <id>] [--force]

DESCRIPTION
    Closes the specified pane. If no pane is specified, closes the
    currently focused pane. A confirmation prompt appears unless
    --force is specified.

ARGUMENTS
    None (all options are flags/flags with values)

OPTIONS
    -p, --pane <id>
        ID of the pane to close.
        Optional. Default: Current focused pane

    -f, --force
        Close without confirmation prompt.
        Optional. Default: false

EXAMPLES
    $ wt2 pane close
    # Closes current pane (with confirmation)

    $ wt2 pane close --pane 3
    # Closes pane 3 (with confirmation)

    $ wt2 pane close --pane 3 --force
    # Force closes pane 3 without confirmation

SEE ALSO
    wt2-pane-split, wt2-tab-close
```

### wt2 focus

```
NAME
    wt2 focus - Focus on a pane in the specified direction

SYNOPSIS
    wt2 focus <direction>

DESCRIPTION
    Moves keyboard focus to the adjacent pane in the specified direction.
    Works with split panes created by wt2 pane split/vsplit.

ARGUMENTS
    direction
        Direction to move focus: up, down, left, or right.
        Required.

EXAMPLES
    $ wt2 focus up
    # Moves focus to pane above

    $ wt2 focus right
    # Moves focus to pane on the right

    $ wt2 focus down
    # Moves focus to pane below

ERRORS
    3.3 - PANE_NOT_FOUND    No pane exists in that direction
    4.6 - INVALID_DIRECTION  Invalid direction specified

SEE ALSO
    wt2-pane-split, wt2-pane-vsplit
```

### wt2 resize

```
NAME
    wt2 resize - Resize the current pane

SYNOPSIS
    wt2 resize --width <size> --height <size> [--pane <id>]

DESCRIPTION
    Resizes the current or specified pane to the given dimensions.
    Accepts either absolute cell counts or percentage values.

ARGUMENTS
    None (all options are flags/flags with values)

OPTIONS
    -w, --width <size>
        New width: number of cells (10-500) or percentage (10%-100%).
        Required.

    -h, --height <size>
        New height: number of cells (10-200) or percentage (10%-100%).
        Required.

    -p, --pane <id>
        ID of the pane to resize.
        Optional. Default: Current focused pane

EXAMPLES
    $ wt2 resize --width 120 --height 40
    # Resizes to 120x40 cells

    $ wt2 resize --width 50% --height 50%
    # Resizes to 50% width and 50% height

ERRORS
    4.3 - INVALID_RANGE  Size value out of valid range
    4.4 - INVALID_SIZE  Malformed size specification

SEE ALSO
    wt2-focus, wt2-list
```

---

## Session Control Commands

### wt2 send

```
NAME
    wt2 send - Send a command to the focused pane

SYNOPSIS
    wt2 send "<command>"

DESCRIPTION
    Sends the specified command text to the focused pane.
    Does NOT append Enter (Enter must be sent separately or use wt2 run).

ARGUMENTS
    command
        Command text to send.
        Required.

EXAMPLES
    $ wt2 send "dir"
    # Sends "dir" (without Enter)

    $ wt2 send "git commit -m 'fix: bug'"
    # Sends command with spaces and quotes

NOTES
    - Use wt2 send for commands that need further editing
    - Use wt2 run for commands that should execute immediately
    - Special characters can be escaped with \

SEE ALSO
    wt2-run, wt2-broadcast-send
```

### wt2 run

```
NAME
    wt2 run - Run a command in a new pane

SYNOPSIS
    wt2 run "<command>" [--profile <name>] [--cwd <path>] [--wait]

DESCRIPTION
    Executes the specified command in a new pane. The command runs
    immediately (Enter is sent automatically).

ARGUMENTS
    command
        Command to execute.
        Required.

OPTIONS
    -p, --profile <name>
        Terminal profile for the new pane.
        Optional. Default: Current profile

    -d, --cwd <path>
        Working directory for the new pane.
        Optional. Default: Current directory

    -w, --wait
        Wait for command to complete before returning.
        Optional. Default: false

EXAMPLES
    $ wt2 run "npm test"
    # Runs npm test in new pane

    $ wt2 run "pip install -r requirements.txt" --wait
    # Installs dependencies and waits for completion

    $ wt2 run "python script.py" --cwd "D:\Scripts"
    # Runs script in specified directory

SEE ALSO
    wt2-send, wt2-pane-split
```

### wt2 clear

```
NAME
    wt2 clear - Clear the pane buffer

SYNOPSIS
    wt2 clear [--scrollback]

DESCRIPTION
    Clears the visible content in the current pane. Optionally clears
    the scrollback history.

ARGUMENTS
    None (all options are flags/flags with values)

OPTIONS
    -s, --scrollback
        Also clear the scrollback (history) buffer.
        Optional. Default: false

EXAMPLES
    $ wt2 clear
    # Clears visible content

    $ wt2 clear --scrollback
    # Clears visible content and history

NOTES
    - This sends Ctrl+L (clear) to the terminal
    - May not work identically across all shells

SEE ALSO
    wt2-list
```

### wt2 list

```
NAME
    wt2 list - List all windows, tabs, and panes

SYNOPSIS
    wt2 list [--format <json|table>] [--filter <type>]

DESCRIPTION
    Displays all open Windows Terminal windows, tabs, and panes.
    Useful for identifying IDs for other commands.

ARGUMENTS
    None (all options are flags/flags with values)

OPTIONS
    -f, --format <format>
        Output format: json or table.
        Optional. Default: table

    -t, --filter <type>
        Filter output: windows, tabs, or panes.
        Optional. Default: all

EXAMPLES
    $ wt2 list
    # Lists all in table format

    $ wt2 list --format json
    # Lists all in JSON format

    $ wt2 list --filter tabs
    # Lists only tabs

OUTPUT FIELDS
    Window ID, Tab ID, Pane ID, Profile, Title, Working Directory

SEE ALSO
    wt2-focus, wt2-config
```

---

## Batch Broadcasting Commands

### wt2 broadcast on

```
NAME
    wt2 broadcast on - Enable broadcast mode

SYNOPSIS
    wt2 broadcast on [--groups <group1,group2>]

DESCRIPTION
    Enables broadcast mode for synchronized input to multiple panes.
    When enabled, commands sent via wt2 send or wt2 run go to all
    broadcast targets.

ARGUMENTS
    None (all options are flags/flags with values)

OPTIONS
    -g, --groups <groups>
        Comma-separated list of pane groups to broadcast to.
        Optional. Default: All panes in current window

EXAMPLES
    $ wt2 broadcast on
    # Enables broadcast to all panes

    $ wt2 broadcast on --groups frontend,backend
    # Enables broadcast to specific groups

EXIT CODES
    0 - Broadcast mode enabled successfully
    2.1 - Windows Terminal not running

SEE ALSO
    wt2-broadcast-off, wt2-broadcast-send
```

### wt2 broadcast off

```
NAME
    wt2 broadcast off - Disable broadcast mode

SYNOPSIS
    wt2 broadcast off

DESCRIPTION
    Disables broadcast mode. After disabling, commands target only
    the focused pane.

ARGUMENTS
    None

EXAMPLES
    $ wt2 broadcast off
    # Disables broadcast mode

SEE ALSO
    wt2-broadcast-on
```

### wt2 broadcast send

```
NAME
    wt2 broadcast send - Send command to all broadcast targets

SYNOPSIS
    wt2 broadcast send "<command>" [--all] [--groups <groups>]

DESCRIPTION
    Sends a command to all broadcast targets without enabling
    persistent broadcast mode.

ARGUMENTS
    command
        Command to send to all targets.
        Required.

OPTIONS
    -a, --all
        Send to all panes in all windows.
        Optional. Default: Current window only

    -g, --groups <groups>
        Comma-separated list of pane groups.
        Optional. Default: All panes in current window

EXAMPLES
    $ wt2 broadcast send "git status"
    # Sends to all panes in current window

    $ wt2 broadcast send "npm test" --all
    # Sends to all panes in all windows

    $ wt2 broadcast send "docker-compose up" --groups backend
    # Sends to specific group

SEE ALSO
    wt2-broadcast-on, wt2-send
```

---

## Real-time Monitoring Commands

### wt2 follow

```
NAME
    wt2 follow - Follow pane output in real-time

SYNOPSIS
    wt2 follow [--pane <id>] [--keyword <pattern>] [--timeout <seconds>]

DESCRIPTION
    Displays output from the specified pane in real-time.
    Useful for monitoring long-running commands.

ARGUMENTS
    None (all options are flags/flags with values)

OPTIONS
    -p, --pane <id>
        ID of the pane to follow.
        Optional. Default: Current focused pane

    -k, --keyword <pattern>
        Filter output to lines containing this keyword.
        Optional. Default: All output

    -t, --timeout <seconds>
        Stop following after specified seconds.
        Optional. Default: No timeout (Ctrl+C to exit)

EXAMPLES
    $ wt2 follow
    # Follows current pane

    $ wt2 follow --keyword "ERROR"
    # Follows and shows only ERROR lines

    $ wt2 follow --pane 3 --timeout 60
    # Follows pane 3 for 60 seconds

KEYBOARD INPUT
    Ctrl+C    Stop following
    Ctrl+F    Search in output
    /pattern  Jump to pattern

SEE ALSO
    wt2-run, wt2-list
```

---

## Configuration Commands

### wt2 load

```
NAME
    wt2 load - Load a saved configuration profile

SYNOPSIS
    wt2 load <profile> [--global]

DESCRIPTION
    Loads a previously saved configuration profile. Profiles can
    contain window layouts, pane arrangements, and settings.

ARGUMENTS
    profile
        Name of the profile to load.
        Required.

OPTIONS
    -g, --global
        Load from global configuration instead of user config.
        Optional. Default: User configuration

EXAMPLES
    $ wt2 load dev
    # Loads user profile 'dev'

    $ wt2 load production --global
    # Loads global profile 'production'

ERRORS
    3.5 - PROFILE_NOT_FOUND    Profile does not exist
    7.3 - CONFIG_READ_ERROR    Cannot read config file

SEE ALSO
    wt2-save, wt2-config
```

### wt2 save

```
NAME
    wt2 save - Save current configuration as a profile

SYNOPSIS
    wt2 save <profile> [--global] [--description <text>]

DESCRIPTION
    Saves the current window layout and settings as a named profile.
    Profiles can be loaded later with wt2 load.

ARGUMENTS
    profile
        Name for the new profile.
        Required.

OPTIONS
    -g, --global
        Save to global configuration (requires admin).
        Optional. Default: User configuration

    -d, --description <text>
        Description for the profile.
        Optional.

EXAMPLES
    $ wt2 save my-dev-setup --description "My development layout"
    # Saves as user profile

    $ wt2 save team-config --global --description "Team standard layout"
    # Saves as global profile

SAVED CONTENT
    - Window count and arrangement
    - Tab layouts and profiles
    - Pane splits and sizes
    - Custom titles

SEE ALSO
    wt2-load, wt2-config
```

### wt2 config

```
NAME
    wt2 config - Manage winterm2 configuration

SYNOPSIS
    wt2 config --edit [--path <path>]

DESCRIPTION
    Opens the winterm2 configuration file for editing or displays
    the configuration file path.

ARGUMENTS
    None (all options are flags/flags with values)

OPTIONS
    -e, --edit
        Open configuration file in default editor.
        Optional.

    -p, --path
        Display path to configuration file.
        Optional.

EXAMPLES
    $ wt2 config --edit
    # Opens config file in editor

    $ wt2 config --path
    # Displays: C:\Users\user\.config\winterm2\config.json

CONFIG FILE LOCATION
    User:    %APPDATA%\winterm2\config.json
    Global:  %PROGRAMDATA%\winterm2\config.json

SEE ALSO
    wt2-load, wt2-save
```

---

## Global Help

### wt2 --help

```
NAME
    wt2 - Windows Terminal Automation CLI

SYNOPSIS
    wt2 [--version] [--help]
    wt2 <command> [<args>]

DESCRIPTION
    winterm2 is a command-line interface for automating Windows Terminal,
    PowerShell 7+, CMD, and WSL2. It provides window, tab, and pane
    management, real-time monitoring, and batch broadcasting.

COMMANDS
    window      Window management
    tab         Tab management
    pane        Pane management (split, close, resize)
    focus       Focus pane in direction
    send        Send command to pane
    run         Run command in new pane
    clear       Clear pane buffer
    list        List windows/tabs/panes
    broadcast   Batch broadcasting
    follow      Real-time monitoring
    load        Load configuration
    save        Save configuration
    config      Edit configuration

OPTIONS
    -V, --version
        Show version information

    -h, --help
        Show this help message

    -d, --debug
        Enable debug output

EXIT CODES
    0   Success
    1   General error
    2   Connection error
    3   Target not found
    4   Invalid argument
    5   Permission denied

FILES
    Config:  %APPDATA%\winterm2\config.json
    Cache:   %LOCALAPPDATA%\winterm2\cache
    Logs:    %LOCALAPPDATA%\winterm2\logs

EXAMPLES
    $ wt2 window new --profile PowerShell
    # Create new window

    $ wt2 tab new --profile Ubuntu
    # Create new tab

    $ wt2 pane split --profile PowerShell
    # Split pane horizontally

SEE ALSO
    https://github.com/winterm2/winterm2
```

---

## Help Output Format Specification

### Required Elements

Every help output must include:

1. **NAME** section with command name and one-line summary
2. **SYNOPSIS** showing full command syntax
3. **DESCRIPTION** with detailed explanation
4. **ARGUMENTS** section (if command has positional args)
5. **OPTIONS** section with all flags and their descriptions
6. **EXAMPLES** section with at least 2 usage examples
7. **SEE ALSO** section with related commands

### Formatting Standards

- Section headers: ALL CAPS, bold in markdown
- Option flags: `-s, --short` format
- Code blocks: triple backticks
- Comments in examples: prefixed with `#`
- Required items: clearly marked
- Default values: shown when applicable

### Output to User

When users run `<command> --help`, show only the NAME, SYNOPSIS,
DESCRIPTION, ARGUMENTS, OPTIONS, and EXAMPLES sections.
Exclude SEE ALSO from inline help.
