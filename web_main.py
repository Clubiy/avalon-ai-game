# -*- coding: utf-8 -*-
"""Main entry point for Avalon web game."""
import asyncio
import sys
from aiohttp import web

from web_server import GameWebSocketServer
from web_human_player import WebHumanPlayer
from main import get_official_agents, get_player_letter
from personality_loader import assign_personalities_to_agents, get_personality_prompt


async def start_web_game(host: str = "0.0.0.0", port: int = 8080):
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


def main():
    """Main function to start web game."""
    host = "0.0.0.0"  # Listen on all interfaces
    port = 8080
    
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
