# -*- coding: utf-8 -*-
# pylint: disable=too-many-branches, too-many-statements, no-name-in-module
"""An Avalon game implemented by agentscope."""
import asyncio
import re
import numpy as np

from utils import (
    majority_vote,
    names_to_str,
    EchoAgent,
    MAX_GAME_ROUND,
    MAX_DISCUSSION_ROUND,
    Players,
)
from structured_model import (
    DiscussionModel,
    get_vote_model,
    get_quest_team_model,
    get_yes_no_vote_model,
    get_quest_vote_model,
)
from prompt import (
    ChinesePrompts as Prompts,
)  # pylint: disable=no-name-in-module

# Uncomment the following line to use English prompts
# from prompt import EnglishPrompts as Prompts

from human_player import HumanPlayer

from agentscope.agent import ReActAgent
from agentscope.pipeline import (
    MsgHub,
    sequential_pipeline,
    fanout_pipeline,
)


def parse_speech_tag(content: str) -> str:
    """Extract content from <发言：> tag.
    
    Args:
        content: Raw response from model which may contain <发言：> tags
        
    Returns:
        Extracted speech content, or original content if no tag found
    """
    # Try to find <发言：>...</ 发言> pattern
    pattern = r'<发言：>(.*?)</发言>'
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        # Return the content inside the tag
        return match.group(1).strip()
    
    # If no closing tag, try to find opening tag and take everything after
    pattern_open = r'<发言：>(.*)'
    match_open = re.search(pattern_open, content, re.DOTALL)
    
    if match_open:
        return match_open.group(1).strip()
    
    # No tag found, return original content
    return content


moderator = EchoAgent()


async def assassin_stage(
    assassin_agent: ReActAgent,
    players: Players,
    merlin_name: str,
) -> str:
    """The final assassination stage where Assassin tries to kill Merlin."""
    global moderator
    msg_assassin = await assassin_agent(
        await moderator(Prompts.to_hunter.format(name=assassin_agent.name)),
        structured_model=get_vote_model(players.current_alive),
    )
    assassinated_player = msg_assassin.metadata.get("vote", None)
    return assassinated_player


