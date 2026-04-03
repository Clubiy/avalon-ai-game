# -*- coding: utf-8 -*-
"""Web-based human player for Avalon game."""
import asyncio
from typing import Optional, Dict, Any
from aiohttp import web


class WebHumanPlayer:
    """Human player that interacts through web interface."""
    
    def __init__(self, name: str, ws_server):
        self.name = name
        self.role: Optional[str] = None
        self.team: Optional[str] = None  # 'good' or 'evil'
        self.ws_server = ws_server
        
        # Queues for communication
        self.input_queue = asyncio.Queue()
        self.current_request: Optional[asyncio.Future] = None
    
    async def wait_for_input(self, prompt: str = "") -> str:
        """Wait for human player to provide input via web interface."""
        # Send prompt to web interface
        await self.ws_server.broadcast_to_human_only({
            "type": "input_request",
            "prompt": prompt
        })
        
        # Wait for response
        try:
            response = await asyncio.wait_for(self.input_queue.get(), timeout=300)
            return response.strip()
        except asyncio.TimeoutError:
            return "我暂时不想发言"
    
    async def submit_input(self, content: str) -> None:
        """Submit input from web interface."""
        await self.input_queue.put(content)
    
    async def observe_game(self, message: str) -> None:
        """Display game messages to human player."""
        await self.ws_server.broadcast_to_human_only({
            "type": "game_message",
            "content": message
        })
    
    async def set_role(self, role: str, team: str) -> None:
        """Set player's role and team."""
        self.role = role
        self.team = team
        
        # Update web interface
        await self.ws_server.broadcast_to_human_only({
            "type": "role_reveal_private",
            "role": role,
            "team": team,
            "content": f"你的角色是 <strong>{self.get_role_name(role)}</strong>"
        })
    
    def get_role_name(self, role: str) -> str:
        """Get Chinese role name."""
        role_names = {
            "merlin": "梅林",
            "percival": "派西维尔",
            "assassin": "刺客",
            "morgana": "莫甘娜",
            "mordred": "莫德雷德",
            "loyal": "忠诚仆人",
            "minion": "爪牙"
        }
        return role_names.get(role, role)
    
    async def get_vote(self, candidates: list, prompt: str = "请选择你要投票的对象：") -> str:
        """Get vote from human player."""
        return await self.wait_for_input(f"{prompt} 可选：{', '.join(candidates)}")
    
    async def get_team_proposal(self, candidates: list, team_size: int) -> list:
        """Get team proposal from human leader."""
        response = await self.wait_for_input(
            f"请提议{team_size}名玩家执行任务：{', '.join(candidates)}"
        )
        # Parse response
        selected = [name.strip() for name in response.replace(',', ' ').split()]
        if len(selected) == team_size:
            return selected
        else:
            # Default: select first N candidates
            return candidates[:team_size]
