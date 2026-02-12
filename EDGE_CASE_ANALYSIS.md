# Windows Terminal CLI Edge Case Analysis

## Document Overview

This document identifies and documents Windows-specific edge cases, robustness considerations, and design challenges for the `wt2` project (Windows Terminal CLI adaptation).

---

## 1. Risk Assessment Matrix

### 1.1 Terminal API Risks

| Risk ID | Description | Likelihood | Impact | Severity | Mitigation |
|---------|-------------|------------|--------|----------|------------|
| WT-001 | Windows Terminal not installed | Medium | High | Critical | Detect installation via registry, winget, or common paths; provide clear installation instructions |
| WT-002 | Experimental JSON API disabled | High | High | Critical | Check settings.json for `"experimentalAPI": true`; provide guidance for enabling |
| WT-003 | Multiple WT instances causing conflicts | Medium | Medium | Major | Use named pipes with unique IDs; implement instance detection and coordination |
| WT-004 | Race conditions in API calls | Medium | High | Major | Implement request queuing and response correlation using correlation IDs |
| WT-005 | WebSocket connection failures | Medium | High | Major | Auto-reconnect with exponential backoff; timeout handling |

### 1.2 Permission Risks

| Risk ID | Description | Likelihood | Impact | Severity | Mitigation |
|---------|-------------|------------|--------|----------|------------|
| PM-001 | Non-admin cannot move/resize windows | Medium | Medium | Major | Detect elevation state; warn user about limitations; provide alternative commands |
| PM-002 | WSL access permission denied | Low | Medium | Medium | Check WSL registration; validate user in `www-data` group if required |
| PM-002 | Config file write permissions | Low | High | Major | Check file permissions before write; use user config directory (~/.wt2rc) |
| PM-004 | Script execution policy blocked | Medium | Medium | Major | Detect PowerShell execution policy; guide user to bypass if needed |

### 1.3 Path Conversion Risks

| Risk ID | Description | Likelihood | Impact | Severity | Mitigation |
|---------|-------------|------------|--------|----------|------------|
| PC-001 | UNC path conversion failure | Medium | Medium | Major | Special handling for `\\wsl$\` prefixes; validate before conversion |
| PC-002 | Network drive mapping inconsistency | Low | Medium | Medium | Resolve to UNC before WSL conversion; document limitation |
| PC-003 | Paths with special characters | Medium | Medium | Major | Escape/quote paths properly; handle spaces, brackets, quotes |
| PC-004 | Long path (>260 chars) failure | Low | High | Major | Enable long-path registry setting; use `\\?\` prefix for Win32 APIs |
| PC-005 | Case sensitivity mismatches | Medium | Low | Low | Document WSL case sensitivity; normalize paths appropriately |

### 1.4 Shell Compatibility Risks

| Risk ID | Description | Likelihood | Impact | Severity | Mitigation |
|---------|-------------|------------|--------|----------|------------|
| SC-001 | `cls` vs `clear` incompatibility | High | Low | Minor | Detect shell type; auto-translate or warn user |
| SC-002 | `dir` vs `ls` incompatibility | High | Low | Minor | Shell detection; command translation layer |
| SC-003 | Environment variable syntax mismatch | High | Medium | Major | Detect shell; parse `$env:VAR` vs `%VAR%` vs `$VAR` |
| SC-004 | PowerShell 5.1 vs 7+ differences | Medium | Medium | Major | Detect PowerShell version; adjust syntax accordingly |
| SC-005 | WSL distribution variations | Medium | Medium | Major | Detect distribution; use distro-specific command paths |

### 1.5 Real-Time Monitoring Risks

| Risk ID | Description | Likelihood | Impact | Severity | Mitigation |
|---------|-------------|------------|--------|----------|------------|
| RT-001 | High-volume output buffer overflow | Medium | Medium | Major | Implement output chunking; streaming parser; backpressure handling |
| RT-002 | Unicode/encoding issues | Medium | Medium | Major | Force UTF-8 encoding; handle BOM; validate encoding |
| RT-003 | Memory leak during long monitoring | Low | High | Major | Resource cleanup; circular buffer; periodic garbage collection |
| RT-004 | Monitoring during broadcast | Medium | Medium | Major | Thread-safe output aggregation; session filtering |

### 1.6 Race Condition Risks

| Risk ID | Description | Likelihood | Impact | Severity | Mitigation |
|---------|-------------|------------|--------|----------|------------|
| RC-001 | Quick successive commands | Medium | Medium | Major | Command debouncing; response tracking |
| RC-002 | Focus changes during operations | Low | Medium | Major | Idempotent operations; state validation before action |
| RC-003 | Tab/close during broadcast | Low | High | Major | Session state tracking; graceful degradation |

### 1.7 Security Risks

| Risk ID | Description | Likelihood | Impact | Severity | Mitigation |
|---------|-------------|------------|--------|----------|------------|
| SEC-001 | Command injection via user input | Medium | Critical | Critical | Input sanitization; parameterization; allowlist validation |
| SEC-002 | Untrusted config file | Low | Critical | Critical | Config validation schema; disable arbitrary code execution |
| SEC-003 | Path traversal vulnerability | Low | Critical | Critical | Path normalization; validation against base directory |
| SEC-004 | Unsafe temp file creation | Low | High | Major | Secure temp file APIs; proper cleanup; permissions |

---

## 2. Mitigation Strategies

### 2.1 Terminal API Mitigations

#### WT-001/002: Windows Terminal Detection and API Enabling

```python
def detect_windows_terminal() -> tuple[bool, str, str]:
    """Detect Windows Terminal installation and API status."""
    # Check common installation paths
    wt_paths = [
        os.environ.get("LOCALAPPDATA") + "\\Microsoft\\Windows Terminal",
        os.environ.get("PROGRAMDATA") + "\\Microsoft\\Windows Terminal",
        "\\Program Files\\Windows Terminal",
    ]

    for path in wt_paths:
        if os.path.exists(os.path.join(path, "wt.exe")):
            return True, "found", path

    # Check registry
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                           r"Software\Microsoft\Windows\CurrentVersion\Terminal Server") as key:
            # Additional checks...
    except WindowsError:
        pass

    return False, "not_found", "Install from Microsoft Store or winget install Microsoft.WindowsTerminal"
