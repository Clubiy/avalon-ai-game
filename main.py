# -*- coding: utf-8 -*-
# flake8: noqa: E501
"""The main entry point for the Avalon game."""
import asyncio
import logging

from game_avalon import avalon_game
from agent_factory import get_player_letter
from personality_loader import assign_personalities_to_agents, get_personality_prompt
from config import GameConfig

# 配置日志
logging.getLogger("agentscope").setLevel(logging.ERROR)
logging.getLogger("ollama").setLevel(logging.ERROR)


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
    
    # Assign personalities
    personality_assignments = assign_personalities_to_agents(
        temp_agents, 
        GameConfig.PERSONALITY_DIR, 
        max_duplicates=GameConfig.MAX_PERSONALITY_DUPLICATES
    )
    
    # Create AI agents with their personality prompts
    players = []
    for i in range(num_ai_players):
        player_name = get_player_letter(i)  # Use letters: A, B, C...
        personality = personality_assignments[player_name]
        personality_prompt = get_personality_prompt(personality)
        from agentscope.agent import ReActAgent
        from agentscope.model import OllamaChatModel
        from agentscope.formatter import OllamaChatFormatter
        from agent_factory import _build_sys_prompt
        agent = ReActAgent(
            name=player_name,
            sys_prompt=_build_sys_prompt(player_name, personality_prompt),
            model=OllamaChatModel(
                model_name=GameConfig.DEFAULT_MODEL,
                host=GameConfig.OLLAMA_HOST,
            ),
            formatter=OllamaChatFormatter(),
        )
        players.append(agent)
        print(f"Assigned {personality.mbti_type} - {personality.name} to {player_name}")
    
    # Create human player if requested
    human_player = None
    if has_human_player:
        from human_player import create_human_player
        # Use letter name for human player (H for 8th player)
        human_name = get_player_letter(num_ai_players)  # H if there are 7 AI players
        human_player = await create_human_player(human_name)
    
    # AI delay setting (seconds) - use config
    ai_delay = GameConfig.AI_DELAY

    # Note: You can replace your own agents here, or use all your own agents

    # Load states from a previous checkpoint
    from agentscope.session import JSONSession
    session = JSONSession(save_dir=GameConfig.CHECKPOINT_DIR)
    await session.load_session_state(
        session_id=GameConfig.SESSION_ID,
        **{player.name: player for player in players},
    )

    # Start the game
    await avalon_game(players, personality_assignments, human_player, ai_delay)

    # Save the states to a checkpoint
    await session.save_session_state(
        session_id=GameConfig.SESSION_ID,
        **{player.name: player for player in players},
    )


asyncio.run(main())
