# -*- coding: utf-8 -*-
"""Human player input handler for Avalon game."""
import asyncio
from typing import Optional


class HumanPlayer:
    """Human player input handler."""
    
    def __init__(self, name: str):
        """Initialize human player.
        
        Args:
            name: Player's name
        """
        self.name = name
        self.role: Optional[str] = None
    
    async def get_input(self, prompt: str = "") -> str:
        """Get text input from human player.
        
        Args:
            prompt: Prompt to display to the player
            
        Returns:
            Player's input text
        """
        if prompt:
            print(f"\n{'='*60}")
            print(prompt)
            print('='*60)
        
        print(f"\n[{self.name}] 请输入你的发言：")
        user_input = await asyncio.get_event_loop().run_in_executor(
            None, input
        )
        return user_input.strip()
    
    async def get_vote(self, candidates: list, prompt: str = "请选择你要投票的对象：") -> str:
        """Get vote from human player.
        
        Args:
            candidates: List of candidate names
            prompt: Voting prompt
            
        Returns:
            Selected candidate name
        """
        while True:
            print(f"\n{'='*60}")
            print(prompt)
            print(f"可选对象：{', '.join(candidates)}")
            print('='*60)
            
            vote = await self.get_input(f"[{self.name}] 你的投票：")
            
            # Validate vote
            if vote in candidates:
                return vote
            else:
                print(f"❌ 无效的选择，请从以下选项中选择：{', '.join(candidates)}")
    
    async def get_yes_no(self, question: str) -> bool:
        """Get yes/no decision from human player.
        
        Args:
            question: Question to ask
            
        Returns:
            True for yes, False for no
        """
        while True:
            print(f"\n{'='*60}")
            print(question)
            print('='*60)
            
            answer = await self.get_input(f"[{self.name}] 请输入 YES 或 NO：")
            
            if answer.upper() in ['YES', 'Y']:
                return True
            elif answer.upper() in ['NO', 'N']:
                return False
            else:
                print("❌ 无效输入，请输入 YES 或 NO")
    
    async def get_team_proposal(self, candidates: list, team_size: int) -> list:
        """Get team proposal from human leader.
        
        Args:
            candidates: List of all alive players
            team_size: Required team size
            
        Returns:
            List of proposed team members
        """
        while True:
            print(f"\n{'='*60}")
            print(f"作为队长，你需要选择 {team_size} 名玩家执行任务")
            print(f"可选玩家：{', '.join(candidates)}")
            print("请输入玩家名字，用逗号分隔（例如：Player1, Player2, Player3）")
            print('='*60)
            
            selection = await self.get_input(f"[{self.name}] 你的提议：")
            
            # Parse selection
            selected = [name.strip() for name in selection.split(',')]
            
            # Validate team size
            if len(selected) != team_size:
                print(f"❌ 需要选择 exactly {team_size} 名玩家，你选择了 {len(selected)} 名")
                continue
            
            # Validate all selected players are valid
            invalid = [p for p in selected if p not in candidates]
            if invalid:
                print(f"❌ 无效的玩家：{', '.join(invalid)}")
                continue
            
            return selected
    
    async def get_quest_vote(self, is_evil: bool = False) -> str:
        """Get quest success/fail vote from human player.
        
        Args:
            is_evil: Whether the player is on evil team
            
        Returns:
            'success' or 'fail'
        """
        while True:
            print(f"\n{'='*60}")
            print("你需要对任务结果进行投票")
            if is_evil:
                print("你可以选择投成功票或失败票来隐藏身份")
            else:
                print("作为好人阵营，你必须投成功票")
            print('='*60)
            
            vote = await self.get_input(f"[{self.name}] 请输入 SUCCESS 或 FAIL：")
            
            if vote.upper() == 'SUCCESS':
                return 'success'
            elif vote.upper() == 'FAIL':
                if is_evil:
                    return 'fail'
                else:
                    print("⚠️  警告：作为好人阵营，你应该投成功票！确定要投失败票吗？")
                    confirm = await self.get_yes_no("确认投失败票？")
                    if confirm:
                        return 'fail'
            else:
                print("❌ 无效输入，请输入 SUCCESS 或 FAIL")
    
    async def get_assassination_target(self, candidates: list) -> str:
        """Get assassination target from human assassin.
        
        Args:
            candidates: List of possible targets
            
        Returns:
            Target name
        """
        return await self.get_vote(
            candidates, 
            "作为刺客，你需要刺杀一名玩家（如果是梅林，邪恶方获胜）"
        )
    
    async def observe_game(self, message: str):
        """Display game observation to human player.
        
        Args:
            message: Game event message
        """
        print(f"\n{'─'*60}")
        print(message)
        print('─'*60)
    
    async def wait_for_continue(self) -> None:
        """Wait for player to continue."""
        input(f"\n[{self.name}] 按回车键继续...")


async def create_human_player(name: str = "Human") -> HumanPlayer:
    """Create a human player instance.
    
    Args:
        name: Player name
        
    Returns:
        HumanPlayer instance
    """
    player = HumanPlayer(name)
    print(f"\n{'='*60}")
    print(f"欢迎人类玩家 {player.name}！")
    print("你将与其他 AI NPC 一起进行阿瓦隆游戏")
    print("注意：AI NPC 不知道你是人类玩家")
    print("通过文本输入进行发言、投票和决策")
    print('='*60)
    await player.wait_for_continue()
    return player
