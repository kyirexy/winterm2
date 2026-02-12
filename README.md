# winterm2

> Windows Terminal CLI tool - it2 for Windows

**[English](#english)** | **[中文](#中文)**

---

## English

### Overview

A native Windows CLI tool for automating Windows Terminal, PowerShell 7+, CMD, and WSL2 shells. Designed as a full Windows-native alternative to macOS's `it2` (iTerm2 control tool).

### Features

- **Window/Tab/Pane Management**: Create, close, focus, resize, split panes
- **Session Control**: Send commands, run scripts, clear output
- **Broadcast**: Send commands to multiple panes simultaneously
- **Real-time Monitoring**: Follow and filter pane output
- **YAML Configuration**: Reusable workflows via `~/.wt2rc.yaml`
- **Shell Adaptations**: Auto-detect and adapt for PowerShell/CMD/WSL

### Quick Start

#### Installation

```powershell
# PyPI (recommended)
pip install winterm2

# Scoop
scoop bucket add extras
scoop install winterm2

# Chocolatey
choco install winterm2
```

#### Basic Usage

```powershell
# Create a new tab with PowerShell
wt2 tab new --profile PowerShell

# Split pane horizontally
wt2 pane split

# Split pane vertically
wt2 pane vsplit

# Send command to current pane
wt2 session send "Get-Process"

# Broadcast command to all panes
wt2 broadcast send "git pull" --all

# Follow pane output
wt2 monitor follow --pane-id 1

# Load configuration
wt2 config load ~/.wt2rc.yaml
```

### Command Reference

#### Window Commands

| Command | Description |
|---------|-------------|
| `wt2 window new` | Create a new window |
| `wt2 window close [id]` | Close a window |
| `wt2 window focus <id>` | Focus a window |
| `wt2 window list` | List all windows |

#### Tab Commands

| Command | Description |
|---------|-------------|
| `wt2 tab new` | Create a new tab |
| `wt2 tab close [id]` | Close a tab |
| `wt2 tab focus <id>` | Focus a tab |
| `wt2 tab list` | List all tabs |
| `wt2 tab next` | Switch to next tab |
| `wt2 tab prev` | Switch to previous tab |

#### Pane Commands

| Command | Description |
|---------|-------------|
| `wt2 pane split` | Split pane horizontally |
| `wt2 pane vsplit` | Split pane vertically |
| `wt2 pane close [id]` | Close a pane |
| `wt2 pane focus <direction>` | Focus adjacent pane |
| `wt2 pane resize <direction> [delta]` | Resize pane |
| `wt2 pane list` | List all panes |
| `wt2 pane zoom` | Toggle pane zoom |

#### Session Commands

| Command | Description |
|---------|-------------|
| `wt2 session send <cmd>` | Send command to pane |
| `wt2 session run <cmd>` | Run command in new pane |
| `wt2 session clear` | Clear pane output |
| `wt2 session list` | List all sessions |

#### Broadcast Commands

| Command | Description |
|---------|-------------|
| `wt2 broadcast on --panes 1,2,3` | Enable broadcast |
| `wt2 broadcast off` | Disable broadcast |
| `wt2 broadcast send <cmd>` | Send command to broadcast targets |
| `wt2 broadcast send <cmd> --all` | Send to all panes |

#### Monitor Commands

| Command | Description |
|---------|-------------|
| `wt2 monitor follow` | Follow pane output |
| `wt2 monitor watch` | Watch for changes |
| `wt2 monitor tail [lines]` | Show last N lines |
| `wt2 monitor filter <pattern>` | Filter by keyword |

#### Config Commands

| Command | Description |
|---------|-------------|
| `wt2 config load <path>` | Load config file |
| `wt2 config save [path]` | Save config |
| `wt2 config get <key>` | Get config value |
| `wt2 config set <key> <value>` | Set config value |
| `wt2 config init` | Initialize config |
| `wt2 config edit` | Edit config file |

### Configuration File

Create `~/.wt2rc.yaml` for reusable workflows:

```yaml
version: "1.0"
defaults:
  shell: powershell
  startup_dir: "C:\Projects"

profiles:
  dev:
    commandline: "pwsh -NoLogo"
    starting_directory: "C:\Projects\dev"

  ops:
    commandline: "cmd"
    color_scheme: "One Half Dark"

workflows:
  daily:
    - tab new --profile dev
    - pane split --direction vertical
    - session send "cd C:\Projects"
    - pane vsplit
    - session run "code ."
```

### Shell Compatibility

winterm2 automatically detects and adapts for different shells:

| Shell | Clear Command | List Command | Path Format |
|-------|---------------|--------------|--------------|
| PowerShell | `Clear-Host` | `Get-ChildItem` | `$env:VAR` |
| CMD | `cls` | `dir` | `%VAR%` |
| WSL | `clear` | `ls` | `$VAR` |

#### Path Conversion

Automatic conversion between Windows and WSL paths:

```powershell
# Windows to WSL
D:\Projects → /mnt/d/Projects

# WSL to Windows
/mnt/d/Projects → D:\Projects
```

### Requirements

- Windows 10 21H2+ or Windows 11
- Windows Terminal 1.15+ (with Experimental JSON API enabled)
- Python 3.10+
- No admin privileges required (except for window move/resize)

### Enable Experimental API

1. Open Windows Terminal Settings (Ctrl+,)
2. Go to Developers section
3. Enable "Experimental JSON Command API"
4. Restart Windows Terminal

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Connection error |
| 3 | Target not found |
| 4 | Invalid configuration |

### Development

```powershell
# Clone and install
git clone https://github.com/yourusername/winterm2.git
cd winterm2
pip install -e .

# Run tests
pip install pytest pytest-mock
pytest tests/ --cov=wt2

# Lint
pip install ruff black
ruff check src/wt2/
black src/wt2/
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes following PEP 8
4. Add tests (80%+ coverage required)
5. Submit pull request

### License

MIT License - see LICENSE file for details.

### Acknowledgments

- Inspired by [it2](https://iterm2.com/documentation-shell-integration.html) (iTerm2)
- Built on [Click](https://click.palletsprojects.com/) CLI framework

---

## 中文

### 概述

原生 Windows 命令行工具，用于自动化 Windows Terminal、PowerShell 7+、CMD 和 WSL2 Shell。作为 macOS `it2`（iTerm2 控制工具）的完整 Windows 原生替代品。

### 功能特性

- **窗口/标签页/窗格管理**：创建、关闭、聚焦、调整大小、分割窗格
- **会话控制**：发送命令、运行脚本、清除输出
- **广播**：同时向多个窗格发送命令
- **实时监控**：跟踪和过滤窗格输出
- **YAML 配置**：通过 `~/.wt2rc.yaml` 实现可重用工作流
- **Shell 适配**：自动检测并适配 PowerShell/CMD/WSL

### 快速开始

#### 安装

```powershell
# PyPI（推荐）
pip install winterm2

# Scoop
scoop bucket add extras
scoop install winterm2

# Chocolatey
choco install winterm2
```

#### 基本用法

```powershell
# 使用 PowerShell 创建新标签页
wt2 tab new --profile PowerShell

# 水平分割窗格
wt2 pane split

# 垂直分割窗格
wt2 pane vsplit

# 向当前窗格发送命令
wt2 session send "Get-Process"

# 向所有窗格广播命令
wt2 broadcast send "git pull" --all

# 跟踪窗格输出
wt2 monitor follow --pane-id 1

# 加载配置
wt2 config load ~/.wt2rc.yaml
```

### 命令参考

#### 窗口命令

| 命令 | 描述 |
|------|------|
| `wt2 window new` | 创建新窗口 |
| `wt2 window close [id]` | 关闭窗口 |
| `wt2 window focus <id>` | 聚焦窗口 |
| `wt2 window list` | 列出所有窗口 |

#### 标签页命令

| 命令 | 描述 |
|------|------|
| `wt2 tab new` | 创建新标签页 |
| `wt2 tab close [id]` | 关闭标签页 |
| `wt2 tab focus <id>` | 聚焦标签页 |
| `wt2 tab list` | 列出所有标签页 |
| `wt2 tab next` | 切换到下一个标签页 |
| `wt2 tab prev` | 切换到上一个标签页 |

#### 窗格命令

| 命令 | 描述 |
|------|------|
| `wt2 pane split` | 水平分割窗格 |
| `wt2 pane vsplit` | 垂直分割窗格 |
| `wt2 pane close [id]` | 关闭窗格 |
| `wt2 pane focus <方向>` | 聚焦相邻窗格 |
| `wt2 pane resize <方向> [增量]` | 调整窗格大小 |
| `wt2 pane list` | 列出所有窗格 |
| `wt2 pane zoom` | 切换窗格缩放 |

#### 会话命令

| 命令 | 描述 |
|------|------|
| `wt2 session send <命令>` | 向窗格发送命令 |
| `wt2 session run <命令>` | 在新窗格中运行命令 |
| `wt2 session clear` | 清除窗格输出 |
| `wt2 session list` | 列出所有会话 |

#### 广播命令

| 命令 | 描述 |
|------|------|
| `wt2 broadcast on --panes 1,2,3` | 启用广播 |
| `wt2 broadcast off` | 禁用广播 |
| `wt2 broadcast send <命令>` | 向广播目标发送命令 |
| `wt2 broadcast send <命令> --all` | 发送到所有窗格 |

#### 监控命令

| 命令 | 描述 |
|------|------|
| `wt2 monitor follow` | 跟踪窗格输出 |
| `wt2 monitor watch` | 监视变化 |
| `wt2 monitor tail [行数]` | 显示最后 N 行 |
| `wt2 monitor filter <模式>` | 按关键字过滤 |

#### 配置命令

| 命令 | 描述 |
|------|------|
| `wt2 config load <路径>` | 加载配置文件 |
| `wt2 config save [路径]` | 保存配置 |
| `wt2 config get <键>` | 获取配置值 |
| `wt2 config set <键> <值>` | 设置配置值 |
| `wt2 config init` | 初始化配置 |
| `wt2 config edit` | 编辑配置文件 |

### 配置文件

创建 `~/.wt2rc.yaml` 实现可重用工作流：

```yaml
version: "1.0"
defaults:
  shell: powershell
  startup_dir: "C:\Projects"

profiles:
  dev:
    commandline: "pwsh -NoLogo"
    starting_directory: "C:\Projects\dev"

  ops:
    commandline: "cmd"
    color_scheme: "One Half Dark"

workflows:
  daily:
    - tab new --profile dev
    - pane split --direction vertical
    - session send "cd C:\Projects"
    - pane vsplit
    - session run "code ."
```

### Shell 兼容性

winterm2 自动检测并适配不同的 Shell：

| Shell | 清除命令 | 列表命令 | 路径格式 |
|-------|---------|---------|---------|
| PowerShell | `Clear-Host` | `Get-ChildItem` | `$env:VAR` |
| CMD | `cls` | `dir` | `%VAR%` |
| WSL | `clear` | `ls` | `$VAR` |

#### 路径转换

Windows 和 WSL 路径之间的自动转换：

```powershell
# Windows 到 WSL
D:\Projects → /mnt/d/Projects

# WSL 到 Windows
/mnt/d/Projects → D:\Projects
```

### 系统要求

- Windows 10 21H2+ 或 Windows 11
- Windows Terminal 1.15+（需要启用实验性 JSON API）
- Python 3.10+
- 不需要管理员权限（窗口移动/调整大小除外）

### 启用实验性 API

1. 打开 Windows Terminal 设置（Ctrl+,）
2. 进入开发者（Developers）部分
3. 启用"实验性 JSON 命令 API"（Experimental JSON Command API）
4. 重启 Windows Terminal

### 退出码

| 代码 | 含义 |
|------|------|
| 0 | 成功 |
| 1 | 常规错误 |
| 2 | 连接错误 |
| 3 | 目标未找到 |
| 4 | 无效配置 |

### 开发

```powershell
# 克隆并安装
git clone https://github.com/yourusername/winterm2.git
cd winterm2
pip install -e .

# 运行测试
pip install pytest pytest-mock
pytest tests/ --cov=wt2

# 代码检查
pip install ruff black
ruff check src/wt2/
black src/wt2/
```

### 贡献

1. Fork 本仓库
2. 创建功能分支
3. 按照 PEP 8 标准进行修改
4. 添加测试（需要 80%+ 覆盖率）
5. 提交 Pull Request

### 许可证

MIT License - 详情请参阅 LICENSE 文件。

### 致谢

- 灵感来自 [it2](https://iterm2.com/documentation-shell-integration.html)（iTerm2）
- 基于 [Click](https://click.palletsprojects.com/) CLI 框架构建
