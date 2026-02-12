@echo off
REM winterm2 团队开发快速启动脚本
REM 在 Windows Terminal 中创建多代理开发环境

echo ╔═══════════════════════════════════════════════════════╗
echo ║           winterm2 团队开发环境启动器                  ║
echo ╚═══════════════════════════════════════════════════════╝
echo.

REM 检查是否安装了 winterm2
where wt2 >nul 2>nul
if %errorlevel% neq 0 (
    echo [警告] wt2 命令未找到，请先安装 winterm2
    echo pip install -e .
    echo.
    pause
    exit /b 1
)

echo 正在创建多窗格开发环境...
echo.

REM 创建新标签页
wt2 tab new --profile PowerShell

REM 等待用户按下任意键继续到下一个窗格设置
echo.
echo ===========================================================
echo 步骤 1: 按 Ctrl+Shift+D (复制当前窗格到右侧)
echo 步骤 2: 在新窗格中运行: cd D:\AI\Agent\winterm2
echo ===========================================================
echo.

set /p choice=按 Enter 继续创建垂直分割窗格...

REM 垂直分割
wt2 pane vsplit

echo.
echo ===========================================================
echo 步骤 3: 按 Ctrl+Shift+D 复制当前窗格
echo 步骤 4: 在新窗格中运行不同代理
echo ===========================================================
echo.

echo 建议的代理分配:
echo.
echo ┌─────────────────────────────────────────────────────┐
echo │ 窗格 1: 代码审查代理                                 │
echo │       cd D:\AI\Agent\winterm2                       │
echo │       ruff check src/wt2/ --fix                      │
echo ├─────────────────────────────────────────────────────┤
echo │ 窗格 2: 测试代理                                    │
echo │       cd D:\AI\Agent\winterm2                       │
echo │       pytest tests/ -v                              │
echo ├─────────────────────────────────────────────────────┤
echo │ 窗格 3: 文档代理                                    │
echo │       cd D:\AI\Agent\winterm2                       │
echo │       python scripts/generate_docs.py                │
echo ├─────────────────────────────────────────────────────┤
echo │ 窗格 4: 主要开发代理 (Claude Code)                   │
echo │       cd D:\AI\Agent\winterm2                       │
echo │       claude                                        │
echo └─────────────────────────────────────────────────────┘
echo.

echo 完成！使用 Ctrl+Tab 在窗格间切换。
echo.
