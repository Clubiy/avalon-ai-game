# -*- coding: utf-8 -*-
"""Main entry point for Avalon web game."""
import asyncio
import sys
from aiohttp import web

from web_server import GameWebSocketServer
from web_human_player import WebHumanPlayer
from game_avalon import avalon_game
from agent_factory import get_player_letter, _build_sys_prompt
from personality_loader import assign_personalities_to_agents, get_personality_prompt
from config import GameConfig


async def start_web_game(host: str = None, port: int = None):
    """Start the Avalon game with web interface."""
    
    # Use config defaults if not specified
    host = host or GameConfig.WEB_HOST
    port = port or GameConfig.WEB_PORT
    
    # Create WebSocket server
    ws_server = GameWebSocketServer(host, port)
    
    print("=" * 60)
    print("🎭 阿瓦隆游戏 Web 服务器")
    print("=" * 60)
    print(f"\n📡 服务器地址：http://{host}:{port}")
    print(f"🌐 请在浏览器中打开上述地址开始游戏\n")
    print("=" * 60)
    
    # Start the server
    runner = web.AppRunner(ws_server.app)
    await runner.setup()
    site = web.TCPSite(runner, host, port)
    await site.start()
    
    # Keep server running
    try:
        while True:
            await asyncio.sleep(3600)
    except KeyboardInterrupt:
        print("\n👋 服务器已关闭")
    finally:
        await runner.cleanup()


async def create_and_start_game(ws_server: GameWebSocketServer, mode: str):
    """Create and start a game session."""
    try:
        # Wait for human player to connect via WebSocket
        if mode == 'player':
            # Wait longer for WebSocket connection and game to initialize
            print("⏳ 等待人类玩家连接...")
            for i in range(10):  # Wait up to 10 seconds
                await asyncio.sleep(1)
                if ws_server.human_player_ws:
                    print("✅ 人类玩家已连接")
                    break
            
            if ws_server.human_player_ws is None:
                print("⚠️ No human player connected, starting spectator mode...")
                mode = 'spectator'
            else:
                # Create human player
                human_player = WebHumanPlayer(ws_server)
                ws_server.human_player = human_player
        
        # Create AI agents - use config for player count
        num_ai_players = 5 if mode == 'player' else 6
        ai_names = [get_player_letter(i) for i in range(num_ai_players)]
        
        # Create temporary agent objects for personality assignment
        class TempAgent:
            def __init__(self, name):
                self.name = name
        
        temp_agents = [TempAgent(name) for name in ai_names]
        
        # Assign personalities - use config for settings
        from personality_loader import Personality
        personality_assignments = assign_personalities_to_agents(
            temp_agents,
            GameConfig.PERSONALITY_DIR,
            max_duplicates=GameConfig.MAX_PERSONALITY_DUPLICATES
        )
        
        # Create actual agents with personality prompts
        ai_agents = []
        for agent_name in ai_names:
            personality = personality_assignments[agent_name]
            personality_prompt = get_personality_prompt(personality)
            
            print(f"Assigned {personality.mbti_type} - {personality.name} to {agent_name}")
            
            from agentscope.agent import ReActAgent
            from agentscope.model import OllamaChatModel
            from agentscope.formatter import OllamaChatFormatter
            agent = ReActAgent(
                name=agent_name,
                sys_prompt=_build_sys_prompt(agent_name, personality_prompt),
                model=OllamaChatModel(
                    host=GameConfig.OLLAMA_HOST,
                    model_name=GameConfig.WEB_MODEL,
                ),
                formatter=OllamaChatFormatter(),
            )
            ai_agents.append(agent)
        
        # Start game - use config for AI delay
        if mode == 'player':
            await avalon_game(
                agents=ai_agents,
                personality_assignments=personality_assignments,
                human_player=human_player,
                ai_delay=GameConfig.AI_DELAY,
                ws_server=ws_server,
            )
        else:
            # Spectator mode - no human player
            await avalon_game(
                agents=ai_agents,
                personality_assignments=personality_assignments,
                human_player=None,
                ai_delay=GameConfig.AI_DELAY,
                ws_server=ws_server,
            )
            
    except Exception as e:
        print(f"❌ 游戏错误：{e}")
        import traceback
        traceback.print_exc()
        # Send error to client
        if ws_server.human_player_ws:
            await ws_server.broadcast_to_human_only({
                "type": "error",
                "content": f"游戏错误：{e}"
            })


def main():
    """Main function to start web game."""
    host = GameConfig.WEB_HOST
    port = GameConfig.WEB_PORT
    
    # Parse command line arguments (override config)
    if len(sys.argv) > 1:
        host = sys.argv[1]
    if len(sys.argv) > 2:
        port = int(sys.argv[2])
    
    # Run the async server
    try:
        asyncio.run(start_web_game(host, port))
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"❌ 错误：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
