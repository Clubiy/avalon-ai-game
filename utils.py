# -*- coding: utf-8 -*-
"""Utility functions for the Avalon game."""
from collections import defaultdict
from typing import Any

import numpy as np
from agentscope.agent import AgentBase, ReActAgent
from agentscope.message import Msg
from prompt import (  # pylint: disable=no-name-in-module
    EnglishPrompts as Prompts,
)
from config import GameConfig, RoleDefs

# Import game config
MAX_GAME_ROUND = GameConfig.MAX_GAME_ROUNDS
MAX_DISCUSSION_ROUND = GameConfig.MAX_DISCUSSION_ROUNDS


def majority_vote(votes: list[str]) -> tuple:
    """Return the vote with the most counts."""
    result = max(set(votes), key=votes.count)
    names, counts = np.unique(votes, return_counts=True)
    conditions = ", ".join(
        [f"{name}: {count}" for name, count in zip(names, counts)],
    )
    return result, conditions


def names_to_str(agents: list[str] | list[ReActAgent]) -> str:
    """Return a string of agent names."""
    if not agents:
        return ""

    if len(agents) == 1:
        if hasattr(agents[0], 'name'):
            return agents[0].name
        return str(agents[0])

    names = []
    for agent in agents:
        # Handle both ReActAgent and HumanAgent (or any AgentBase subclass)
        if hasattr(agent, 'name'):
            names.append(agent.name)
        else:
            # Fallback for string inputs
            names.append(str(agent))
    return ", ".join([*names[:-1], "and " + names[-1]])


class EchoAgent(AgentBase):
    """Echo agent that repeats the input message."""

    def __init__(self) -> None:
        super().__init__()
        self.name = "Moderator"

    async def reply(self, content: str) -> Msg:
        """Repeat the input content with its name and role."""
        msg = Msg(
            self.name,
            content,
            role="assistant",
        )
        await self.print(msg)
        return msg

    async def handle_interrupt(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> Msg:
        """Handle interrupt."""

    async def observe(self, msg: Msg | list[Msg] | None) -> None:
        """Observe the user's message."""


class Players:
    """Maintain the players' status."""

    def __init__(self) -> None:
        """Initialize the players."""
        # The mapping from player name to role
        self.name_to_role = {}
        self.role_to_names = defaultdict(list)
        self.name_to_agent = {}
        
        # Team lists
        self.evil: list = []  # All evil players
        self.good: list = []  # All good players
        
        # Special role lists (using lists for potential multiple of same role)
        self.merlin: list = []
        self.percival: list = []
        self.loyal: list = []
        self.assassin: list = []
        self.morgana: list = []
        self.mordred: list = []
        self.minion: list = []
        
        # Role lists dictionary for dynamic access
        self._role_lists = {
            "merlin": self.merlin,
            "percival": self.percival,
            "loyal": self.loyal,
            "assassin": self.assassin,
            "morgana": self.morgana,
            "mordred": self.mordred,
            "minion": self.minion,
        }
        
        self.current_alive: list = []
        self.all_players: list = []
        
        # Game state
        self.failed_votes = 0  # Track consecutive failed team proposals
        self.total_players = 0

    def add_player(self, player: ReActAgent, role: str) -> None:
        """Add a player to the game.

        Args:
            player (`ReActAgent`):
                The player to be added.
            role (`str`):
                The role of the player.
        """
        self.name_to_role[player.name] = role
        self.name_to_agent[player.name] = player
        self.role_to_names[role].append(player.name)
        self.all_players.append(player)
        self.total_players = len(self.all_players)
        
        # Add to team lists
        if RoleDefs.is_good(role):
            self.good.append(player)
        elif RoleDefs.is_evil(role):
            self.evil.append(player)
        
        # Add to role-specific list if exists
        if role in self._role_lists:
            self._role_lists[role].append(player)
        
        self.current_alive.append(player)

    def get_role_list(self, role: str) -> list:
        """Get list of players with a specific role.
        
        Args:
            role: Role name (e.g., 'merlin', 'assassin')
            
        Returns:
            List of players with that role
        """
        return self._role_lists.get(role, [])

    def update_players(self, dead_players: list[ReActAgent]) -> None:
        """Update the current alive players.
    
        Args:
            dead_players (`list[ReActAgent]`):
                A list of dead players to be removed.
        """
        dead_names = [p.name for p in dead_players]
        
        # Update all role lists
        for role, player_list in self._role_lists.items():
            self._role_lists[role] = [p for p in player_list if p.name not in dead_names]
        
        # Sync list variables
        self.merlin = self._role_lists["merlin"]
        self.percival = self._role_lists["percival"]
        self.loyal = self._role_lists["loyal"]
        self.assassin = self._role_lists["assassin"]
        self.morgana = self._role_lists["morgana"]
        self.mordred = self._role_lists["mordred"]
        self.minion = self._role_lists["minion"]
        
        self.good = [p for p in self.good if p.name not in dead_names]
        self.evil = [p for p in self.evil if p.name not in dead_names]
        self.current_alive = [p for p in self.current_alive if p.name not in dead_names]

    def print_roles(self) -> None:
        """Print the roles of all players."""
        print("Roles:")
        for name, role in self.name_to_role.items():
            print(f" - {name}: {role}")

    def check_winning(self) -> str | None:
        """Check if the game is over and return the winning message."""
        # This is handled in the main game loop for Avalon
        return None
