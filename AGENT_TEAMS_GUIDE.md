# winterm2 与 Claude Agent Teams 集成指南

## 概述

本指南介绍如何将 winterm2 与 Claude Agent Teams 结合使用，实现多代理协作开发。

## 方案 1: Claude Code 内置多代理

Claude Code 支持使用 `/team` 命令启动多代理协作：

```powershell
# 在 Claude Code 中输入
/team create winterm2-dev "winterm2 CLI 工具开发团队"
```

## 方案 2: 使用 Windows Terminal 窗格 + tmux

### 步骤 1: 安装依赖

```powershell
# 在 WSL 中安装 tmux
wsl -e sudo apt update && sudo apt install tmux -y

# 或在 PowerShell 中使用 Windows Terminal 内置功能
```

### 步骤 2: 创建多窗格开发环境

```powershell
# 创建 4 窗格开发环境
wt2 tab new --profile PowerShell
wt2 pane split              # 水平分割
wt2 pane vsplit             # 垂直分割
wt2 pane split --direction vertical  # 再垂直分割

# 结果：4 个等大窗格
# ┌─────────┬─────────┐
# │  代理1  │  代理2  │
# ├─────────┼─────────┤
# │  代理3  │  代理4  │
# └─────────┴─────────┘
```

### 步骤 3: 在每个窗格运行不同任务

```powershell
# 窗格 1: 代码审查代理
wt2 send-text "cd D:\\AI\\Agent\\winterm2 && python -m CLAUDE --agent reviewer"

# 窗格 2: 测试代理
wt2 send-text "cd D:\\AI\\Agent\\winterm2 && python -m pytest tests/ -v"

# 窗格 3: 文档代理
wt2 send-text "cd D:\\AI\\Agent\\winterm2 && python scripts/generate_docs.py"

# 窗格 4: 开发代理 (主代理)
wt2 send-text "cd D:\\AI\\Agent\\winterm2 && claude"
```

## 方案 3: 使用 winterm2 广播功能

同时向所有窗格发送命令：

```powershell
# 启用广播到所有窗格
wt2 broadcast on --all

# 发送更新命令到所有代理
wt2 broadcast send "git pull"

# 禁用广播
wt2 broadcast off
```

## 推荐的团队工作流

### 每日开发流程

```
1. 打开 Windows Terminal
2. wt2 tab new --profile PowerShell
3. wt2 pane split && wt2 pane vsplit  # 创建 4 窗格
4. 每个窗格运行不同的代理
5. 使用 wt2 broadcast 同步命令
```

### 自动化脚本

```powershell
# 创建开发环境并启动所有代理
./scripts/team_dev.py
```

## 与 Claude Teams API 集成

如果需要更高级的集成，可以使用 Claude Teams API：

```python
# 伪代码示例
from claude_code import AgentTeam

team = AgentTeam("winterm2-dev")

# 添加队友
team.add_agent("reviewer", role="代码审查")
team.add_agent("tester", role="测试工程师")
team.add_agent("docs", role="技术文档")

# 分配任务
team.assign_task("reviewer", "检查 src/wt2/ 中的代码质量")
team.assign_task("tester", "运行完整测试套件")
team.assign_task("docs", "更新 README.md")

# 启动并行执行
results = team.execute_all()
```

## 快速参考

| 命令 | 描述 |
|------|------|
| `wt2 pane split` | 水平分割当前窗格 |
| `wt2 pane vsplit` | 垂直分割当前窗格 |
| `wt2 broadcast on --all` | 启用全局广播 |
| `wt2 broadcast send "cmd"` | 向所有窗格发送命令 |
| `wt2 session send "cmd"` | 向当前窗格发送命令 |
| `wt2 monitor follow` | 监控窗格输出 |

## 相关链接

- [Claude Agent Teams 文档](https://code.claude.com/docs/zh-CN/agent-teams)
- [winterm2 GitHub](https://github.com/kyirexy/winterm2)
- [Windows Terminal 文档](https://docs.microsoft.com/en-us/windows/terminal/)
