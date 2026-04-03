# 人类玩家功能集成指南

## ✅ 已完成的功能

### 1. 人类玩家输入模块 (`human_player.py`)
- ✅ 文本输入发言
- ✅ 投票选择
- ✅ YES/NO决策
- ✅ 团队提议
- ✅ 任务投票
- ✅ 刺杀选择

### 2. 游戏核心集成 (`game_avalon.py`)
- ✅ 人类玩家作为 Agent 包装
- ✅ 角色分配支持人类
- ✅ 特殊角色信息告知人类
- ✅ AI NPC 发言延迟机制

### 3. 身份隐藏机制
- ✅ AI NPC 不知道人类玩家的存在
- ✅ 人类玩家的发言通过 Agent 包装器自然融入
- ✅ 所有玩家使用统一的接口

## 📝 待完成的修改

需要在 `game_avalon.py` 中继续修改以下部分：

### 讨论阶段 (Discussion Phase)
```python
# 在 sequential_pipeline 处添加人类玩家支持
# 当前代码第 278 行左右
alive_players_hub.set_auto_broadcast(True)
await sequential_pipeline(players.current_alive)
```

**需要修改为**:
- 检测当前发言者是 AI 还是人类
- AI 发言后添加延迟
- 人类通过 input 输入发言

### 投票阶段 (Voting Phase)
```python
# 在 fanout_pipeline 处添加人类玩家支持
# 当前代码第 284 行左右
msgs_vote = await fanout_pipeline(
    players.current_alive,
    await moderator(...),
    structured_model=get_vote_model(...),
    enable_gather=False,
)
```

**需要修改为**:
- AI 使用结构化模型投票
- 人类通过 get_vote() 输入
- 为 AI 投票添加延迟

### 任务执行 (Quest Execution)
```python
# 任务团队成员投票部分
# 当前代码第 300 行左右
for member_name in team_members:
    member = players.name_to_agent[member_name]
    role = players.name_to_role[member_name]
    
    if role in ["merlin", "percival", "loyal"]:
        quest_votes.append("success")
    else:
        # Evil player decides
        ...
```

**需要修改为**:
- 如果是人类玩家，调用 get_quest_vote()
- 如果是 AI，保持原有逻辑
- 添加 AI 延迟

### 邪恶势力讨论 (Evil Discussion)
```python
# 邪恶势力私下讨论
# 当前代码第 242 行左右
if evil_alive:
    async with MsgHub(evil_alive, ...) as evil_hub:
        # Discussion
        ...
```

**需要修改为**:
- 如果人类是邪恶阵营，参与讨论
- 如果人类是好人阵营，不参与邪恶讨论
- AI 发言后添加延迟

## 🔧 实现示例

### 讨论阶段修改示例
```python
# 修改 sequential_pipeline 以支持人类
from agentscope.pipeline import sequential_pipeline

async def mixed_discussion(players_list, human_player, ai_delay):
    """Mixed discussion with AI and human."""
    for player in players_list:
        if isinstance(player, ReActAgent):
            # AI speaks
            await player(structured_model=DiscussionModel)
            await asyncio.sleep(ai_delay)  # Add delay
        elif human_player and player.name == human_player.name:
            # Human speaks
            response = await human_player.get_input("轮到你了，请发言：")
            # Broadcast to all
            await alive_players_hub.broadcast(
                await moderator(f"{human_player.name}: {response}")
            )
```

### 投票阶段修改示例
```python
# 混合投票（AI + 人类）
votes = []
for player in players.current_alive:
    if isinstance(player, ReActAgent):
        # AI votes with structured model
        msg = await player(
            await moderator("Vote YES or NO"),
            structured_model=get_vote_model(["YES", "NO"]),
        )
        votes.append(msg.metadata.get("vote"))
        await asyncio.sleep(ai_delay)
    elif human_player and player.name == human_player.name:
        # Human votes
        vote = await human_player.get_vote(["YES", "NO"])
        votes.append(vote)
```

## 🎯 关键要点

### 1. AI 延迟设置
```python
ai_delay = 3.0  # 秒
# 可在 main.py 中调整
# 建议范围：2.0 - 5.0 秒
```

### 2. 人类玩家身份保护
- ✅ 不透露人类身份
- ✅ 使用统一的 Agent 接口
- ✅ 发言格式一致

### 3. 游戏平衡
- 人类玩家应该有足够时间阅读
- AI 不应该表现得像机器人
- 保持自然的游戏节奏

## 📋 测试清单

- [ ] 人类玩家可以正常发言
- [ ] 人类玩家可以投票
- [ ] AI NPC 发言后有延迟
- [ ] 人类玩家可以看到所有信息
- [ ] AI NPC 不知道是人类
- [ ] 游戏流程正常进行
- [ ] 特殊角色功能正常

## 🚀 下一步

1. 完成 game_avalon.py 的讨论阶段修改
2. 完成投票阶段修改
3. 完成任务执行阶段修改
4. 全面测试游戏流程
5. 调整 AI 延迟时间

---

**状态**: 框架已完成，需要细化各个阶段的处理  
**难度**: 中等  
**预计时间**: 1-2 小时
