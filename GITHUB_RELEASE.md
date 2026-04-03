# 🚀 GitHub 发布指南

## 快速发布步骤

### 1. 初始化 Git 仓库（如果还没有）
```bash
cd /home/aiserver/Projects/LRS
git init
git add .
git commit -m "Initial commit: Avalon AI Game with Human Player Support"
```

### 2. 创建 GitHub 仓库

#### 选项 A: 使用 GitHub CLI (推荐)
```bash
# 安装 gh (如果还没有)
# Ubuntu/Debian: sudo apt install gh
# macOS: brew install gh

# 登录 GitHub
gh auth login

# 创建新仓库
gh repo create avalon-ai-game --public --source=. --remote=origin --push
```

#### 选项 B: 使用 GitHub 网页
1. 访问 https://github.com/new
2. 输入仓库名称：`avalon-ai-game`
3. 选择 **Public**（公开）
4. **不要** 勾选 "Initialize this repository with a README"
5. 点击 "Create repository"

然后按照网页提示执行：
```bash
cd /home/aiserver/Projects/LRS
git remote add origin https://github.com/YOUR_USERNAME/avalon-ai-game.git
git branch -M main
git push -u origin main
```

### 3. 推送到 GitHub
```bash
# 如果已经创建了远程仓库
git push -u origin main
```

## 完整的 Git 命令序列

```bash
# 进入项目目录
cd /home/aiserver/Projects/LRS

# 初始化 Git
git init

# 添加所有文件
git add .

# 首次提交
git commit -m "feat: Initial release of Avalon AI Game

Features:
- Complete Avalon game rules implementation
- 10 MBTI-based NPC personalities
- Human player support with identity hiding
- AI NPC speech delay for better UX
- Comprehensive documentation

Includes:
- game_avalon.py: Full Avalon game logic
- human_player.py: Human player input handler
- personality_loader.py: MBTI personality system
- Main entry point with human/AI mode selection
- Detailed usage guides and examples"

# 重命名分支为 main
git branch -M main

# 添加远程仓库（替换为你的仓库地址）
git remote add origin https://github.com/YOUR_USERNAME/avalon-ai-game.git

# 推送到 GitHub
git push -u origin main
```

## 推荐的文件结构

```
avalon-ai-game/
├── .gitignore              # ✅ 已创建
├── LICENSE                 # ✅ 已创建 (MIT)
├── README.md               # ✅ 已存在
├── requirements.txt        # ✅ 已存在
├── main.py                 # ✅ 游戏入口
├── game_avalon.py          # ✅ 阿瓦隆游戏逻辑
├── human_player.py         # ✅ 人类玩家模块
├── personality_loader.py   # ✅ 人格加载器
├── prompt.py               # ✅ 提示词
├── structured_model.py     # ✅ 结构化模型
├── utils.py                # ✅ 工具函数
├── test_personality.py     # ✅ 测试文件
├── personalities/          # ✅ 人格模板文件夹
│   ├── INTJ_建筑师.md
│   ├── ENTP_发明家.md
│   └── ...
├── checkpoints/            # ⚠️ 已在.gitignore 中忽略
└── docs/                   # 📖 可选：整理文档
    ├── HUMAN_PLAYER_GUIDE.md
    ├── HUMAN_PLAYER_SUMMARY.md
    └── ...
```

## GitHub 仓库优化建议

### 1. 更新 README.md
在 README.md 顶部添加徽章和简介：

```markdown
# 🏰 阿瓦隆 AI 游戏 - Avalon AI Game

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![AgentScope](https://img.shields.io/badge/AgentScope-0.1.0-green.svg)](https://github.com/modelscope/agentscope)

**与 AI NPC 同台竞技的阿瓦隆桌游！支持人类玩家参与，身份完全隐藏。**

✨ 特性：
- 🎮 完整阿瓦隆规则实现
- 🤖 10 种基于 MBTI 的 NPC 人格
- 👤 人类玩家可与 AI 对战
- 🎭 身份隐藏机制
- ⏱️ 智能 AI 延迟系统
```

### 2. 添加截图或演示 GIF
如果有游戏截图或录屏，可以添加到 README。

### 3. 添加贡献指南
创建 `CONTRIBUTING.md`：
```markdown
# 贡献指南

欢迎提交 Issue 和 Pull Request！

## 开发环境设置
1. Fork 本仓库
2. 克隆到本地
3. 创建虚拟环境
4. 安装依赖

## 提交代码
1. 创建功能分支
2. 提交更改
3. 推送到分支
4. 创建 Pull Request
```

### 4. 添加 Issues 模板
创建 `.github/ISSUE_TEMPLATE/bug_report.md` 等。

## 发布后的推广建议

### 1. 社交媒体分享
- Twitter/X
- LinkedIn
- Reddit (r/MachineLearning, r/Python)
- V2EX
- 知乎

### 2. 技术社区
- Hacker News
- Product Hunt
- GitHub Trending

### 3. 中文社区
- 掘金
- SegmentFault
- 开源中国

### 4. 标签和话题
使用相关标签：
```
#AI #MachineLearning #GameDev #Python #OpenSource
#Avalon #BoardGame #Agentscope #LLM #MBTI
```

## 版本发布流程

### 语义化版本控制
遵循 [Semantic Versioning](https://semver.org/)：
- MAJOR.MINOR.PATCH (例如：1.0.0)

### 创建 Release
```bash
# 打标签
git tag -a v1.0.0 -m "Release version 1.0.0"

# 推送标签
git push origin v1.0.0
```

然后在 GitHub 上创建 Release：
1. 访问 https://github.com/YOUR_USERNAME/avalon-ai-game/releases
2. 点击 "Draft a new release"
3. 选择标签 `v1.0.0`
4. 填写发布说明
5. 点击 "Publish release"

### 发布说明模板
```markdown
## 🎉 Avalon AI Game v1.0.0

### ✨ 新特性
- 完整阿瓦隆游戏规则实现
- 10 种基于 MBTI 的 NPC 人格
- 人类玩家支持（身份隐藏）
- AI NPC 发言延迟机制

### 🐛 Bug 修复
- （如有）

### 📝 文档更新
- 完整使用指南
- 快速开始指南
- API 文档

### 🔧 技术改进
- 性能优化
- 代码重构

### 📦 安装
```bash
pip install -r requirements.txt
python main.py
```

### 🙏 致谢
感谢所有贡献者！
```

## 统计信息

查看项目统计：
```bash
# 代码行数
find . -name "*.py" -exec wc -l {} + | tail -1

# 文件大小
du -sh .

# 文件数量
find . -type f | wc -l
```

---

**祝发布顺利！** 🚀
