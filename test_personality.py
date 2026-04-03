# -*- coding: utf-8 -*-
"""Test script to verify personality assignment and Avalon game setup."""
import asyncio
from personality_loader import (
    load_all_personalities,
    assign_personalities_to_agents,
    get_personality_prompt,
)


def test_personality_loader():
    """Test the personality loader functionality."""
    print("=" * 60)
    print("Testing Personality Loader")
    print("=" * 60)
    
    # Load all personalities
    personalities_dir = "./personalities"
    personalities = load_all_personalities(personalities_dir)
    
    print(f"\n✓ Loaded {len(personalities)} personalities:")
    for p in personalities:
        print(f"  - {p.mbti_type}: {p.name}")
    
    # Create dummy agents
    class DummyAgent:
        def __init__(self, name):
            self.name = name
    
    agents = [DummyAgent(f"Player{i}") for i in range(1, 9)]
    
    # Assign personalities
    assignments = assign_personalities_to_agents(
        agents, 
        personalities_dir, 
        max_duplicates=2
    )
    
    print(f"\n✓ Assigned personalities to {len(assignments)} agents:")
    for agent_name, personality in assignments.items():
        print(f"  - {agent_name}: {personality.mbti_type} - {personality.name}")
    
    # Check for duplicates
    from collections import Counter
    mbti_counts = Counter([p.mbti_type for p in assignments.values()])
    print(f"\n✓ MBTI type distribution:")
    for mbti, count in mbti_counts.items():
        print(f"  - {mbti}: {count} times")
    
    # Test personality prompt generation
    print("\n✓ Sample personality prompt:")
    sample_personality = list(assignments.values())[0]
    prompt = get_personality_prompt(sample_personality)
    print(prompt[:500] + "...")  # Print first 500 chars
    
    print("\n" + "=" * 60)
    print("Personality Loader Test Complete!")
    print("=" * 60)


def test_avalon_roles():
    """Test Avalon role assignment logic."""
    print("\n" + "=" * 60)
    print("Testing Avalon Role Assignment")
    print("=" * 60)
    
    import numpy as np
    
    # Simulate role assignment for different player counts
    for num_players in [5, 6, 7, 8, 9, 10]:
        print(f"\n{num_players} players configuration:")
        
        if num_players <= 6:
            roles = ["merlin", "percival"] + ["loyal"] * (num_players - 4) + ["assassin", "morgana"]
        else:
            evil_count = num_players // 3
            good_count = num_players - evil_count
            roles = ["merlin", "percival"] + ["loyal"] * (good_count - 2)
            roles += ["assassin", "morgana", "mordred"] + ["minion"] * (evil_count - 3)
        
        print(f"  Roles: {', '.join(roles)}")
        print(f"  Good: {roles.count('merlin') + roles.count('percival') + roles.count('loyal')}")
        print(f"  Evil: {roles.count('assassin') + roles.count('morgana') + roles.count('mordred') + roles.count('minion')}")
    
    print("\n" + "=" * 60)
    print("Avalon Role Assignment Test Complete!")
    print("=" * 60)


if __name__ == "__main__":
    test_personality_loader()
    test_avalon_roles()
    print("\n✓ All tests completed successfully!")
