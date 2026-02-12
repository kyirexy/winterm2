# winterm2 Error Codes Reference

A comprehensive reference for all error codes returned by winterm2 commands.

## Error Code Overview

| Code | Name | Category |
|------|------|----------|
| 0 | `SUCCESS` | Success |
| 1 | `GENERAL_ERROR` | General Errors |
| 2 | `CONNECTION_ERROR` | Connection Errors |
| 3 | `TARGET_NOT_FOUND` | Target Errors |
| 4 | `INVALID_ARGUMENT` | Argument Errors |
| 5 | `PERMISSION_DENIED` | Permission Errors |
| 6 | `TIMEOUT_ERROR` | Timeout Errors |
| 7 | `CONFIG_ERROR` | Configuration Errors |

---

## Success (0)

### 0 - SUCCESS

Operation completed successfully.

**Example output:**
```
$ wt2 tab new --profile PowerShell
Tab created successfully in window 1 (ID: 3)
```

---

## General Errors (1)

### 1 - GENERAL_ERROR

An unspecified error occurred during operation.

**Common causes:**
- Unexpected exception
- Invalid state
- Resource exhaustion

**Example output:**
```
$ wt2 pane close
Error: Unable to close pane (Error code: 1)
Details: Unexpected error occurred while closing pane
```

### 1.1 - ALREADY_EXISTS

Attempted to create a resource that already exists.

**Example:**
```bash
# Trying to create a tab with an ID that already exists
$ wt2 tab new --id 3
Error: Tab with ID 3 already exists (Error code: 1.1)
```

### 1.2 - NOT_IMPLEMENTED

Feature not yet implemented.

**Example:**
```bash
$ wt2 broadcast send "test" --all
Error: Broadcast to all windows not yet implemented (Error code: 1.2)
```

### 1.3 - INTERRUPTED

Operation was interrupted by user or signal.

**Example:**
```bash
$ wt2 follow --keyword "ERROR"
Error: Monitoring interrupted (Error code: 1.3)
```

---

## Connection Errors (2)

### 2 - CONNECTION_ERROR

Unable to connect to Windows Terminal.

**Common causes:**
- Windows Terminal not running
- IPC communication failure
- Windows Terminal RPC server unavailable

**Example output:**
```
$ wt2 list
Error: Cannot connect to Windows Terminal (Error code: 2)
Details: Ensure Windows Terminal is running and RPC is enabled
```

### 2.1 - TERMINAL_NOT_RUNNING

Windows Terminal process is not running.

**Example:**
```bash
$ wt2 window new
Error: Windows Terminal is not running (Error code: 2.1)
Hint: Start Windows Terminal and try again
```

### 2.2 - RPC_UNAVAILABLE

Windows Terminal RPC interface is unavailable.

**Example:**
```bash
$ wt2 pane split
Error: Windows Terminal RPC interface unavailable (Error code: 2.2)
Hint: Ensure Windows Terminal version 1.12+ is installed
```

### 2.3 - SOCKET_ERROR

IPC socket connection failed.

**Example:**
```bash
$ wt2 list
Error: Cannot open IPC socket to Windows Terminal (Error code: 2.3)
Details: [Errno 111] Connection refused
```

### 2.4 - AUTHENTICATION_FAILED

IPC authentication failed.

**Example:**
```bash
$ wt2 config --edit
Error: IPC authentication failed (Error code: 2.4)
Hint: Restart Windows Terminal to reset IPC credentials
```

---

## Target Not Found Errors (3)

### 3 - TARGET_NOT_FOUND

The requested target (window/tab/pane) does not exist.

**Common causes:**
- Invalid ID specified
- Target was already closed
- Wrong window/tab number

**Example output:**
```
$ wt2 focus right --pane 999
Error: Pane not found (Error code: 3)
Details: Pane ID 999 does not exist
```

### 3.1 - WINDOW_NOT_FOUND

Specified window ID does not exist.

**Example:**
```bash
$ wt2 tab new --window 999
Error: Window 999 not found (Error code: 3.1)
Details: Available windows: 1, 2, 3
```

### 3.2 - TAB_NOT_FOUND

Specified tab ID does not exist.

