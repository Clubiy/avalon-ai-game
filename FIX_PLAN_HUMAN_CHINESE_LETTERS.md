# 🔧 综合修复方案 - 人类玩家、中文输出、字母命名

## 📋 需要修复的问题

### 问题 1: HumanAgent 不支持 structured_model
**错误**: `TypeError: Failed to bind parameters for function 'reply': got an unexpected keyword argument 'structured_model'`

**原因**: `HumanAgent` 的 `reply()` 方法只接受 `content` 参数，但游戏代码在队长提议时传入了 `structured_model` 参数。

**解决方案**: 在 `game_avalon.py` 中，为人类玩家单独处理团队提议逻辑。

---

### 问题 2: AI 输出英文而非中文
**需求**: 所有 AI NPC 应该使用中文发言

**解决方案**: 
1. 修改 `main.py` 中的系统提示词为中文
2. 确保 `prompt.py` 中的中文提示词被使用

---

### 问题 3: 玩家命名为 Player1, Player2... 不够直观
**需求**: 使用字母 A、B、C、D 方式命名

**解决方案**: 
- 将玩家命名从 `Player{i+1}` 改为字母 `A`, `B`, `C`, `D`...
- 更新所有相关代码和显示

---

## ✅ 修复步骤

### 步骤 1: 修改玩家命名为字母

**文件**: `main.py`

**修改位置**: 第 127-134 行左右

**原代码**:
```python
temp_agents = [type('TempAgent', (), {'name': f"Player{i + 1}"})() for i in range(num_ai_players)]

# ... later ...

for i in range(num_ai_players):
    player_name = f"Player{i + 1}"
```

**新代码**:
```python
# 使用字母命名：A, B, C, D, E, F, G, H
def get_player_letter(i: int) -> str:
    """Convert index to letter (0->A, 1->B, etc.)"""
    return chr(ord('A') + i)

temp_agents = [type('TempAgent', (), {'name': get_player_letter(i)})() for i in range(num_ai_players)]

# ... later ...

for i in range(num_ai_players):
    player_name = get_player_letter(i)
```

---

### 步骤 2: 修改 AI 系统提示词为中文

**文件**: `main.py`

**修改位置**: `get_official_agents()` 函数中的 sys_prompt

**原代码** (英文):
```python
sys_prompt=f"""You're an Avalon game player named {name}.

# YOUR TARGET
Your target is to win the game with your teammates as much as possible.
...
"""
```

**新代码** (中文):
```python
sys_prompt=f"""你是一个阿瓦隆游戏玩家，名字叫{name}。

# 你的目标
尽可能与你的队友一起赢得游戏。

# 游戏规则 - 阿瓦隆
在阿瓦隆游戏中，玩家分为两个阵营：
- 好人阵营：梅林、派西维尔、忠诚仆人
- 邪恶阵营：刺客、莫甘娜、莫德雷德、爪牙
...

# 重要提示
- 请使用中文发言！
- 保持你的发言简洁明了。
- 使用逻辑推理和分析。
"""
```

---

### 步骤 3: 启用中文提示词

**文件**: `game_avalon.py`

**修改位置**: 导入语句部分（第 20-23 行）

**原代码**:
```python
from prompt import (
    EnglishPrompts as Prompts,
)  # pylint: disable=no-name-in-module

# Uncomment the following line to use Chinese prompts
# from prompt import ChinesePrompts as Prompts
```

**新代码**:
```python
# from prompt import (
#     EnglishPrompts as Prompts,
# )  # pylint: disable=no-name-in-module

# Use Chinese prompts
from prompt import ChinesePrompts as Prompts
```

---

### 步骤 4: 修复 HumanAgent 的团队提议逻辑

**文件**: `game_avalon.py`

**修改位置**: 第 279 行左右，队长提议部分

**原代码**:
```python
msg_leader_proposal = await leader(
    await moderator(Prompts.to_leader.format(...)),
    structured_model=get_quest_team_model(players.current_alive, quest_team_size),
)
```

**新代码**:
```python
# Handle human leader differently (no structured_model)
if human_player and leader.name == human_player.name:
    # Human leader proposes team via text input
    candidates = [p.name for p in players.current_alive]
    team_members = await human_player.get_team_proposal(candidates, quest_team_size)
    # Create a mock message
    from agentscope.message import Msg
    msg_leader_proposal = Msg(
        name=human_player.name,
        content=f"I propose the team: {', '.join(team_members)}",
        role="assistant"
    )
else:
    # AI leader uses structured model
    msg_leader_proposal = await leader(
        await moderator(Prompts.to_leader.format(...)),
        structured_model=get_quest_team_model(players.current_alive, quest_team_size),
    )
```

---

## 🎯 完整代码示例

### main.py 中的关键修改