```

**User-facing message**:
```
Windows Terminal is not installed or not found.
Installation options:
  1. Microsoft Store:   winget install Microsoft.WindowsTerminal
  2. Chocolatey:         choco install microsoft-windows-terminal
  3. Manual:             Download from https://github.com/microsoft/terminal
```

#### WT-004: WebSocket with Retry Logic

```python
async def connect_with_retry(max_retries: int = 3, base_delay: float = 0.5):
    """Connect to Windows Terminal API with exponential backoff."""
    for attempt in range(max_retries):
        try:
            ws = await asyncio.wait_for(
                connect("ws://localhost:8000/terminal"),
                timeout=5.0
            )
            return ws
        except asyncio.TimeoutError:
            delay = base_delay * (2 ** attempt)
            logger.warning(f"Connection attempt {attempt + 1} timed out, retrying in {delay}s")
            await asyncio.sleep(delay)
    raise ConnectionError("Failed to connect after {max_retries} attempts")
```

### 2.2 Permission Mitigations

#### PM-001: Elevation Detection and Handling

```python
def is_admin() -> bool:
    """Check if current process has administrator privileges."""
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False

def warn_if_not_admin(command: str) -> None:
    """Warn user if admin rights may be required."""
    if command in ("window move", "window resize") and not is_admin():
        click.echo(
            "Warning: Window move/resize may require administrator privileges.\n"
            "Some operations might fail if running without elevation.",
            err=True
        )
```

#### PM-003: Config File Permission Handling

```python
def safe_write_config(config_path: str, config_data: dict) -> None:
    """Safely write config file with proper permissions."""
    import stat

    # Create parent directories
    os.makedirs(os.path.dirname(config_path), exist_ok=True)

    # Write to temp file first
    temp_path = config_path + ".tmp"
    with open(temp_path, 'w', encoding='utf-8') as f:
        yaml.dump(config_data, f)

    # Set restrictive permissions (owner read/write only)
    os.chmod(temp_path, stat.S_IRUSR | stat.S_IWUSR)

    # Atomic replace
    os.replace(temp_path, config_path)
```

### 2.3 Path Conversion Mitigations

#### PC-001/PC-003: Robust Path Conversion

```python
import re
from pathlib import PureWindowsPath, PurePosixPath

