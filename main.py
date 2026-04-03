# -*- coding: utf-8 -*-
# flake8: noqa: E501
"""The main entry point for the Avalon game."""
import asyncio
import logging
import os

from game_avalon import avalon_game

from agentscope.agent import ReActAgent
from agentscope.formatter import OllamaChatFormatter
from agentscope.model import OllamaChatModel
from agentscope.session import JSONSession
from personality_loader import assign_personalities_to_agents, get_personality_prompt
import os

# 配置 Ollama 服务地址
OLLAMA_BASE_URL = os.environ.get("OLLAMA_HOST", "http://192.168.3.127:5500")

# 过滤 AgentScope 和 Ollama 的警告信息
logging.getLogger("agentscope").setLevel(logging.ERROR)
logging.getLogger("ollama").setLevel(logging.ERROR)


def get_player_letter(i: int) -> str:
    """Convert index to letter (0->A, 1->B, etc.)"""
    return chr(ord('A') + i)


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
            host=OLLAMA_BASE_URL,
        ),
        formatter=OllamaChatFormatter(),
    )
    return agent


async def main() -> None:
    """The main entry point for the Avalon game."""

    # Uncomment the following lines if you want to use Agentscope Studio
    # to visualize the game process.
    # import agentscope
    # agentscope.init(
    #     studio_url="http://localhost:3000",
    #     project="avalon_game",
    # )

    # Ask if user wants to play as human
    print("\n" + "="*60)
    print("欢迎来到阿瓦隆游戏！")
    print("="*60)
    print("\n你想要作为人类玩家参与游戏吗？")
    print("- 选择 YES：你将与 AI NPC 一起游戏")
    print("- 选择 NO：观看 AI NPC 之间的对战")
    print("="*60)
    
    human_input = input("\n请输入 YES 或 NO: ").strip().upper()
    has_human_player = human_input in ['YES', 'Y']
    
    # Prepare AI agents with letter names
    num_ai_players = 7 if has_human_player else 8  # 7 AI + 1 Human or 8 AI
    temp_agents = [type('TempAgent', (), {'name': get_player_letter(i)})() for i in range(num_ai_players)]
    
    personalities_dir = "./personalities"
    personality_assignments = assign_personalities_to_agents(
        temp_agents, 
        personalities_dir, 
        max_duplicates=2
    )
    
    # Create AI agents with their personality prompts
    players = []
    for i in range(num_ai_players):
        player_name = get_player_letter(i)  # Use letters: A, B, C...
        personality = personality_assignments[player_name]
        personality_prompt = get_personality_prompt(personality)
        agent = get_official_agents(player_name, personality_prompt)
        players.append(agent)
        print(f"Assigned {personality.mbti_type} - {personality.name} to {player_name}")
    
    # Create human player if requested
    human_player = None
    if has_human_player:
        from human_player import create_human_player
        # Use letter name for human player (H for 8th player)
        human_name = get_player_letter(num_ai_players)  # H if there are 7 AI players
        human_player = await create_human_player(human_name)
    
    # AI delay setting (seconds)
    ai_delay = 3.0  # Adjust this value as needed

    # Note: You can replace your own agents here, or use all your own agents

    # Load states from a previous checkpoint
    session = JSONSession(save_dir="./checkpoints")
    await session.load_session_state(
        session_id="players_checkpoint",
        **{player.name: player for player in players},
    )

    # Start the game
    await avalon_game(players, personality_assignments, human_player, ai_delay)

    # Save the states to a checkpoint
    await session.save_session_state(
        session_id="players_checkpoint",
        **{player.name: player for player in players},
    )


asyncio.run(main())
