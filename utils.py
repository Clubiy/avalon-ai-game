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

MAX_GAME_ROUND = 30
MAX_DISCUSSION_ROUND = 3


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
        if isinstance(agents[0], ReActAgent):
            return agents[0].name
        return agents[0]

    names = []
    for agent in agents:
        if isinstance(agent, ReActAgent):
            names.append(agent.name)
        else:
            names.append(agent)
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
        self.evil = []  # All evil players
        self.good = []  # All good players
        self.merlin = []
        self.percival = []
        self.loyal = []
        self.assassin = []
        self.morgana = []
        self.mordred = []
        self.minion = []
        self.current_alive = []
        self.all_players = []

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
        
        if role in ["merlin", "percival", "loyal"]:
            self.good.append(player)
        else:
            self.evil.append(player)
        
        if role == "merlin":
            self.merlin.append(player)
        elif role == "percival":
            self.percival.append(player)
        elif role == "loyal":
            self.loyal.append(player)
        elif role == "assassin":
            self.assassin.append(player)
        elif role == "morgana":
            self.morgana.append(player)
        elif role == "mordred":
            self.mordred.append(player)
        elif role == "minion":
            self.minion.append(player)
        else:
            raise ValueError(f"Unknown role: {role}")
        self.current_alive.append(player)

    def update_players(self, dead_players: list[ReActAgent]) -> None:
        """Update the current alive players.
    
        Args:
            dead_players (`list[ReActAgent`):
                A list of dead players to be removed.
        """
        self.evil = [_ for _ in self.evil if _.name not in dead_players]
        self.good = [_ for _ in self.good if _.name not in dead_players]
        self.merlin = [_ for _ in self.merlin if _.name not in dead_players]
        self.percival = [_ for _ in self.percival if _.name not in dead_players]
        self.loyal = [_ for _ in self.loyal if _.name not in dead_players]
        self.assassin = [_ for _ in self.assassin if _.name not in dead_players]
        self.morgana = [_ for _ in self.morgana if _.name not in dead_players]
        self.mordred = [_ for _ in self.mordred if _.name not in dead_players]
        self.minion = [_ for _ in self.minion if _.name not in dead_players]
        self.current_alive = [
            _ for _ in self.current_alive if _.name not in dead_players
        ]

    def print_roles(self) -> None:
        """Print the roles of all players."""
        print("Roles:")
        for name, role in self.name_to_role.items():
            print(f" - {name}: {role}")

    def check_winning(self) -> str | None:
        """Check if the game is over and return the winning message."""
        # This is handled in the main game loop for Avalon
        return None