async def avalon_game(
    agents: list[ReActAgent], 
    personality_assignments: dict,
    human_player: HumanPlayer = None,
    ai_delay: float = 3.0,
    ws_server = None,  # WebSocket server for sending messages
) -> None:
    """The main entry of the Avalon game

    Args:
        agents (`list[ReActAgent`):
            A list of AI agents.
        personality_assignments: Dictionary mapping agent names to personalities
        human_player: Optional human player instance
        ai_delay: Delay in seconds after each AI NPC speaks (default: 3.0s)
        ws_server: Optional WebSocket server for web interface
    """
    total_players = len(agents) + (1 if human_player else 0)
    assert total_players >= 5 and total_players <= 10, "Avalon needs 5-10 players."

    # Init the players' status
    players = Players()

    # Quest success/failure counts
    quest_successes = 0
    quest_failures = 0
    
    # Current quest number (1-5)
    current_quest = 0
    
    # Current leader index
    leader_index = 0

    # All participants (AI agents + optional human)
    all_participants = list(agents)
    if human_player:
        # Create a dummy agent for human to participate in MsgHub
        from agentscope.agent import AgentBase
        from agentscope.message import Msg
        
        class HumanAgent(AgentBase):
            """Agent wrapper for human player."""
            def __init__(self, human: HumanPlayer):
                super().__init__()
                self.human = human
                self.name = human.name
                self.role = None
            
            async def reply(self, content: str = "", structured_model=None) -> Msg:
                """Human types their response. Support both normal and structured model modes."""
                # For structured model (like DiscussionModel), just get text input from human
                if structured_model:
                    # Ignore structured model requirement, just get text input
                    response = await self.human.get_input(content if content else "请发表你的看法：")
                else:
                    response = await self.human.get_input(content)
                msg = Msg(self.name, response, role="assistant")
                await self.print(msg)
                return msg
            
            async def observe(self, msg: Msg) -> None:
                """Human observes messages (displays them)."""
                # Display the message to human player
                if hasattr(msg, 'content') and msg.content:
                    await self.human.observe_game(str(msg.content))
        
        human_agent = HumanAgent(human_player)
        all_participants.append(human_agent)

    # Broadcast the game begin message
    async with MsgHub(participants=all_participants) as greeting_hub:
        msg = await moderator(
            Prompts.to_all_new_game.format(names_to_str(all_participants)),
        )
        await greeting_hub.broadcast(msg)
        
        # Send to WebSocket if available
        if ws_server:
            await ws_server.broadcast_public({
                "type": "game_start",
                "content": "游戏开始！"
            })

    # Assign roles to all players (AI + human)
    num_players = total_players
    
    if num_players <= 6:
        roles = ["merlin", "percival"] + ["loyal"] * (num_players - 4) + ["assassin", "morgana"]
    else:
        # 7+ players: add Mordred and more minions
        evil_count = num_players // 3  # Approximately 1/3 evil
        good_count = num_players - evil_count
        roles = ["merlin", "percival"] + ["loyal"] * (good_count - 2)
        roles += ["assassin", "morgana", "mordred"] + ["minion"] * (evil_count - 3)
    
    np.random.shuffle(all_participants)
    np.random.shuffle(roles)

    # Assign roles to AI agents and human player
    ai_idx = 0
    for i, participant in enumerate(all_participants):
        role = roles[i]
        
        if isinstance(participant, ReActAgent):
            # AI agent - show role privately
            await participant.observe(
                await moderator(
                    f"[{participant.name} ONLY] {participant.name}, your role is {role}.",
                ),
            )
            players.add_player(participant, role)
            
            # Add delay after AI receives information
            await asyncio.sleep(ai_delay)
        elif human_player and participant.name == human_player.name:
            # Human player - only show if special role, otherwise keep hidden
            human_player.role = role
            # Only tell human if they have a special role (Merlin, Percival, Assassin, Morgana, Mordred)
            if role in ["merlin", "percival", "assassin", "morgana", "mordred"]:
                role_name = human_player.get_role_name(role)
                await human_player.observe_game(
                    f"[仅你可见] {human_player.name}，你的角色是 {role_name}。"
                )
                # Send to WebSocket
                if ws_server:
                    await ws_server.broadcast_to_human_only({
                        "type": "role_reveal_private",
                        "role": role,
                        "team": "good" if role in ["merlin", "percival", "loyal"] else "evil",
                        "content": f"你的角色是 <strong>{role_name}</strong>"
                    })
            else:
                # For loyal servants, just give a vague hint
                await human_player.observe_game(
                    f"[仅你可见] {human_player.name}，你是一个好人阵营的角色。"
                )
                # Send to WebSocket
                if ws_server:
                    await ws_server.broadcast_to_human_only({
                        "type": "role_reveal_private",
                        "role": "loyal",
                        "team": "good",
                        "content": "你是一个好人阵营的角色"
                    })
            players.add_player(participant, role)

    # Special role information sharing
    # Merlin sees all evil except Mordred
    merlin_agent = players.merlin[0] if players.merlin else None
    evil_names_for_merlin = [p.name for p in players.evil if players.name_to_role[p.name] != "mordred"]
    
    if merlin_agent:
        if isinstance(merlin_agent, ReActAgent):
            await merlin_agent.observe(
                await moderator(
                    Prompts.to_witch_resurrect.format(
                        witch_name=merlin_agent.name,
                        dead_name=names_to_str(evil_names_for_merlin),
                    ),
                ),
            )
            await asyncio.sleep(ai_delay)
        elif human_player and merlin_agent.name == human_player.name:
            await human_player.observe_game(
                f"[仅你可见] 你是梅林！你可以看到除了莫德雷德之外的所有邪恶势力。"
                f"\n邪恶玩家有：{', '.join(evil_names_for_merlin)}"
            )
    
    # Percival sees Merlin and Morgana (but can't distinguish)
    percival_agent = players.percival[0] if players.percival else None
    morgana_agent = players.morgana[0] if players.morgana else None
    
    if percival_agent and merlin_agent and morgana_agent:
        if isinstance(percival_agent, ReActAgent):
            await percival_agent.observe(
                await moderator(
                    Prompts.to_seer.format(
                        percival_agent.name,
                    ),
                ),
            )
            await percival_agent.observe(
                await moderator(
                    f"[PERCIVAL ONLY] You see that {merlin_agent.name} and {morgana_agent.name} are Merlin/Morgana, but you cannot tell which is which.",
                ),
            )
            await asyncio.sleep(ai_delay)
        elif human_player and percival_agent.name == human_player.name:
            await human_player.observe_game(
                f"[仅你可见] 你是派西维尔！你看到 {merlin_agent.name} 和 {morgana_agent.name} 是梅林或莫甘娜，但无法区分他们。"
            )
    
    # Evil players know each other
    if players.evil:
        evil_names = [p.name for p in players.evil]
        for evil_agent in players.evil:
            if isinstance(evil_agent, ReActAgent):
                await evil_agent.observe(
                    await moderator(
                        f"[EVIL FORCES ONLY] {evil_agent.name}, your fellow evil forces are: {names_to_str([n for n in evil_names if n != evil_agent.name])}.",
                    ),
                )
                await asyncio.sleep(ai_delay)
            elif human_player and evil_agent.name == human_player.name:
                fellow_evil = [n for n in evil_names if n != human_player.name]
                await human_player.observe_game(
                    f"[仅你可见] 你是邪恶阵营！你的邪恶队友有：{', '.join(fellow_evil) if fellow_evil else '无（你是唯一的邪恶）'}"
                )

    # Printing the roles
    players.print_roles()

    # GAME BEGIN!
    for _ in range(MAX_GAME_ROUND):
        # Create a MsgHub for all players to broadcast messages
        async with MsgHub(
            participants=players.current_alive,
            enable_auto_broadcast=False,  # manual broadcast only
            name="alive_players",
        ) as alive_players_hub:
            
            # Leader proposes a quest team
            leader = players.current_alive[leader_index % len(players.current_alive)]
            await alive_players_hub.broadcast(
                await moderator(f"{leader.name} is the leader for this quest."),
            )
            
            # Evil forces discuss their strategy (if any evil alive)
            evil_alive = [p for p in players.evil if p.name in [a.name for a in players.current_alive]]
            if evil_alive:
                # Evil discussion - keep it private, don't show to human
                # Automatically reach agreement to speed up the game
                n_evil = len(evil_alive)
                for round_idx in range(1, min(3, MAX_DISCUSSION_ROUND) * n_evil + 1):
                    # AI evil players discuss without showing prompts
                    await evil_alive[round_idx % n_evil](
                        await moderator("Discuss your strategy."),
                        structured_model=DiscussionModel,
                    )
                    # Always reach agreement quickly
                    if round_idx >= n_evil:  # After one round per evil player
                        break
            
            # Leader proposes team members
            quest_size = [2, 3, 4, 3, 4][min(current_quest, 4)]  # Quest sizes for 5 quests
            await alive_players_hub.broadcast(
                await moderator(f"Leader {leader.name} needs to propose {quest_size} players for the quest team."),
            )
            
            # Leader votes for team members
            team_members = None
            while team_members is None:
                # Handle human leader differently (no structured_model)
                if human_player and leader.name == human_player.name:
                    # Human leader proposes team via text input
                    candidates = [p.name for p in players.current_alive]
                    team_members = await human_player.get_team_proposal(candidates, quest_size)
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
                        await moderator(f"Propose {quest_size} players (including yourself) for the quest team from: {names_to_str(players.current_alive)}"),
                        structured_model=get_quest_team_model(players.current_alive, quest_size),
                    )
                    proposed_team = msg_leader_proposal.metadata.get("team", [])
                    if len(proposed_team) == quest_size:
                        team_members = proposed_team
                
                if team_members:
                    await alive_players_hub.broadcast(
                        await moderator(f"{leader.name} proposes the following team: {names_to_str(team_members)}"),
                    )
            
            # All players vote to approve or reject the team
            await alive_players_hub.broadcast(
                await moderator(
                    Prompts.to_all_vote.format(
                        names_to_str(team_members),
                    ),
                ),
            )
            
            msgs_vote = await fanout_pipeline(
                players.current_alive,
                await moderator("Vote YES to approve this team, NO to reject."),
                structured_model=get_yes_no_vote_model(),
                enable_gather=False,
            )
            
            yes_votes = sum(1 for msg in msgs_vote if msg.metadata.get("vote") == "YES")
            no_votes = len(msgs_vote) - yes_votes
            
            voting_result = f"YES: {yes_votes}, NO: {no_votes}"
            team_approved = yes_votes > no_votes
            
            await alive_players_hub.broadcast(
                await moderator(Prompts.to_all_res.format(voting_result, "approved" if team_approved else "rejected")),
            )
            
            # If team rejected, move to next leader
            if not team_approved:
                failed_votes = getattr(players, 'failed_votes', 0) + 1
                if failed_votes >= 5:
                    # 5 failed votes means automatic evil win (optional rule)
                    await moderator("5 teams have been rejected. Evil forces win by default!")
                    break
                leader_index = (leader_index + 1) % len(players.current_alive)
                continue
            
            # Team approved, execute quest
            await alive_players_hub.broadcast(
                await moderator(f"The quest team is: {names_to_str(team_members)}. Now they will vote on the quest outcome."),
            )
            
            # Quest team members vote success or failure
            quest_votes = []
            for member_name in team_members:
                member = players.name_to_agent[member_name]
                role = players.name_to_role[member_name]
                
                # Good players must vote success
                # Evil players can choose to fail or succeed
                if role in ["merlin", "percival", "loyal"]:
                    quest_votes.append("success")
                else:
                    # Evil player decides
                    msg_evil_vote = await member(
                        await moderator("Vote 'success' or 'fail' for this quest. As evil, you can choose to hide or reveal yourself."),
                        structured_model=get_quest_vote_model(),
                    )
                    quest_votes.append(msg_evil_vote.metadata.get("vote", "success"))
            
            # Count quest results
            success_count = quest_votes.count("success")
            fail_count = quest_votes.count("fail")
            
            quest_succeeded = fail_count == 0
            
            await alive_players_hub.broadcast(
                await moderator(f"Quest result: {success_count} successes, {fail_count} failures. The quest {'SUCCEEDED' if quest_succeeded else 'FAILED'}."),
            )
            
            if quest_succeeded:
                quest_successes += 1
            else:
                quest_failures += 1
            
            # Check winning conditions
            if quest_successes >= 3:
                # Good team completed 3 quests, now comes the assassination phase
                await alive_players_hub.broadcast(
                    await moderator("Good team has completed 3 successful quests! Now comes the final assassination..."),
                )
                
                # Assassin tries to kill Merlin
                assassin = players.assassin[0] if players.assassin else None
                if assassin:
                    assassinated = await assassin_stage(assassin, players, merlin_agent.name if merlin_agent else "")
                    await alive_players_hub.broadcast(
                        await moderator(Prompts.to_all_hunter_shoot.format(assassinated)),
                    )
                    
                    if assassinated and merlin_agent and assassinated == merlin_agent.name:
                        await moderator("ASSASSIN KILLED MERLIN! EVIL FORCES WIN! 🐺🎉")
                        break
                    else:
                        await moderator("ASSASSINATION FAILED! LOYAL SERVANTS WIN! 🏘️🎉")
                        break
                else:
                    await moderator("NO ASSASSIN IN GAME! LOYAL SERVANTS WIN! 🏘️🎉")
                    break
            
            elif quest_failures >= 3:
                # Evil team succeeded in failing 3 quests
                await moderator("Evil forces have failed 3 quests! EVIL WINS! 🐺🎉")
                break
            
            # Discussion phase
            current_quest += 1
            leader_index = (leader_index + 1) % len(players.current_alive)
            
            await alive_players_hub.broadcast(
                await moderator(
                    Prompts.to_all_discuss.format(
                        names=names_to_str(players.current_alive),
                    ),
                ),
            )
            
            # Manual discussion loop to support human player and WebSocket
            for player in players.current_alive:
                if human_player and player.name == human_player.name:
                    # Human player discusses via text input
                    response = await human_player.get_input("请发表你的看法：")
                    from agentscope.message import Msg
                    msg_discussion = Msg(player.name, response, role="assistant")
                else:
                    # AI player uses model
                    msg_discussion = await player(
                        await moderator("Please discuss and share your thoughts."),
                        structured_model=DiscussionModel,
                    )
                    discussion_content = msg_discussion.metadata.get("response", "")
                    
                    # Parse <发言：> tag from response
                    display_content = parse_speech_tag(discussion_content)
                    msg_discussion.content = display_content
                
                # Broadcast to all (must be Msg object for MsgHub)
                await alive_players_hub.broadcast(msg_discussion)
                
                # Send to WebSocket if available
                if ws_server:
                    await ws_server.broadcast_public({
                        "type": "discussion",
                        "speaker": msg_discussion.name,
                        "content": msg_discussion.content if hasattr(msg_discussion, 'content') else str(msg_discussion)
                    })
                
                # Add delay after AI speaks
                if not (human_player and player.name == human_player.name):
                    await asyncio.sleep(ai_delay)

    # Game over, each player reflects
    await fanout_pipeline(
        agents=agents,
        msg=await moderator(Prompts.to_all_reflect),
    )