**Example:**
```bash
$ wt2 close --tab 50
Error: Tab 50 not found (Error code: 3.2)
Details: Window 1 has tabs: 1, 2, 3
```

### 3.3 - PANE_NOT_FOUND

Specified pane ID does not exist.

**Example:**
```bash
$ wt2 resize --pane 100 --width 50
Error: Pane 100 not found (Error code: 3.3)
Hint: Use 'wt2 list --filter panes' to see available panes
```

### 3.4 - PROFILE_NOT_FOUND

Specified profile name does not exist.

**Example:**
```bash
$ wt2 window new --profile "NonExistent"
Error: Profile 'NonExistent' not found (Error code: 3.4)
Details: Available profiles: PowerShell, Command Prompt, Ubuntu, Debian
```

### 3.5 - PROFILE_NOT_FOUND

Specified configuration profile does not exist.

**Example:**
```bash
$ wt2 load my-config
Error: Configuration profile 'my-config' not found (Error code: 3.5)
Hint: Use 'wt2 save <name>' to create a profile first
```

---

## Invalid Argument Errors (4)

### 4 - INVALID_ARGUMENT

Invalid command-line argument or syntax error.

**Common causes:**
- Missing required argument
- Invalid flag combination
- Malformed argument value

**Example output:**
```
$ wt2 resize --width
Error: Invalid argument (Error code: 4)
Details: --width requires a value
```

### 4.1 - MISSING_REQUIRED_ARGUMENT

A required argument is missing.

**Example:**
```bash
$ wt2 window new
Error: Missing required argument --profile (Error code: 4.1)
Usage: wt2 window new --profile <name>
```

### 4.2 - INVALID_CHOICE

Argument value is not a valid choice.

**Example:**
```bash
$ wt2 list --format yaml
Error: Invalid format 'yaml' (Error code: 4.2)
Valid options: json, table
```

### 4.3 - INVALID_RANGE

Numeric argument is out of valid range.

**Example:**
```bash
$ wt2 resize --width 5000
Error: Width 5000 is out of valid range (Error code: 4.3)
Valid range: 10-500
```

### 4.4 - INVALID_SIZE

Size specification is malformed.

**Example:**
```bash
$ wt2 pane split --size abc
Error: Invalid size 'abc' (Error code: 4.4)
Valid formats: 10-100 (percentage) or 10-100 (cells)
```

### 4.5 - INVALID_PATTERN

Regex or glob pattern is invalid.

**Example:**
```bash
$ wt2 follow --keyword "["
Error: Invalid keyword pattern (Error code: 4.5)
Hint: Use --keyword "pattern" for simple matching or --regex for regex
```

### 4.6 - INVALID_DIRECTION

Focus direction is invalid.

**Example:**
```bash
$ wt2 focus diagonal
Error: Invalid direction 'diagonal' (Error code: 4.6)
Valid directions: up, down, left, right
```

### 4.7 - ARGUMENT_CONFLICT

Conflicting arguments provided.

**Example:**
```bash
$ wt2 run "cmd" --wait --background
Error: Conflicting arguments --wait and --background (Error code: 4.7)
Hint: Cannot wait and run in background simultaneously
```

---

## Permission Denied Errors (5)

### 5 - PERMISSION_DENIED

Operation requires elevated privileges.

**Common causes:**
- Admin operation without admin rights
- Protected resource access

**Example output:**
```
$ wt2 config --edit --system
Error: Permission denied (Error code: 5)
Details: System configuration requires administrator privileges
```

### 5.1 - ADMIN_REQUIRED

Operation requires administrator privileges.

**Example:**
```bash
$ wt2 install --system-service
Error: Administrator privileges required (Error code: 5.1)
Hint: Run as administrator or use --user flag
```

### 5.2 - FILE_PERMISSION_DENIED

Cannot read or write to specified file.

**Example:**
```bash
$ wt2 save config --path "/etc/winterm2.json"
Error: Permission denied writing to /etc/winterm2.json (Error code: 5.2)
Hint: Check file permissions or use --user flag
```

### 5.3 - WINDOW_LOCKED

Window is locked by another process.

