# winterm2 Installation Guide

A Windows-native CLI tool for automating Windows Terminal, PowerShell 7+, CMD, and WSL2.

## Requirements

- **Operating System:** Windows 10 1909+ or Windows 11
- **Python:** 3.8 or higher (for pip installation)
- **Windows Terminal:** Version 1.12+ recommended (1.0+ minimum)
- **PowerShell:** 7.0 or higher (optional, for PowerShell module)

---

## Installation Methods

### Method 1: pip (PyPI)

The recommended method for most users.

#### Prerequisites

1. Install Python 3.8 or higher from [python.org](https://www.python.org/downloads/)
2. Ensure Python is added to your PATH during installation
3. Verify installation:
   ```powershell
   python --version
   pip --version
   ```

#### Installation

```powershell
# Upgrade pip first (recommended)
python -m pip install --upgrade pip

# Install winterm2
pip install winterm2

# Verify installation
wt2 --version
```

#### Upgrade

```powershell
pip install --upgrade winterm2
```

#### Uninstall

```powershell
pip uninstall winterm2
```

---

### Method 2: pipx (Recommended for CLI Tools)

pipx provides isolated environments for CLI tools, preventing dependency conflicts.

#### Prerequisites

Install pipx using PowerShell (admin):

```powershell
pip install --user pipx
pipx ensurepath
```

#### Installation

```powershell
pipx install winterm2
```

#### Upgrade

```powershell
pipx upgrade winterm2
```

#### Uninstall

```powershell
pipx uninstall winterm2
```

---

### Method 3: Scoop

For users who prefer Scoop package manager.

#### Prerequisites

Install Scoop if not already installed:

```powershell
# Set execution policy
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser

# Install Scoop
irm get.scoop.sh | iex

# Add extras bucket (for some dependencies)
scoop bucket add extras
```

#### Installation

```powershell
# Add winterm2 bucket (official)
scoop bucket add winterm2 https://github.com/winterm2/scoop-winterm2

# Install winterm2
scoop install winterm2

# Verify installation
wt2 --version
```

#### Upgrade

```powershell
scoop update winterm2
```

#### Uninstall

```powershell
scoop uninstall winterm2
```

---

### Method 4: Chocolatey

For users who prefer Chocolatey package manager.

#### Prerequisites

Install Chocolatey if not already installed:

```powershell
# Set execution policy
Set-ExecutionPolicy Bypass -Scope Process

# Install Chocolatey
iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))
```

#### Installation

```powershell
# Install winterm2
choco install winterm2

# Verify installation
wt2 --version
```

#### Upgrade

```powershell
choco upgrade winterm2
```

#### Uninstall

```powershell
choco uninstall winterm2
```

---

### Method 5: Git + Source

For developers who want the latest source code.

#### Prerequisites

```powershell
# Install Git
scoop install git

# Or via Chocolatey
choco install git
```

#### Installation

```powershell
# Clone repository
git clone https://github.com/winterm2/winterm2.git
cd winterm2

# Install in development mode
pip install -e .

# Or install dependencies only
pip install -r requirements.txt
```

#### Update

```powershell
cd winterm2
git pull
pip install -e .
```

---

## Post-Installation Setup

### Add to PATH (if not automatic)

After installation, ensure winterm2 is in your PATH:

```powershell
# For pip install (User level)
[Environment]::SetEnvironmentVariable(
    "Path",
    $env:Path + ";" + ($env:LOCALAPPDATA) + "\Packages\Python\Python38\Site-packages",
    "User"
)

# Restart your terminal or run:
$env:Path = [Environment]::GetEnvironmentVariable("Path", "User")
```

### Verify Installation

```powershell
# Check version
wt2 --version

# Show help
wt2 --help

# List available commands
wt2 --help
```

### Initial Configuration

```powershell
# Create default configuration
wt2 config --edit

# Verify connection to Windows Terminal
wt2 list
```

---

## Windows Terminal Integration

### Enable RPC (Required)

winterm2 uses Windows Terminal's RPC interface for automation.

1. Open Windows Terminal Settings (Ctrl+,)
2. Navigate to **Actions** > **Profile** > **Advanced**
3. Enable **Enable RPC** (on by default in WT 1.12+)

### Verify RPC Connection

```powershell
wt2 list
```

If you see an error, ensure Windows Terminal is running and RPC is enabled.

---

## Troubleshooting

### "command not found" after pip install

**Cause:** winterm2 not in PATH

**Solution:**
```powershell
# Find where winterm2 was installed
where wt2

# If found, add to PATH manually
[Environment]::SetEnvironmentVariable(
    "Path",
    $env:Path + ";C:\Python38\Scripts",
    "User"
)

# Or reinstall with --script-links flag
pip install --user winterm2 --script-links
```

### Connection error (Error 2)

**Cause:** Windows Terminal not running or RPC disabled

**Solution:**
```powershell
# Ensure Windows Terminal is running
wt

# Enable RPC in Windows Terminal settings
# Settings > Profile > Advanced > Enable RPC
```

### Permission denied (Error 5)

**Cause:** Requires elevated privileges

**Solution:**
```powershell
# Run as Administrator for system-wide operations
# Or use --user flag for user-level only
```

### Python version error

**Cause:** Python version too old

**Solution:**
```powershell
# Check Python version
python --version

# Update Python from https://python.org
# Or via Scoop:
scoop install python

# Or via Chocolatey:
choco install python
```

---

## Docker (Alternative)

For isolated environments, winterm2 can run via Docker:

```dockerfile
FROM python:3.9-slim

RUN pip install winterm2

# Note: Docker on Windows needs X11 forwarding for GUI
# This is an advanced configuration
```

---

## Support

- **GitHub Issues:** [github.com/winterm2/winterm2/issues](https://github.com/winterm2/winterm2/issues)
- **Documentation:** [winterm2.readthedocs.io](https://winterm2.readthedocs.io)
- **Discord:** [discord.gg/winterm2](https://discord.gg/winterm2)

---

## Version Compatibility

| winterm2 | Windows Terminal | Python |
|----------|-------------------|--------|
| 2.0.x    | 1.12+             | 3.8+   |
| 1.5.x    | 1.0+              | 3.7+   |
| 1.0.x    | 1.0+              | 3.6+   |

---

## License

MIT License - See [LICENSE](LICENSE) for details.