```python
def get_player_letter(i: int) -> str:
    """Convert index to letter (0->A, 1->B, etc.)"""
    return chr(ord('A') + i)

async def main() -> None:
    """The main entry point for the Avalon game."""
    
    # ... welcome dialog ...
    
    # Prepare AI agents with letter names
    num_ai_players = 7 if has_human_player else 8
    temp_agents = [type('TempAgent', (), {'name': get_player_letter(i)})() 
                   for i in range(num_ai_players)]
    
    # ... personality assignment ...
    
    # Create AI agents with their personality prompts
    players = []
    for i in range(num_ai_players):
        player_name = get_player_letter(i)  # Use letters: A, B, C...
        personality = personality_assignments[player_name]
        personality_prompt = get_personality_prompt(personality)
        agent = get_official_agents(player_name, personality_prompt)  # This now uses Chinese prompt
        players.append(agent)
        print(f"Assigned {personality.mbti_type} - {personality.name} to {player_name}")
    
    # ... rest of the code ...
```

### get_official_agents 完整中文版本

```python
def get_official_agents(name: str, personality_prompt: str = "") -> ReActAgent:
    """Get the official Avalon game agents."""
    agent = ReActAgent(
        name=name,
        sys_prompt=f"""你是一个阿瓦隆游戏玩家，名字叫{name}。

# 你的目标
尽可能与你的队友一起赢得游戏。

# 游戏规则 - 阿瓦隆
在阿瓦隆游戏中，玩家分为两个阵营：
- 好人阵营：梅林、派西维尔、忠诚仆人
- 邪恶阵营：刺客、莫甘娜、莫德雷德、爪牙

关键角色：
  - 梅林（好人）：知道所有邪恶玩家（除了莫德雷德）。要在隐藏身份的同时引导好人。
  - 派西维尔（好人）：能看到梅林和莫甘娜，但无法区分。必须保护梅林。
  - 刺客（邪恶）：好人完成 3 次任务后，可以刺杀一名玩家。如果刺中梅林，邪恶获胜。
  - 莫甘娜（邪恶）：在派西维尔面前伪装成梅林。迷惑派西维尔。
  - 莫德雷德（邪恶）：不会被梅林看到。暗中协助邪恶阵营。

# 游戏阶段
1. 团队提议阶段：队长提议执行任务的团队
2. 投票阶段：所有玩家投票是否通过该团队
3. 任务执行：团队成员投票任务成功/失败（好人必须投成功，邪恶可选择）
4. 任务结果：根据投票决定任务成败
5. 最终刺杀：好人完成 3 次成功后，刺客尝试刺杀梅林

胜利条件：
- 好人获胜：完成 3 次成功任务 AND 保护梅林不被刺杀
- 邪恶获胜：破坏 3 次任务 OR 成功刺杀梅林

# 游戏建议
- 尽全力与队友赢得游戏。欺骗、策略和推理是关键。
- 讨论时分析投票模式和任务结果寻找线索。
- 发言要有逻辑，给出你的分析和推理。
- 作为好人要找出坏人，作为坏人要隐藏自己。

{personality_prompt}

# 重要提示
- 请使用中文发言！
- 保持你的发言简洁明了。
- 使用逻辑推理和分析。
""",
        model=OllamaChatModel(
            model_name="qwen3:8b",
            formatter=OllamaMultiAgentFormatter(),
        ),
    )
    return agent
```

---

## 📊 预期效果

### 游戏开始时
```
============================================================
欢迎来到阿瓦隆游戏！
============================================================

你想要作为人类玩家参与游戏吗？
- 选择 YES：你将与 AI NPC 一起游戏
- 选择 NO：观看 AI NPC 之间的对战
============================================================

请输入 YES 或 NO: yes
Assigned INFP - 调停者型人格 to A
Assigned INFJ - 提倡者型人格 to B
Assigned ISFP - 探险家型人格 to C
Assigned ESFJ - 执政官型人格 to D
Assigned ENTP - 辩论家型人格 to E
Assigned INFP - 调停者型人格 to F
Assigned ESTJ - 总经理型人格 to G

============================================================
欢迎人类玩家 Human！
...
```

### 游戏进行中
```
Moderator: A new game is starting, the players are: A, B, C, D, E, F, G, and Human.
...
[AI 发言全部使用中文]
A: 我认为我们应该仔细分析上一轮的投票...
B: 我同意 A 的观点，但是...
...
```

---

## ✅ 测试清单

- [ ] 玩家命名为字母 A, B, C, D...
- [ ] AI NPC 全部使用中文发言
- [ ] 人类玩家可以正常提议团队
- [ ] 游戏流程正常进行
- [ ] 所有提示词为中文

---

**状态**: ⏳ 待修复  
**优先级**: 高  
**预计时间**: 30 分钟
