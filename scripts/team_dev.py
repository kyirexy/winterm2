#!/usr/bin/env python3
"""
winterm2 Team Development Script

在多个终端窗格中并行运行不同的开发任务。
支持 Claude Agent Teams 风格的多代理协作。
"""

import subprocess
import sys
import os

def run_in_wt_pane(command: str, pane_index: int = 0) -> None:
    """在指定窗格中运行命令（需要 Windows Terminal wt.exe）"""
    wt_command = [
        "wt.exe",
        "split-pane",
        "--pane",
        str(pane_index),
        "pwsh",
        "-NoLogo",
        "-Command",
        command,
    ]
    subprocess.run(wt_command, shell=True)


def team_dev():
    """启动团队开发模式 - 同时运行多个代理"""

    print("""
╔════════════════════════════════════════════════════════════╗
║                    winterm2 团队开发模式                      ║
╚════════════════════════════════════════════════════════════╝

在 Windows Terminal 中并行运行多个开发代理：

1. 代理 - 代码审查 (review-agent)
   └── 检查代码质量、PEP 8 违规、安全问题

2. 代理 - 测试工程师 (test-agent)
   └── 运行测试、检查覆盖率、生成报告

3. 代理 - 文档工程师 (docs-agent)
   └── 更新 README、API 文档、CHANGELOG

4. 代理 - 主要开发 (dev-agent)
   └── 功能开发、bug 修复、重构

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

启动命令（请在 Windows Terminal 中手动执行）:

# 创建 4 窗格布局
wt2 tab new --profile PowerShell
wt2 pane split
wt2 pane vsplit
wt2 pane split --direction vertical

# 在每个窗格中运行不同的代理

# 窗格 1: 代码审查
cd D:\\AI\\Agent\\winterm2
python -m pytest tests/ --tb=short -q

# 窗格 2: 测试运行
cd D:\\AI\\Agent\\winterm2
ruff check src/wt2/ --fix

# 窗格 3: 文档更新
cd D:\\AI\\Agent\\winterm2
python scripts/generate_docs.py

# 窗格 4: 主要开发
cd D:\\AI\\Agent\\winterm2
python -m CLAUDE --role dev-agent

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

提示: 使用 Claude Code 的 /team 命令启动多代理协作！

Learn more: https://code.claude.com/docs/zh-CN/agent-teams
""")

    # 检查是否在 tmux 中运行
    if os.environ.get("TMUX"):
        print("检测到 tmux 会话 - 可用命令:")
        print("  Ctrl+b c  - 创建新窗格")
        print("  Ctrl+b n  - 切换到下一个窗格")
        print("  Ctrl+b p  - 切换到上一个窗格")
        print("  Ctrl+b d  - 分离会话（后台运行）")


if __name__ == "__main__":
    team_dev()
