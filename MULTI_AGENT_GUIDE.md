# winterm2 + Claude Code 多代理开发完整指南

## 架构概览

```
┌─────────────────────────────────────────────────────────────────────┐
│                     Claude Code (多代理 UI)                          │
│  ┌─────────────┬─────────────┬─────────────┬─────────────┐          │
│  │  reviewer   │   tester    │    docs     │    dev      │          │
│  │  (agent)    │  (agent)    │  (agent)    │  (agent)    │          │
│  └─────────────┴─────────────┴─────────────┴─────────────┘          │
│                      ↑ Claude Code UI 创建                          │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              │ 不自动控制终端
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│                  winterm2 (终端自动化工具)                          │
│  ┌─────────────┬─────────────┬─────────────┬─────────────┐          │
│  │ PowerShell  │ PowerShell  │ PowerShell  │ PowerShell  │          │
│  │ (Pane 1)    │ (Pane 2)    │ (Pane 3)    │ (Pane 4)    │          │
│  └─────────────┴─────────────┴─────────────┴─────────────┘          │
│                      ↑ 你用 wt2 命令创建                             │
└─────────────────────────────────────────────────────────────────────┘
```

## 重要说明

**Claude Agent Teams** 和 **winterm2** 是两个独立的东西：

| 工具 | 作用 | 创建终端？ |
|------|------|-----------|
| Claude Agent Teams | 多 AI 代理协作（UI 层） | ❌ 不创建 |
| winterm2 | 终端自动化（控制层） | ✅ 创建 |

**它们不会自动联动**！需要手动配合使用。

## 快速开始

### 步骤 1: 创建 4 窗格开发环境

```powershell
# 在 Windows Terminal 中执行
wt2 tab new --profile PowerShell
wt2 pane split              # 水平分割 → 2 个窗格
wt2 pane vsplit             # 垂直分割 → 4 个窗格

# 结果布局:
# ┌─────────┬─────────┐
# │  窗格1  │  窗格2  │
# ├─────────┼─────────┤
# │  窗格3  │  窗格4  │
# └─────────┴─────────┘
```

### 步骤 2: 在每个窗格中运行不同的 Claude Code 代理

```powershell
# 窗格 1: 代码审查代理
cd D:\AI\Agent\winterm2
claude --agent reviewer

# 窗格 2: 测试代理
cd D:\AI\Agent\winterm2
claude --agent tester

# 窗格 3: 文档代理
cd D:\AI\Agent\winterm2
claude --agent docs

# 窗格 4: 主开发代理
cd D:\AI\Agent\winterm2
claude --agent dev
```

### 步骤 3: 配置 Claude Code 代理

创建 `.claude/agents.json`:

```json
{
  "agents": {
    "reviewer": {
      "name": "Code Reviewer",
      "description": "Reviews code for quality and bugs",
      "system_prompt": "You are a code reviewer. Check code for: PEP 8 violations, potential bugs, security issues, code complexity. Always run tests after reviewing."
    },
    "tester": {
      "name": "Test Engineer",
      "description": "Runs tests and checks coverage",
      "system_prompt": "You are a test engineer. Run pytest, check coverage reports, identify failing tests, and suggest fixes."
    },
    "docs": {
      "name": "Documentation Engineer",
      "description": "Updates documentation",
      "system_prompt": "You are a documentation engineer. Update README, docstrings, and API documentation. Keep it clear and concise."
    },
    "dev": {
      "name": "Developer",
      "description": "Main development tasks",
      "system_prompt": "You are the main developer. Implement features, fix bugs, refactor code. Follow PEP 8 and project conventions."
    }
  }
}
```

## 完整工作流示例

### 场景：添加新功能

```powershell
# 1. 创建开发环境
wt2 tab new --profile PowerShell --title "winterm2 开发"
wt2 pane split
wt2 pane vsplit

# 2. 在窗格4（dev）中开始开发
# 输入：
# "添加一个 'wt2 config export' 命令"

# 3. 发现问题后，让 reviewer 检查
# 切换到窗格1 (reviewer):
# "检查 src/wt2/commands/config.py 的代码质量"

# 4. 让 tester 运行测试
# 切换到窗格2 (tester):
# "运行完整测试套件并报告结果"

# 5. 更新文档
# 切换到窗格3 (docs):
# "更新 README.md 添加 config export 命令说明"
```

## 使用 winterm2 广播功能

同时控制所有窗格：

```powershell
# 启用广播到所有窗格
wt2 broadcast on --all

# 所有窗格同时执行
wt2 broadcast send "cd D:\AI\Agent\winterm2 && git status"

# 禁用广播
wt2 broadcast off
```

## Claude Code 命令行代理使用

### 方式 1: 使用预设 agent

```powershell
claude --agent reviewer "检查最近的提交"
claude --agent tester "运行测试并报告覆盖率"
claude --agent docs "更新 CHANGELOG"
```

### 方式 2: 使用自定义 agents.json

```powershell
claude --agent custom "在 agents.json 中定义的任意代理名"
```

### 方式 3: 内联定义代理

```powershell
claude --agents '{
  "security": {
    "description": "Security checker",
    "prompt": "You are a security expert. Check for vulnerabilities."
  }
}' --agent security "扫描安全漏洞"
```

## 推荐的每日开发流程

```powershell
# === 早上开始工作 ===
wt2 tab new --profile PowerShell --title "winterm2 开发"
wt2 pane split
wt2 pane vsplit

# 窗格1: reviewer - 检查代码变更
# 窗格2: tester - 运行测试
# 窗格3: docs - 更新文档
# 窗格4: dev - 主要开发

# === 开始开发 ===
# 1. git pull 更新代码
wt2 broadcast send "cd D:\AI\Agent\winterm2 && git pull"

# 2. 在 dev 窗格中工作
# "实现新功能 X"

# 3. 代码审查
# 切换到 reviewer 窗格
# "检查最近修改的代码"

# 4. 测试验证
# 切换到 tester 窗格
# "运行测试确保没有回归"

# === 结束工作 ===
# 1. 提交代码
wt2 session send "git add . && git commit -m 'feat: 添加新功能'"

# 2. 推送
wt2 session send "git push"
```

## 故障排除

### 问题: Claude Code 不响应

```powershell
# 检查 CLAUDE_API_KEY 环境变量
echo $env:CLAUDE_API_KEY

# 如果没有，设置它
$env:CLAUDE_API_KEY = "your-api-key"
```

### 问题: winterm2 无法连接

```powershell
# 确保 Windows Terminal 已启用 Experimental JSON API
# 检查: wt2 config path
# 如果报错，启用 API 后重启 Terminal
```

## 相关资源

- [Claude Code 文档](https://code.claude.com/docs/zh-CN/agent-teams)
- [winterm2 GitHub](https://github.com/kyirexy/winterm2)
- [it2 GitHub](https://github.com/mkusaka/it2) (参考实现)
