# -*- coding: utf-8 -*-
"""Game configuration for Avalon game."""
import os


class GameConfig:
    """Centralized configuration for the Avalon game."""
    
    # ==================== AI/Model Settings ====================
    OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://192.168.3.127:5500")
    DEFAULT_MODEL = "qwen3:8b"
    WEB_MODEL = "qwen3:8b"  # Model for web interface
    
    # ==================== Web Server Settings ====================
    WEB_HOST = "0.0.0.0"
    WEB_PORT = 8182
    WEBSOCKET_TIMEOUT = 300  # seconds
    
    # ==================== Game Settings ====================
    MIN_PLAYERS = 5
    MAX_PLAYERS = 10
    MAX_GAME_ROUNDS = 30
    MAX_DISCUSSION_ROUNDS = 3
    AI_DELAY = 3.0  # seconds between AI actions
    
    # ==================== Quest Configuration ====================
    # Quest sizes by total player count (5-10 players)
    QUEST_SIZES = {
        5: [2, 3, 2, 3, 3],
        6: [2, 3, 4, 3, 4],
        7: [2, 3, 3, 4, 4],
        8: [3, 4, 4, 5, 5],
        9: [3, 4, 4, 5, 5],
        10: [3, 4, 4, 5, 5],
    }
    
    # Players needed for each quest (7+ players need extra fail vote)
    # Format: {total_players: {quest_number: (team_size, need_fail_vote)}}
    QUEST_REQUIREMENTS = {
        5: {1: (2, False), 2: (3, False), 3: (2, False), 4: (3, False), 5: (3, False)},
        6: {1: (2, False), 2: (3, False), 3: (4, False), 4: (3, False), 5: (4, False)},
        7: {1: (2, False), 2: (3, False), 3: (3, False), 4: (4, False), 5: (4, False)},
        8: {1: (3, False), 2: (4, False), 3: (4, False), 4: (5, True), 5: (5, True)},
        9: {1: (3, False), 2: (4, False), 3: (4, False), 4: (5, True), 5: (5, True)},
        10: {1: (3, False), 2: (4, False), 3: (4, False), 4: (5, True), 5: (5, True)},
    }
    
    # ==================== Role Configuration ====================
    # Role assignment by player count
    @staticmethod
    def get_roles(num_players: int) -> list[str]:
        """Get role list for given player count.
        
        Args:
            num_players: Total number of players (5-10)
            
        Returns:
            List of roles to assign
        """
        if num_players <= 6:
            return ["merlin", "percival"] + ["loyal"] * (num_players - 4) + ["assassin", "morgana"]
        else:
            # 7+ players: add Mordred and more minions
            evil_count = num_players // 3  # Approximately 1/3 evil
            good_count = num_players - evil_count
            roles = ["merlin", "percival"] + ["loyal"] * (good_count - 2)
            roles += ["assassin", "morgana", "mordred"] + ["minion"] * (evil_count - 3)
            return roles
    
    # ==================== Personality Settings ====================
    PERSONALITY_DIR = "./personalities"
    MAX_PERSONALITY_DUPLICATES = 2
    
    # ==================== Game Paths ====================
    CHECKPOINT_DIR = "./checkpoints"
    SESSION_ID = "players_checkpoint"
    
    # ==================== Message Settings ====================
    LANGUAGE = "chinese"  # "chinese" or "english"
    
    @classmethod
    def get_quest_size(cls, num_players: int, quest_round: int) -> int:
        """Get quest team size for current round.
        
        Args:
            num_players: Total number of players
            quest_round: Current quest round (1-5)
            
        Returns:
            Number of players needed for the quest
        """
        quest_sizes = cls.QUEST_SIZES.get(num_players, cls.QUEST_SIZES[8])
        return quest_sizes[min(quest_round - 1, 4)]
    
    @classmethod
    def needs_fail_vote(cls, num_players: int, quest_round: int) -> bool:
        """Check if quest needs a fail vote to fail (4th quest in 7+ player games).
        
        Args:
            num_players: Total number of players
            quest_round: Current quest round (1-5)
            
        Returns:
            True if at least one fail vote is needed
        """
        requirements = cls.QUEST_REQUIREMENTS.get(num_players, cls.QUEST_REQUIREMENTS[8])
        return requirements.get(quest_round, (3, False))[1]


# Role definitions for cleaner code
class RoleDefs:
    """Role-related definitions."""
    
    GOOD_ROLES = ["merlin", "percival", "loyal"]
    EVIL_ROLES = ["assassin", "morgana", "mordred", "minion"]
    SPECIAL_ROLES = GOOD_ROLES + EVIL_ROLES
    
    # Special vision roles
    VISION_ROLES = {
        "merlin": "good",      # Sees all evil except Mordred
        "percival": "seer",    # Sees Merlin and Morgana
        "morgana": "seer",     # Appears as Merlin to Percival
    }
    
    # Chinese names
    CHINESE_NAMES = {
        "merlin": "梅林",
        "percival": "派西维尔",
        "assassin": "刺客",
        "morgana": "莫甘娜",
        "mordred": "莫德雷德",
        "loyal": "忠诚仆人",
        "minion": "爪牙",
    }
    
    @staticmethod
    def is_good(role: str) -> bool:
        """Check if role is on good team."""
        return role in RoleDefs.GOOD_ROLES
    
    @staticmethod
    def is_evil(role: str) -> bool:
        """Check if role is on evil team."""
        return role in RoleDefs.EVIL_ROLES
    
    @staticmethod
    def get_chinese_name(role: str) -> str:
        """Get Chinese name for role."""
        return RoleDefs.CHINESE_NAMES.get(role, role)


# Export convenience
config = GameConfig