def windows_to_wsl_path(windows_path: str, distro: str = "Ubuntu") -> str:
    """Convert Windows path to WSL path with edge case handling."""

    # Handle UNC paths
    if windows_path.startswith("\\\\wsl$\\"):
        # Already a WSL UNC path, just normalize
        return windows_path.replace("\\\\wsl$\\", "/mnt/")

    # Handle network drives
    if windows_path.startswith("\\\\"):
        raise ValueError("Network drive paths require mapping to local first")

    # Handle long paths (Windows API limit)
    if len(windows_path) > 260:
        # Remove \\?\ prefix if present, add for Win32 API calls
        if not windows_path.startswith("\\\\?\\"):
            windows_path = "\\\\?\\" + windows_path

    # Convert to PureWindowsPath for parsing
    win_path = PureWindowsPath(windows_path)

    # Extract components, handling special characters
    parts = [p for p in win_path.parts]

    # Build WSL path
    if len(parts) >= 2 and parts[0][1] == ':':
        drive_letter = parts[0][0].lower()
        wsl_path = f"/mnt/{drive_letter}/" + "/".join(parts[1:])
    else:
        wsl_path = "/" + "/".join(parts)

    # Quote path if it contains special characters
    special_chars = re.compile(r'[()\[\]{};&!$`"\']')
    if special_chars.search(wsl_path):
        wsl_path = wsl_path.replace(" ", "\\ ")

    return wsl_path
```

#### PC-004: Long Path Handling

```python
def ensure_long_path_compliance(path: str) -> str:
    """Ensure path is compliant with Windows length limits."""
    MAX_PATH = 260

    # Check if long paths are enabled in registry
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                           r"SYSTEM\CurrentControlSet\Control\FileSystem") as key:
            long_paths_enabled, _ = winreg.QueryValueEx(key, "LongPathsEnabled")
    except WindowsError:
        long_paths_enabled = 0

    if len(path) > MAX_PATH or not long_paths_enabled:
        if not path.startswith("\\\\?\\"):
            return "\\\\?\\" + os.path.abspath(path)

    return path
```

### 2.4 Shell Compatibility Mitigations

#### SC-001/002: Shell Detection and Command Translation

```python
SHELL_TRANSLATIONS = {
    ("cmd", "clear"): "cls",
    ("cmd", "ls"): "dir",
    ("powershell", "clear"): "Clear-Host",
    ("powershell", "ls"): "Get-ChildItem",
}

def detect_shell(session_id: str) -> str:
    """Detect the shell type for a given session."""
    # Query session for shell type or infer from environment
    response = wt_api.get_session_info(session_id)
    return response.get("shell", "unknown")

def translate_command(shell: str, command: str) -> str:
    """Translate generic commands to shell-specific equivalents."""
    if shell == "cmd":
        # CMD doesn't need translation for most commands
        return command

    # PowerShell/WSL translations
    return SHELL_TRANSLATIONS.get((shell, command), command)
```

#### SC-003: Environment Variable Handling

```python
def expand_env_vars(value: str, shell: str) -> str:
    """Expand environment variables according to shell syntax."""
    if shell in ("cmd", "command"):
        # CMD: %VAR%
        def cmd_replace(m):
            return os.environ.get(m.group(1), "")
        return re.sub(r'%(\w+)%', cmd_replace, value)

    elif shell in ("powershell", "pwsh"):
        # PowerShell: $env:VAR
        def ps_replace(m):
            return os.environ.get(m.group(1), "")
        return re.sub(r'\$env:(\w+)', ps_replace, value)

    else:
        # WSL/Linux: $VAR
        def unix_replace(m):
            return os.environ.get(m.group(1), "")
        return re.sub(r'\$(\w+)', unix_replace, value)
```

### 2.5 Real-Time Monitoring Mitigations

#### RT-001/003: Streaming Parser with Backpressure

```python
import asyncio
from collections import deque
from typing import Optional