**Example:**
```bash
$ wt2 resize --width 100 --window 1
Error: Window 1 is locked by another process (Error code: 5.3)
Hint: Close other winterm2 instances controlling this window
```

---

## Timeout Errors (6)

### 6 - TIMEOUT_ERROR

Operation timed out.

**Common causes:**
- Command taking too long
- Network/connection timeout
- User input timeout

**Example output:**
```
$ wt2 run "sleep 300" --wait
Error: Operation timed out after 60 seconds (Error code: 6)
Hint: Use --timeout flag to set custom timeout
```

### 6.1 - COMMAND_TIMEOUT

Command execution exceeded time limit.

**Example:**
```bash
$ wt2 broadcast send "npm install" --all
Error: Command timed out after 120 seconds (Error code: 6.1)
```

### 6.2 - CONNECTION_TIMEOUT

Connection to Windows Terminal timed out.

**Example:**
```bash
$ wt2 list
Error: Connection to Windows Terminal timed out (Error code: 6.2)
Hint: Ensure Windows Terminal is responsive
```

---

## Configuration Errors (7)

### 7 - CONFIG_ERROR

Configuration file or settings error.

**Common causes:**
- Malformed config file
- Invalid config value
- Missing config section

**Example output:**
```
$ wt2 load dev
Error: Configuration error (Error code: 7)
Details: Invalid 'pane' configuration in profile 'dev'
```

### 7.1 - CONFIG_PARSE_ERROR

Configuration file contains syntax errors.

**Example:**
```bash
$ wt2 config --edit
Error: Configuration parse error (Error code: 7.1)
Details: Line 15: Unexpected token '}'
Hint: Check JSON/YAML syntax
```

### 7.2 - CONFIG_VALIDATION_ERROR

Configuration values failed validation.

**Example:**
```bash
$ wt2 save my-profile
Error: Configuration validation failed (Error code: 7.2)
Details: 'default_shell' must be one of: powershell, cmd, wsl
```

### 7.3 - CONFIG_READ_ERROR

Cannot read configuration file.

**Example:**
```bash
$ wt2 load my-profile
Error: Cannot read configuration (Error code: 7.3)
Details: [Errno 2] No such file or directory
Hint: Use 'wt2 save <name>' to create a profile first
```

### 7.4 - CONFIG_WRITE_ERROR

Cannot write configuration file.

**Example:**
```bash
$ wt2 save my-profile
Error: Cannot save configuration (Error code: 7.4)
Details: Read-only filesystem
```

---

## Error Handling in Scripts

### Exit Code Checking

Check exit codes in batch scripts:

```batch
@echo off
wt2 tab new --profile PowerShell
if %ERRORLEVEL% equ 0 (
    echo Tab created successfully
) else if %ERRORLEVEL% equ 3 (
    echo Target not found
) else if %ERRORLEVEL% equ 4 (
    echo Invalid argument
) else (
    echo Unknown error occurred
)
```

### PowerShell Error Handling

```powershell
try {
    wt2 pane split --profile PowerShell
    Write-Host "Pane created successfully"
}
catch [System.Exception] {
    $exitCode = $LASTEXITCODE
    if ($exitCode -eq 2) {
        Write-Error "Cannot connect to Windows Terminal"
    } elseif ($exitCode -eq 3) {
        Write-Error "Target not found"
    } else {
        Write-Error "Error occurred: $exitCode"
    }
}
```

### Bash/Zsh Error Handling

```bash
#!/bin/bash
set -e

wt2 tab new --profile PowerShell || {
    exit_code=$?
    case $exit_code in
        2) echo "Connection error" ;;
        3) echo "Target not found" ;;
        4) echo "Invalid argument" ;;
        *) echo "Unknown error: $exit_code" ;;
    esac
    exit $exit_code
}
```

---

## Debug Mode

Enable debug mode for detailed error information:

```bash
wt2 --debug <command>
```

Debug output includes:
- Full stack traces
- IPC communication logs
- Timing information
- Configuration values

---

## Reporting Errors

When reporting issues, include:
1. Error code and message
2. Command that caused the error
3. `--debug` output if available
4. Windows Terminal version (`wt --version`)
5. winterm2 version (`wt2 --version`)
6. Operating system version
