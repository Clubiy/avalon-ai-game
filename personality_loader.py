# -*- coding: utf-8 -*-
"""Personality loader for NPC agents."""
import os
import random
from typing import Dict, List
from dataclasses import dataclass


@dataclass
class Personality:
    """Personality data class."""
    
    name: str
    mbti_type: str
    core_traits: List[str]
    speaking_style: List[str]
    behavior_tendencies: List[str]
    game_strategies: Dict[str, str]
    example_phrases: List[str]


def load_personality(file_path: str) -> Personality:
    """Load personality from a markdown file.
    
    Args:
        file_path: Path to the markdown file
        
    Returns:
        Personality object
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Parse markdown content
    lines = content.split('\n')
    
    personality_data = {
        'name': '',
        'mbti_type': '',
        'core_traits': [],
        'speaking_style': [],
        'behavior_tendencies': [],
        'game_strategies': {},
        'example_phrases': []
    }
    
    current_section = None
    
    for line in lines:
        line = line.strip()
        
        if line.startswith('# '):
            # Title line: "# INTJ - 建筑师型人格"
            personality_data['name'] = line.replace('# ', '').split(' - ')[1]
        elif line.startswith('## '):
            # Section header
            if '基本信息' in line:
                current_section = 'basic_info'
            elif '性格特征' in line:
                current_section = 'core_traits'
            elif '说话风格' in line:
                current_section = 'speaking_style'
            elif '行为倾向' in line:
                current_section = 'behavior_tendencies'
            elif '游戏策略偏好' in line:
                current_section = 'game_strategies'
            elif '典型台词示例' in line:
                current_section = 'example_phrases'
            else:
                current_section = None
        elif line.startswith('- **MBTI 类型**'):
            personality_data['mbti_type'] = line.split(': ')[1].split(' (')[0]
        elif line.startswith('- ') and current_section:
            if current_section == 'core_traits':
                personality_data['core_traits'].append(line[2:])
            elif current_section == 'speaking_style':
                personality_data['speaking_style'].append(line[2:])
            elif current_section == 'behavior_tendencies':
                personality_data['behavior_tendencies'].append(line[2:])
            elif current_section == 'example_phrases':
                personality_data['example_phrases'].append(line[2:].strip('"'))
        elif line.startswith('- 作为好人：') and current_section == 'game_strategies':
            personality_data['game_strategies']['good'] = line.replace('- 作为好人：', '')
        elif line.startswith('- 作为坏人：') and current_section == 'game_strategies':
            personality_data['game_strategies']['evil'] = line.replace('- 作为坏人：', '')
        elif line.startswith('- 投票行为：') and current_section == 'game_strategies':
            personality_data['game_strategies']['voting'] = line.replace('- 投票行为：', '')
    
    return Personality(**personality_data)


def load_all_personalities(personalities_dir: str) -> List[Personality]:
    """Load all personalities from the personalities directory.
    
    Args:
        personalities_dir: Path to the personalities directory
        
    Returns:
        List of Personality objects
    """
    personalities = []
    
    for filename in os.listdir(personalities_dir):
        if filename.endswith('.md'):
            file_path = os.path.join(personalities_dir, filename)
            personality = load_personality(file_path)
            personalities.append(personality)
    
    return personalities


def assign_personalities_to_agents(
    agents: List,
    personalities_dir: str,
    max_duplicates: int = 2
) -> Dict[str, Personality]:
    """Assign personalities to agents randomly with limited duplicates.
    
    Args:
        agents: List of agent objects with 'name' attribute
        personalities_dir: Path to the personalities directory
        max_duplicates: Maximum number of times a personality can be assigned
        
    Returns:
        Dictionary mapping agent names to personalities
    """
    # Load all available personalities
    all_personalities = load_all_personalities(personalities_dir)
    
    # Create a pool of personalities respecting max_duplicates
    personality_pool = []
    for personality in all_personalities:
        personality_pool.extend([personality] * max_duplicates)
    
    # Shuffle the pool
    random.shuffle(personality_pool)
    
    # Assign personalities to agents
    assignments = {}
    for i, agent in enumerate(agents):
        if i < len(personality_pool):
            assignments[agent.name] = personality_pool[i]
        else:
            # If not enough personalities, reuse from the beginning
            assignments[agent.name] = all_personalities[i % len(all_personalities)]
    
    return assignments


def get_personality_prompt(personality: Personality) -> str:
    """Generate a system prompt based on personality.
    
    Args:
        personality: Personality object
        
    Returns:
        System prompt string
    """
    prompt = f"""# Your Personality Profile

You have the following personality traits that should influence your behavior and speech:

## Core Traits
{chr(10).join('- ' + trait for trait in personality.core_traits)}

## Speaking Style
{chr(10).join('- ' + style for style in personality.speaking_style)}

## Behavioral Tendencies
{chr(10).join('- ' + tendency for tendency in personality.behavior_tendencies)}

## Example Phrases
You may use phrases like:
{chr(10).join('- "' + phrase + '"' for phrase in personality.example_phrases[:5])}

Remember to stay in character throughout the game. Your decisions and speech should reflect your personality type ({personality.mbti_type} - {personality.name}).
"""
    return prompt