class StreamingOutputParser:
    """Handle high-volume output with backpressure management."""

    def __init__(self, max_buffer_size: int = 1024 * 1024):  # 1MB
        self.buffer = deque(maxlen=max_buffer_size)
        self.output_queue: asyncio.Queue = asyncio.Queue(maxsize=100)
        self._running = False

    async def process_stream(self, stream):
        """Process stream with backpressure handling."""
        self._running = True

        try:
            async for chunk in stream:
                # Apply backpressure if queue is full
                while self.output_queue.full():
                    await asyncio.sleep(0.01)

                # Parse and queue
                parsed = self._parse_chunk(chunk)
                await self.output_queue.put(parsed)

                # Manage buffer size
                while len(self.buffer) > self.max_buffer_size:
                    self.buffer.popleft()

        finally:
            self._running = False

    def _parse_chunk(self, chunk: bytes) -> str:
        """Parse output chunk with encoding handling."""
        # Force UTF-8, fallback to other encodings
        try:
            return chunk.decode("utf-8")
        except UnicodeDecodeError:
            try:
                return chunk.decode("utf-8", errors="replace")
            except:
                return chunk.decode("latin-1", errors="replace")

    async def cleanup(self):
        """Clean up resources to prevent memory leaks."""
        self._running = False
        self.buffer.clear()
        while not self.output_queue.empty():
            try:
                self.output_queue.get_nowait()
            except asyncio.QueueEmpty:
                break
```

### 2.6 Race Condition Mitigations

#### RC-001: Command Debouncing with Response Tracking

```python
import asyncio
import uuid
from typing import Dict, Callable, Any

class CommandCoordinator:
    """Coordinate commands to prevent race conditions."""

    def __init__(self, debounce_delay: float = 0.1):
        self.pending_commands: Dict[str, asyncio.Task] = {}
        self.debounce_delay = debounce_delay
        self._command_lock = asyncio.Lock()

    async def execute_with_debounce(
        self,
        command_id: str,
        coro: Callable[..., Any],
        *args,
        **kwargs
    ) -> Any:
        """Execute command with debouncing for rapid invocations."""
        async with self._command_lock:
            # Check for duplicate pending command
            if command_id in self.pending_commands:
                existing = self.pending_commands[command_id]
                if not existing.done():
                    # Wait for existing to complete
                    return await existing

            # Create new command
            task = asyncio.create_task(coro(*args, **kwargs))
            self.pending_commands[command_id] = task

            try:
                return await task
            finally:
                # Cleanup after completion
                self.pending_commands.pop(command_id, None)
```

### 2.7 Security Mitigations

#### SEC-001: Command Injection Prevention

```python
import shlex
import re

def sanitize_command(user_input: str, allowed_chars: str = None) -> str:
    """Sanitize user input to prevent command injection."""
    if allowed_chars is None:
        allowed_chars = r"a-zA-Z0-9_./-"

    # Check for dangerous characters
    dangerous = re.compile(r'[;&|`$(){}[\]\\!#*?"\'<>]')
    if dangerous.search(user_input):
        raise ValueError(
            "Command contains potentially dangerous characters. "
            "Only alphanumeric characters, underscore, forward slash, "
            "hyphen, and period are allowed."
        )

    # Use shlex for safe quoting if needed
    return user_input

def execute_safe_command(base_cmd: str, args: list[str]) -> subprocess.CompletedProcess:
    """Execute command with proper argument separation."""
    # Use shlex.join for proper quoting on POSIX
    # On Windows, use proper array-based invocation
    return subprocess.run(
        [base_cmd] + args,
        shell=False,  # Never use shell=True with user input
        capture_output=True,
        text=True,
        check=False  # Don't raise on non-zero exit
    )
```

#### SEC-003: Path Traversal Prevention

```python
import os

def safe_resolve_path(requested: str, base_dir: str) -> str:
    """Resolve path while preventing path traversal attacks."""
    # Normalize and resolve
    resolved = os.path.normpath(os.path.join(base_dir, requested))

    # Ensure result is within base directory
    real_base = os.path.realpath(base_dir)
    real_resolved = os.path.realpath(resolved)

    if not real_resolved.startswith(real_base + os.sep):
        raise ValueError(
            f"Path '{requested}' would escape base directory '{base_dir}'"
        )

    return resolved
