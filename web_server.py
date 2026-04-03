# -*- coding: utf-8 -*-
"""WebSocket server for Avalon game web interface."""
import asyncio
import json
from typing import Set, Optional, Dict, Any
from aiohttp import web, WSMsgType


class GameWebSocketServer:
    """WebSocket server for real-time game communication."""
    
    def __init__(self, host: str = "localhost", port: int = 8080):
        self.host = host
        self.port = port
        self.app = web.Application()
        self.app.router.add_get("/", self.index_handler)
        self.app.router.add_get("/ws", self.websocket_handler)
        self.app.router.add_post("/api/start_game", self.start_game_handler)
        
        # Store connected clients
        self.clients: Set[web.WebSocketResponse] = set()
        self.human_player_ws: Optional[web.WebSocketResponse] = None
        self.human_player = None  # Reference to WebHumanPlayer instance
        self.game_messages: list = []
        self.game_started = False
        self.player_mode = None  # 'player' or 'spectator'
        
    async def index_handler(self, request: web.Request) -> web.Response:
        """Serve the main HTML page."""
        html_content = self.get_html_template()
        return web.Response(text=html_content, content_type="text/html")
    
    async def start_game_handler(self, request: web.Request) -> web.Response:
        """Handle game start request."""
        try:
            data = await request.json()
            mode = data.get('mode', 'player')  # 'player' or 'spectator'
            
            self.player_mode = mode
            self.game_started = True
            
            # Start game in background
            asyncio.create_task(self.start_game_logic(mode))
            
            # Send confirmation to client
            return web.json_response({
                'success': True,
                'message': f'Game started in {mode} mode',
                'mode': mode
            })
        except Exception as e:
            return web.json_response({
                'success': False,
                'error': str(e)
            }, status=400)
    
    async def start_game_logic(self, mode: str):
        """Start the actual game logic."""
        from web_main import create_and_start_game
        await create_and_start_game(self, mode)
    
    async def websocket_handler(self, request: web.Request) -> web.WebSocketResponse:
        """Handle WebSocket connections."""
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        
        self.clients.add(ws)
        print(f"Client connected. Total clients: {len(self.clients)}")
        
        # First client is the human player
        if self.human_player_ws is None:
            self.human_player_ws = ws
            print("✅ Human player WebSocket connection established")
        
        # Send all previous messages to new client
        for msg in self.game_messages:
            await ws.send_json(msg)
        
        try:
            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    # Handle messages from client (e.g., human player input)
                    data = json.loads(msg.data)
                    await self.handle_client_message(data)
                elif msg.type == WSMsgType.ERROR:
                    print(f"WebSocket error: {ws.exception()}")
        finally:
            self.clients.discard(ws)
            if ws == self.human_player_ws:
                self.human_player_ws = None
            print(f"Client disconnected. Total clients: {len(self.clients)}")
        
        return ws
    
    async def handle_client_message(self, data: Dict[str, Any]) -> None:
        """Handle messages received from clients."""
        # This will be used to receive human player actions
        print(f"Received from client: {data}")
        
        # Handle different message types
        msg_type = data.get("type", "")
        
        if msg_type == "player_message":
            # Human player submitted a message
            content = data.get("content", "")
            if self.human_player and hasattr(self.human_player, 'submit_input'):
                await self.human_player.submit_input(content)
        
        # Forward to game engine or store for processing
        # The game engine will listen for these messages
    
    async def broadcast_to_all(self, message: Dict[str, Any]) -> None:
        """Broadcast message to all connected clients."""
        if not self.clients:
            return
        
        # Store message history
        self.game_messages.append(message)
        
        # Broadcast to all clients
        for ws in self.clients.copy():
            try:
                await ws.send_json(message)
            except Exception as e:
                print(f"Error sending to client: {e}")
                self.clients.discard(ws)
    
    async def broadcast_to_human_only(self, message: Dict[str, Any]) -> None:
        """Send message only to human player's client."""
        if self.human_player_ws and not self.human_player_ws.closed:
            try:
                await self.human_player_ws.send_json(message)
            except Exception as e:
                print(f"Error sending to human player: {e}")
    
    async def broadcast_public(self, message: Dict[str, Any]) -> None:
        """
        Broadcast public messages that everyone can see.
        Filter out private information.
        """
        # Only broadcast if it's a public message type
        public_types = [
            "game_start", "role_reveal_public", "discussion", 
            "vote_result", "quest_result", "game_end"
        ]
        
        if message.get("type") in public_types:
            await self.broadcast_to_all(message)
    
    def set_human_player_ws(self, ws: web.WebSocketResponse) -> None:
        """Set the human player's WebSocket connection."""
        self.human_player_ws = ws
        print("Human player connected")
    
    def get_html_template(self) -> str:
        """Return the HTML template for the game interface."""
        return '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>阿瓦隆游戏</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Microsoft YaHei', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        
        .container {
            width: 100%;
            max-width: 1200px;
            height: 90vh;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .header h1 {
            font-size: 2em;
            margin-bottom: 10px;
        }
        
        .identity-panel {
            background: #f8f9fa;
            padding: 15px 20px;
            border-bottom: 2px solid #e9ecef;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .identity-info {
            display: flex;
            gap: 20px;
            align-items: center;
        }
        
        .identity-badge {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 1.1em;
        }
        
        .team-badge {
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: bold;
        }
        
        .team-good {
            background: #d4edda;
            color: #155724;
        }
        
        .team-evil {
            background: #f8d7da;
            color: #721c24;
        }
        
        .chat-container {
            flex: 1;
            overflow-y: auto;
            overflow-x: hidden;
            padding: 20px;
            background: #f8f9fa;
            min-height: 0; /* Important for flex item scrolling */
            max-height: calc(100vh - 250px); /* Ensure input area stays visible */
        }
        
        .message {
            margin-bottom: 15px;
            animation: fadeIn 0.3s ease-in;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .message.moderator {
            text-align: center;
            color: #6c757d;
            font-style: italic;
            margin: 20px 0;
        }
        
        .message.npc {
            display: flex;
            flex-direction: column;
            align-items: flex-start;
        }
        
        .message.npc .speaker {
            font-weight: bold;
            color: #667eea;
            margin-bottom: 5px;
        }
        
        .message.npc .content {
            background: white;
            padding: 12px 16px;
            border-radius: 12px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            max-width: 70%;
            line-height: 1.6;
            word-wrap: break-word;
            overflow-wrap: break-word;
            white-space: pre-wrap;
        }
        
        .message.private {
            border-left: 4px solid #667eea;
            padding-left: 15px;
            background: #e7f3ff;
        }
        
        .input-area {
            border-top: 2px solid #e9ecef;
            padding: 20px;
            background: white;
        }
        
        .input-area textarea {
            width: 100%;
            min-height: 80px;
            padding: 15px;
            border: 2px solid #e9ecef;
            border-radius: 10px;
            resize: vertical;
            font-family: inherit;
            font-size: 1em;
            margin-bottom: 10px;
        }
        
        .input-area textarea:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .button-group {
            display: flex;
            gap: 10px;
            justify-content: flex-end;
        }
        
        .btn {
            padding: 10px 25px;
            border: none;
            border-radius: 8px;
            font-size: 1em;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        
        .btn-secondary {
            background: #6c757d;
            color: white;
        }
        
        .btn-secondary:hover {
            background: #5a6268;
        }
        
        .welcome-panel {
            padding: 40px;
            text-align: center;
            background: white;
        }
        
        .welcome-panel h2 {
            font-size: 2em;
            color: #667eea;
            margin-bottom: 20px;
        }
        
        .welcome-panel p {
            font-size: 1.2em;
            color: #6c757d;
            margin-bottom: 30px;
        }
        
        .mode-selection {
            display: flex;
            gap: 20px;
            justify-content: center;
            margin-bottom: 30px;
        }
        
        .mode-card {
            padding: 30px;
            border: 2px solid #e9ecef;
            border-radius: 15px;
            cursor: pointer;
            transition: all 0.3s;
            width: 300px;
        }
        
        .mode-card:hover {
            border-color: #667eea;
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(102, 126, 234, 0.2);
        }
        
        .mode-card.selected {
            border-color: #667eea;
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
        }
        
        .mode-card h3 {
            color: #667eea;
            margin-bottom: 10px;
        }
        
        .mode-card p {
            color: #6c757d;
            font-size: 0.9em;
        }
        
        .start-button-area {
            margin-top: 30px;
        }
        
        .btn-large {
            padding: 15px 50px;
            font-size: 1.2em;
        }
        
        /* Scrollbar styling */
        .chat-container::-webkit-scrollbar {
            width: 8px;
        }
        
        .chat-container::-webkit-scrollbar-track {
            background: #f1f1f1;
        }
        
        .chat-container::-webkit-scrollbar-thumb {
            background: #667eea;
            border-radius: 4px;
        }
        
        .chat-container::-webkit-scrollbar-thumb:hover {
            background: #764ba2;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎭 阿瓦隆游戏</h1>
        </div>
        
        <!-- Welcome Panel (shown before game starts) -->
        <div class="welcome-panel" id="welcomePanel">
            <h2>欢迎来到阿瓦隆游戏！</h2>
            <p>请选择你的参与方式，然后点击开始按钮</p>
            
            <div class="mode-selection">
                <div class="mode-card" onclick="selectMode('player')" id="playerModeCard">
                    <h3>🎮 作为玩家加入</h3>
                    <p>与 AI NPC 一起游戏，体验推理和欺骗的乐趣</p>
                </div>
                
                <div class="mode-card" onclick="selectMode('spectator')" id="spectatorModeCard">
                    <h3>👁️ 作为旁观者</h3>
                    <p>观看 AI NPC 之间的精彩对战</p>
                </div>
            </div>
            
            <div class="start-button-area">
                <button class="btn btn-primary btn-large" onclick="startGame()" id="startButton" disabled>
                    🚀 开始游戏
                </button>
            </div>
        </div>
        
        <!-- Game Interface (hidden until game starts) -->
        <div id="gameInterface" class="hidden" style="display: none;">
            <div class="identity-panel">
                <div class="identity-info">
                    <span class="identity-badge" id="playerName">玩家：H</span>
                    <span class="identity-badge" id="playerRole">角色：加载中...</span>
                    <span class="team-badge team-good" id="teamBadge">阵营：好人</span>
                </div>
                <div id="connectionStatus">🔴 未连接</div>
            </div>
            
            <div class="chat-container" id="chatContainer">
                <!-- Messages will be added here -->
            </div>
            
            <div class="input-area">
                <textarea id="messageInput" placeholder="请输入你的发言..." rows="3"></textarea>
                <div class="button-group">
                    <button class="btn btn-secondary" onclick="clearInput()">清空</button>
                    <button class="btn btn-primary" onclick="sendMessage()">发送</button>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        let ws = null;
        let selectedMode = null;
        
        // Select game mode
        function selectMode(mode) {
            selectedMode = mode;
            
            // Update UI
            document.getElementById('playerModeCard').classList.remove('selected');
            document.getElementById('spectatorModeCard').classList.remove('selected');
            
            if (mode === 'player') {
                document.getElementById('playerModeCard').classList.add('selected');
            } else {
                document.getElementById('spectatorModeCard').classList.add('selected');
            }
            
            // Enable start button
            document.getElementById('startButton').disabled = false;
        }
        
        // Start the game
        async function startGame() {
            if (!selectedMode) {
                alert('请先选择游戏模式！');
                return;
            }
            
            try {
                const response = await fetch('/api/start_game', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ mode: selectedMode })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    // Hide welcome panel, show game interface
                    document.getElementById('welcomePanel').style.display = 'none';
                    document.getElementById('gameInterface').style.display = 'block';
                    
                    // Add system message
                    addSystemMessage(`✅ 游戏已开始！模式：${selectedMode === 'player' ? '玩家' : '旁观者'}`);
                    
                    // Notify server via WebSocket
                    if (ws && ws.readyState === WebSocket.OPEN) {
                        ws.send(JSON.stringify({
                            type: 'game_started',
                            mode: selectedMode
                        }));
                    }
                } else {
                    alert('启动失败：' + result.error);
                }
            } catch (error) {
                console.error('Error starting game:', error);
                alert('启动失败：' + error.message);
            }
        }
        
        // Connect to WebSocket server
        function connectWebSocket() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/ws`;
            
            ws = new WebSocket(wsUrl);
            
            ws.onopen = function() {
                document.getElementById('connectionStatus').innerHTML = '🟢 已连接';
                addSystemMessage('✅ 已连接到游戏服务器');
            };
            
            ws.onclose = function() {
                document.getElementById('connectionStatus').innerHTML = '🔴 未连接';
                addSystemMessage('❌ 与服务器断开连接');
                setTimeout(connectWebSocket, 3000); // Auto reconnect
            };
            
            ws.onerror = function(error) {
                console.error('WebSocket error:', error);
                addSystemMessage('⚠️ 连接错误');
            };
            
            ws.onmessage = function(event) {
                const message = JSON.parse(event.data);
                handleMessage(message);
            };
        }
        
        // Handle incoming messages
        function handleMessage(message) {
            const chatContainer = document.getElementById('chatContainer');
            const messageDiv = document.createElement('div');
            
            switch(message.type) {
                case 'game_start':
                    messageDiv.className = 'message moderator';
                    messageDiv.textContent = '🎮 游戏开始！';
                    break;
                    
                case 'role_reveal_private':
                    // Private role information - only show to human player
                    messageDiv.className = 'message private';
                    messageDiv.innerHTML = `<strong>📜 你的身份：</strong>${message.content}`;
                    updateIdentity(message.role, message.team);
                    break;
                    
                case 'role_reveal_public':
                    messageDiv.className = 'message moderator';
                    messageDiv.textContent = message.content;
                    break;
                    
                case 'discussion':
                    messageDiv.className = 'message npc';
                    messageDiv.innerHTML = `
                        <div class="speaker">${message.speaker}</div>
                        <div class="content">${message.content}</div>
                    `;
                    break;
                    
                case 'vote_result':
                    messageDiv.className = 'message moderator';
                    messageDiv.textContent = `📊 投票结果：${message.content}`;
                    break;
                    
                case 'quest_result':
                    messageDiv.className = 'message moderator';
                    messageDiv.textContent = `⚔️ 任务结果：${message.content}`;
                    break;
                    
                case 'game_end':
                    messageDiv.className = 'message moderator';
                    messageDiv.innerHTML = `<strong>🏆 游戏结束：</strong>${message.content}`;
                    break;
                    
                case 'input_request':
                    // Highlight that it's player's turn to speak
                    messageDiv.className = 'message moderator';
                    messageDiv.innerHTML = `<strong>⏰ 轮到你发言：</strong>${message.prompt || '请发表你的看法：'}`;
                    // Focus the input field
                    const input = document.getElementById('messageInput');
                    if (input) {
                        input.focus();
                        input.placeholder = '请在此输入你的发言...';
                        input.style.borderColor = '#667eea';
                        input.style.boxShadow = '0 0 10px rgba(102, 126, 234, 0.3)';
                    }
                    break;
                    
                default:
                    messageDiv.className = 'message moderator';
                    messageDiv.textContent = message.content;
            }
            
            chatContainer.appendChild(messageDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
        
        // Update identity panel
        function updateIdentity(role, team) {
            document.getElementById('playerRole').textContent = `角色：${role}`;
            const teamBadge = document.getElementById('teamBadge');
            teamBadge.textContent = `阵营：${team === 'good' ? '好人 🔵' : '邪恶 🔴'}`;
            teamBadge.className = `team-badge ${team === 'good' ? 'team-good' : 'team-evil'}`;
        }
        
        // Send message to server
        function sendMessage() {
            const input = document.getElementById('messageInput');
            const content = input.value.trim();
            
            if (content && ws && ws.readyState === WebSocket.OPEN) {
                ws.send(JSON.stringify({
                    type: 'player_message',
                    content: content
                }));
                input.value = '';
                // Reset input style
                input.style.borderColor = '#ddd';
                input.style.boxShadow = 'none';
                input.placeholder = '请输入你的发言...';
            }
        }
        
        // Clear input
        function clearInput() {
            document.getElementById('messageInput').value = '';
        }
        
        // Add system message
        function addSystemMessage(text) {
            const chatContainer = document.getElementById('chatContainer');
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message moderator';
            messageDiv.textContent = text;
            chatContainer.appendChild(messageDiv);
        }
        
        // Enter key to send
        document.getElementById('messageInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
        
        // Initialize connection
        connectWebSocket();
    </script>
</body>
</html>'''
