# -*- coding: utf-8 -*-
"""The structured output models used in the Avalon game."""
from typing import Literal

from pydantic import BaseModel, Field
from agentscope.agent import AgentBase


class DiscussionModel(BaseModel):
    """The output format for discussion."""

    reach_agreement: bool = Field(
        description="Whether you have reached an agreement or not",
    )


def get_vote_model(agents: list[AgentBase]) -> type[BaseModel]:
    """Get the vote model by player names.
    
    Args:
        agents: List of agent instances
        
    Returns:
        VoteModel class with Literal type for valid player names
    """
    # Convert generator to tuple before using in Literal
    names = tuple(agent.name for agent in agents)
    
    class VoteModel(BaseModel):
        """The vote output format."""

        vote: Literal[names] = Field(
            description="The name of the player you want to vote for",
        )

    return VoteModel


def get_yes_no_vote_model() -> type[BaseModel]:
    """Get a yes/no vote model."""

    class YesNoVoteModel(BaseModel):
        """Yes or No vote output format."""

        vote: Literal["YES", "NO"] = Field(
            description="Vote YES to approve, NO to reject",
        )

    return YesNoVoteModel


def get_quest_vote_model() -> type[BaseModel]:
    """Get a success/fail vote model for quest execution."""

    class QuestVoteModel(BaseModel):
        """Quest vote output format."""

        vote: Literal["success", "fail"] = Field(
            description="Vote 'success' to support the quest, 'fail' to sabotage (evil only)",
        )

    return QuestVoteModel


class WitchResurrectModel(BaseModel):
    """The output format for witch resurrect action."""

    resurrect: bool = Field(
        description="Whether you want to resurrect the player",
    )


def get_poison_model(agents: list[AgentBase]) -> type[BaseModel]:
    """Get the poison model by player names.
    
    Args:
        agents: List of agent instances
        
    Returns:
        WitchPoisonModel class
    """
    # Convert to tuple before using in Literal
    names = tuple(agent.name for agent in agents)

    class WitchPoisonModel(BaseModel):
        """The output format for witch poison action."""

        poison: bool = Field(
            description="Do you want to use the poison potion",
        )
        name: Literal[names] | None = Field(
            description="The name of the player you want to poison, if you "
            "don't want to poison anyone, just leave it empty",
            default=None,
        )

    return WitchPoisonModel


def get_seer_model(agents: list[AgentBase]) -> type[BaseModel]:
    """Get the seer model by player names.
    
    Args:
        agents: List of agent instances
        
    Returns:
        SeerModel class
    """
    # Convert to tuple before using in Literal
    names = tuple(agent.name for agent in agents)

    class SeerModel(BaseModel):
        """The output format for seer action."""

        name: Literal[names] = Field(
            description="The name of the player you want to check",
        )

    return SeerModel


def get_hunter_model(agents: list[AgentBase]) -> type[BaseModel]:
    """Get the hunter model by player agents.
    
    Args:
        agents: List of agent instances
        
    Returns:
        HunterModel class
    """
    # Convert to tuple before using in Literal
    names = tuple(agent.name for agent in agents)

    class HunterModel(BaseModel):
        """The output format for hunter action."""

        shoot: bool = Field(
            description="Whether you want to use the shooting ability or not",
        )
        name: Literal[names] | None = Field(
            description="The name of the player you want to shoot, if you "
            "don't want to the ability, just leave it empty",
            default=None,
        )

    return HunterModel


def get_quest_team_model(agents: list[AgentBase], team_size: int) -> type[BaseModel]:
    """Get the quest team proposal model.
    
    Args:
        agents: List of available players
        team_size: Required size of the quest team
    
    Returns:
        QuestTeamModel class
    """
    # Convert to tuple before using in Literal
    names = tuple(agent.name for agent in agents)
    
    class QuestTeamModel(BaseModel):
        """The output format for quest team proposal."""
        
        team: list[Literal[names]] = Field(
            description=f"List of exactly {team_size} player names for the quest team",
            min_length=team_size,
            max_length=team_size,
        )
    
    return QuestTeamModel