```

---

## 3. Testing Recommendations

### 3.1 Terminal API Tests

| Test Case | Description | Expected Result | Automation |
|-----------|-------------|-----------------|------------|
| WT-DETECT-001 | Detect when WT is not installed | Error with install instructions | Mock registry/filesystem |
| WT-DETECT-002 | Detect when WT is installed but API disabled | Warning with enable instructions | Mock settings.json |
| WT-CONNECT-001 | Successful WebSocket connection | Connected state | Mock WebSocket server |
| WT-CONNECT-002 | Connection timeout handling | Retry with backoff | Mock timeout responses |
| WT-CONNECT-003 | Connection during high load | Graceful degradation | Simulated load |

### 3.2 Permission Tests

| Test Case | Description | Expected Result | Automation |
|-----------|-------------|-----------------|------------|
| PERM-ADMIN-001 | Run as non-admin, try window move | Warning message | Mock elevation check |
| PERM-ADMIN-002 | Run as admin, try window move | Success | Mock elevation |
| PERM-WSL-001 | User not in WSL group | Permission error | Mock WSL permissions |
| PERM-CONFIG-001 | Write to read-only config dir | Permission error | Mock filesystem permissions |

### 3.3 Path Conversion Tests

| Test Case | Description | Expected Result | Automation |
|-----------|-------------|-----------------|------------|
| PATH-UNC-001 | Convert `\\wsl$\Ubuntu\home\user` | `/mnt/c/home/user` | Unit test |
| PATH-SPACE-001 | Convert path with spaces | Properly quoted | Unit test |
| PATH-LONG-001 | Path > 260 characters | Long-path handling | Unit test |
| PATH-SPECIAL-001 | Path with brackets/parentheses | Properly escaped | Unit test |
| PATH-CASE-001 | Case sensitivity in WSL | Document behavior | Unit test |

### 3.4 Shell Compatibility Tests

| Test Case | Description | Expected Result | Automation |
|-----------|-------------|-----------------|------------|
| SHELL-DETECT-001 | Detect CMD session | Shell type = cmd | Mock session info |
| SHELL-DETECT-002 | Detect PowerShell session | Shell type = powershell | Mock session info |
| SHELL-DETECT-003 | Detect WSL-Ubuntu session | Shell type = wsl.ubuntu | Mock session info |
| SHELL-TRANS-001 | Translate `clear` in CMD | `cls` | Unit test |
| SHELL-TRANS-002 | Translate `ls` in CMD | `dir` | Unit test |
| SHELL-ENV-001 | Expand `%VAR%` in CMD | Actual value | Unit test |
| SHELL-ENV-002 | Expand `$env:VAR` in PS | Actual value | Unit test |

### 3.5 Real-Time Monitoring Tests

| Test Case | Description | Expected Result | Automation |
|-----------|-------------|-----------------|------------|
| MONITOR-HIGH-001 | Monitor with 1000+ lines/sec | Buffer management active | Load test |
| MONITOR-UNICODE-001 | Monitor with emoji/unicode | Proper display | Unit test |
| MONITOR-MEMORY-001 | Monitor for 1 hour | Stable memory usage | Long-running test |
| MONITOR-BROADCAST-001 | Monitor while broadcasting | No data corruption | Integration test |

### 3.6 Race Condition Tests

| Test Case | Description | Expected Result | Automation |
|-----------|-------------|-----------------|------------|
| RACE-RAPID-001 | 10 commands in <100ms | Commands executed sequentially | Load test |
| RACE-FOCUS-001 | Focus change during operation | Graceful handling | Mock focus events |
| RACE-CLOSE-001 | Close tab during broadcast | Clean termination | Integration test |

### 3.7 Security Tests

| Test Case | Description | Expected Result | Automation |
|-----------|-------------|-----------------|------------|
| SEC-INJECT-001 | Command with `; rm -rf /` | Sanitization error | Fuzz test |
| SEC-INJECT-002 | Command with backticks | Sanitization error | Fuzz test |
| SEC-TRAVERSAL-001 | Path `../../etc/passwd` | Safe resolution error | Fuzz test |
| SEC-TRAVERSAL-002 | Path with null byte | Null byte stripped | Fuzz test |

---

## 4. Known Limitations

### 4.1 Feature Limitations

| Feature | Limitation | Workaround | Future Enhancement |
|---------|------------|------------|-------------------|
| Window move/resize | Limited without elevation | Use WT window controls | Detect elevation requirement |
| Broadcast | Text input only | Manual sync | File-based broadcast |
| Profile sync | Read-only from WT | Manual config | Write-back support |
| Tab color | Not supported by API | Manual setting | Request WT API enhancement |

### 4.2 Platform Limitations

| Limitation | Description | Impact |
|------------|-------------|--------|
| WT must be running | CLI requires active WT instance | Background automation not possible |
| Single WT instance | Only one active API connection | No multi-instance coordination |
| WSL requirement | Some features need WSL | Not available on Windows 10 Home |
| PowerShell version | Some commands require PS 7+ | Detect and warn, fallback |

### 4.3 Configuration Limitations

| Limitation | Description | Impact |
|------------|-------------|--------|
| ~ expansion | Only in specific contexts | Use full paths |
| Glob patterns | Limited support | Native shell globbing |
| Environment vars | Shell-dependent syntax | Provide shell context |

---

## 5. Design Challenges

### 5.1 Split Behavior Consistency

**Challenge**: The `split` command in it2 creates horizontal/vertical pane splits. Windows Terminal's API may have different semantics.

**Questions to Resolve**:
- Does WT API support both horizontal and vertical splits?
- How are split sizes determined (equal vs. specified)?
- What happens when splitting in a maximized pane?

**Recommendation**: Implement split as:
1. Query current pane layout
2. Calculate split geometry
3. Execute split via WT API
4. Validate resulting layout matches intent

### 5.2 Broadcast Across Mixed Shells

**Challenge**: Broadcasting to PowerShell, CMD, and WSL panes requires different command formats.

**Approaches**:
1. **Shell-aware broadcast**: Translate commands per pane's shell
2. **Raw broadcast**: Send raw bytes to all panes
3. **Compatibility mode**: Only broadcast to same-shell panes

**Recommendation**: Implement layered approach:
- Default: Raw broadcast with warning
- Optional: Shell-aware translation with user opt-in

### 5.3 Path Conversion Robustness

**Challenge**: WSL path conversion has many edge cases beyond simple drive letter mapping.

**Known Complex Cases**:
- `\\wsl$\` UNC paths from WSL
- `/mnt/c/...` vs `/c/...` variants
- NTFS mount points in WSL
- Symbolic link resolution

**Recommendation**: Use Microsoft's `wslpath` tool for authoritative conversion when available.

### 5.4 Long-Running Monitoring Memory

**Challenge**: 24/7 monitoring with real-time output parsing can accumulate memory.

**Monitoring Strategy**:
- Circular buffer for recent output (configurable size)
- Periodic garbage collection triggers
- Leak detection via memory profiling in tests

**Recommendation**: Implement with these safeguards:
1. Configurable max buffer size (default 10,000 lines)
2. Automatic flush on buffer overflow
3. Optional output to file instead of memory

### 5.5 Actionable Error Messages

**Challenge**: Windows Terminal API errors can be cryptic.

**Error Categories and Messages**:

| Error Category | User-Friendly Message | Action |
|----------------|----------------------|--------|
| Connection refused | "Windows Terminal is not running. Start Windows Terminal and try again." | User action |
| Session not found | "Tab/session not found. Use `wt2 session list` to see available sessions." | User action |
| API error | "Terminal operation failed. Check Windows Terminal is up to date." | Documentation link |
| Permission denied | "This operation requires administrator privileges. Restart as admin?" | Escalation |

---

## 6. Appendix: Windows Terminal API Reference

### 6.1 Required Settings for Full Functionality

```json
{
    "experimentalAPI": true,
    "alwaysOnTop": false,
    "firstWindowPreference": "defaultProfile",
    "launchMode": "default"
}
```

### 6.2 WT.exe Command Line Reference

Common wt.exe commands that wt2 may need to invoke:

| Command | Purpose | Notes |
|---------|---------|-------|
| `wt new-tab` | Open new tab | RequiresWT running |
| `wt split-pane` | Split current pane | Horizontal/vertical options |
| `wt move-focus` | Change focus | Directional navigation |
| `wt resize-pane` | Resize pane | Direction or size specification |

### 6.3 WebSocket API Endpoints

When experimental API is enabled, Windows Terminal exposes:

| Endpoint | Purpose | Protocol |
|----------|---------|----------|
| `ws://localhost:8000/terminal` | Main terminal control | JSON-RPC over WebSocket |
| `ws://localhost:8000/tab` | Tab management | JSON-RPC |

---

## 7. Document Version

- **Version**: 0.1.0
- **Created**: 2026-02-12
- **Status**: Initial Edge Case Analysis
- **Review Cycle**: Per major release or significant API changes
