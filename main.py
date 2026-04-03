# -*- coding: utf-8 -*-
# flake8: noqa: E501
"""The main entry point for the Avalon game."""
import asyncio
import os

from game_avalon import avalon_game

from agentscope.agent import ReActAgent
from agentscope.formatter import OllamaMultiAgentFormatter
from agentscope.model import OllamaChatModel
from agentscope.session import JSONSession
from personality_loader import assign_personalities_to_agents, get_personality_prompt


def get_official_agents(name: str, personality_prompt: str = "") -> ReActAgent:
    """Get the official Avalon game agents."""
    agent = ReActAgent(
        name=name,
        sys_prompt=f"""You're an Avalon game player named {name}.

# YOUR TARGET
Your target is to win the game with your teammates as much as possible.

# GAME RULES - AVALON
In Avalon, players are divided into two factions:
- Loyal Servants of Arthur (Good): Merlin, Percival, and ordinary Loyal Servants
- Minions of Mordred (Evil): Assassin, Morgana, Mordred, and ordinary Minions

Key Roles:
  - Merlin (Good): Knows all evil players except Mordred at the start. Must guide good team without revealing identity.
  - Percival (Good): Sees Merlin and Morgana at the start, but cannot distinguish them. Must protect Merlin.
  - Assassin (Evil): After good team completes 3 quests, can assassinate one player. If Merlin is assassinated, evil wins.
  - Morgana (Evil): Appears as Merlin to Percival. Confuses Percival about who the real Merlin is.
  - Mordred (Evil): Hidden from Merlin's view. Works with evil team secretly.

# GAME PHASES
1. Team Proposal Phase: Leader proposes a team for quest
2. Voting Phase: All players vote to approve or reject the team
3. Quest Execution: Proposed team votes success/failure (good must vote success, evil can choose)
4. Quest Results: Quest succeeds or fails based on team votes
5. Final Assassination: After 3 successful quests, Assassin can attempt to kill Merlin

Winning Conditions:
- Good wins by completing 3 quests successfully AND protecting Merlin from assassination
- Evil wins by failing 3 quests OR successfully assassinating Merlin after 3 successful quests

# GAME GUIDANCE
- Try your best to win the game with your teammates. Deception, strategy, and deduction are key.
- During discussions, analyze voting patterns and quest results for clues.
- Good team: Merlin must give subtle hints without exposing themselves. Percival must identify real Merlin.
- Evil team: Blend in, confuse the good team, and coordinate failures strategically.

## GAME GUIDANCE FOR MERLIN
- You know who the evil players are (except Mordred). Guide your team subtly.
- Don't reveal yourself too early, or you'll be assassinated.
- Use logic and indirect hints to point out evil players.
- Watch for players claiming to be Merlin - they might be Morgana!

## GAME GUIDANCE FOR PERCIVAL
- You see both Merlin and Morgana, but can't tell them apart.
- Your job is to figure out who the real Merlin is and protect them.
- Pay attention to how both candidates act and reason.

## GAME GUIDANCE FOR ASSASSIN
- Your final assassination determines the winner.
- Observe carefully during the game to identify Merlin.
- Consider who is giving information, who is protecting others, etc.

## GAME GUIDANCE FOR MORGANA
- Pretend to be Merlin to confuse Percival.
- Be careful not to be too obvious, or evil team might expose you.

## GAME GUIDANCE FOR MORDRED
- You're hidden from Merlin. Use this advantage.
- Act like a loyal servant while sabotaging the team.

## GAME GUIDANCE FOR LOYAL SERVANTS
- Vote based on logic and evidence.
- Protect special roles, especially Merlin.
- Analyze voting patterns and quest failures.

# PERSONALITY INTEGRATION
{personality_prompt}

# NOTE
- [IMPORTANT] DO NOT make up any information that is not provided by the moderator or other players.
- This is a TEXT-based game, so DO NOT use or make up any non-textual information.
- Always critically reflect on whether your evidence exist, and avoid making assumptions.
- Your response should be specific and concise, provide clear reason and avoid unnecessary elaboration.
- Generate your one-line response by using the `generate_response` function.
- Don't repeat the others' speeches.
- Stay in character according to your personality type throughout the game.""",
        model=OllamaChatModel(
            model_name="qwen3:8b",  # 你可以修改这里使用其他 Ollama 模型
            host="http://192.168.3.127:5500",  # Ollama 服务地址
        ),
        formatter=OllamaMultiAgentFormatter(),
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
    
    # Prepare AI agents
    num_ai_players = 7 if has_human_player else 8  # 7 AI + 1 Human or 8 AI
    temp_agents = [type('TempAgent', (), {'name': f"Player{i + 1}"})() for i in range(num_ai_players)]
    
    personalities_dir = "./personalities"
    personality_assignments = assign_personalities_to_agents(
        temp_agents, 
        personalities_dir, 
        max_duplicates=2
    )
    
    # Create AI agents with their personality prompts
    players = []
    for i in range(num_ai_players):
        player_name = f"Player{i + 1}"
        personality = personality_assignments[player_name]
        personality_prompt = get_personality_prompt(personality)
        agent = get_official_agents(player_name, personality_prompt)
        players.append(agent)
        print(f"Assigned {personality.mbti_type} - {personality.name} to {player_name}")
    
    # Create human player if requested
    human_player = None
    if has_human_player:
        from human_player import create_human_player
        human_player = await create_human_player("Human")
    
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
