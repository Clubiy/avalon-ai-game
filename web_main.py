# -*- coding: utf-8 -*-
"""Main entry point for Avalon web game."""
import asyncio
import sys
from aiohttp import web

from web_server import GameWebSocketServer
from web_human_player import WebHumanPlayer
from game_avalon import avalon_game
from main import get_official_agents, get_player_letter
from personality_loader import assign_personalities_to_agents, get_personality_prompt
from human_player import HumanPlayer


async def start_web_game(host: str = "0.0.0.0", port: int = 8183):
    """Start the Avalon game with web interface."""
    
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
            # Wait a bit for WebSocket connection
            await asyncio.sleep(2)
            
            if ws_server.human_player_ws is None:
                print("⚠️ No human player connected, starting spectator mode...")
                mode = 'spectator'
            else:
                # Create human player
                human_player = WebHumanPlayer(ws_server)
                ws_server.human_player = human_player
                ws_server.set_human_player(human_player)
        
        # Create AI agents
        num_ai_players = 5 if mode == 'player' else 6
        ai_names = [get_player_letter(i) for i in range(num_ai_players)]
        
        # Get personality prompts and assign personalities
        personality_prompt = get_personality_prompt()
        ai_agents = get_official_agents(
            names=ai_names,
            personality_prompt=personality_prompt,
        )
        
        # Assign personalities
        personality_assignments = assign_personalities_to_agents(
            ai_agents,
            personality_prompt,
        )
        
        # Start game
        if mode == 'player':
            await avalon_game(
                agents=ai_agents,
                personality_assignments=personality_assignments,
                human_player=human_player,
                ai_delay=3.0,
                ws_server=ws_server,
            )
        else:
            # Spectator mode - no human player
            await avalon_game(
                agents=ai_agents,
                personality_assignments=personality_assignments,
                human_player=None,
                ai_delay=3.0,
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
    host = "0.0.0.0"  # Listen on all interfaces
    port = 8182
    
    # Parse command line arguments
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
