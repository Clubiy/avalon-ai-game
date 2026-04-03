# -*- coding: utf-8 -*-
"""Agent factory for creating Avalon game agents."""
from typing import Optional

from agentscope.agent import ReActAgent
from agentscope.model import OllamaChatModel
from agentscope.formatter import OllamaChatFormatter
from config import GameConfig


def get_player_letter(i: int) -> str:
    """Convert index to letter (0->A, 1->B, etc.)
    
    Args:
        i: Player index (0-based)
        
    Returns:
        Player letter name (A, B, C, ...)
    """
    return chr(ord('A') + i)


def get_official_agents(
    names: list[str],
    personality_prompts: Optional[dict[str, str]] = None,
    model_name: Optional[str] = None,
    host: Optional[str] = None,
) -> list[ReActAgent]:
    """Create official Avalon game agents with Ollama.
    
    Args:
        names: List of agent names
        personality_prompts: Dictionary mapping names to personality prompts
        model_name: Ollama model name (default from config)
        host: Ollama host URL (default from config)
        
    Returns:
        List of ReActAgent instances
    """
    model_name = model_name or GameConfig.DEFAULT_MODEL
    host = host or GameConfig.OLLAMA_HOST
    
    # Remove http:// or https:// prefix if present
    if host.startswith("http://"):
        host = host[7:]
    elif host.startswith("https://"):
        host = host[8:]
    
    agents = []
    for name in names:
        # Get personality prompt if provided
        personality_prompt = ""
        if personality_prompts and name in personality_prompts:
            personality_prompt = personality_prompts[name]
        
        agent = ReActAgent(
            name=name,
            sys_prompt=_build_sys_prompt(name, personality_prompt),
            model=OllamaChatModel(
                model_name=model_name,
                host=host,
            ),
            formatter=OllamaChatFormatter(),
        )
        agents.append(agent)
    
    return agents


def _build_sys_prompt(name: str, personality_prompt: str = "") -> str:
    """Build system prompt for an agent.
    
    Args:
        name: Agent name
        personality_prompt: Personality-specific prompt
        
    Returns:
        Complete system prompt
    """
    base_prompt = f"""你是一个阿瓦隆游戏玩家，名字叫{name}。

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
"""
    return base_prompt


def create_agents_with_personalities(
    num_agents: int,
    personality_assignments: dict,
) -> list[ReActAgent]:
    """Create agents with assigned personalities.
    
    Args:
        num_agents: Number of agents to create
        personality_assignments: Dictionary from personality_loader
        
    Returns:
        List of ReActAgent instances
    """
    from personality_loader import get_personality_prompt
    
    agents = []
    for i in range(num_agents):
        name = get_player_letter(i)
        personality = personality_assignments.get(name)
        
        if personality:
            personality_prompt = get_personality_prompt(personality)
        else:
            personality_prompt = ""
        
        agent = ReActAgent(
            name=name,
            sys_prompt=_build_sys_prompt(name, personality_prompt),
            model=OllamaChatModel(
                model_name=GameConfig.DEFAULT_MODEL,
                host=GameConfig.OLLAMA_HOST,
            ),
            formatter=OllamaChatFormatter(),
        )
        agents.append(agent)
    
    return agents
