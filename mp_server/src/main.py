from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import List
from .multiplayer_manager import MultiplayerManager
from .player_request_handler import PlayerConnection
from collections import deque
import threading
import json


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.active_connection_dict = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket, player_id: str):
        self.active_connections.remove(websocket)
        self.active_connection_dict.pop(player_id)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


app = FastAPI()
con_manager = ConnectionManager()
mp_manager = MultiplayerManager()
message_queue = deque([])
players_on_this_worker = {}


@app.on_event('startup')
async def on_startup():
    ml = threading.Thread(target=message_listen, daemon=True)
    ml.start()  # 메시지 리스너 스레드 시작
    mp = threading.Thread(target=message_parse, daemon=True)
    mp.start()  # 메시지 파서 스레드 시작


# redis 에서 받은 메시지를 큐에 넣음.
def message_listen():
    for msg in mp_manager.redis_pup_sub.listen():
        if msg.get('type') == 'message':
            message_queue.append(msg)


# 메시지 큐 제너레이터
def message_queue_gen():
    while True:
        if message_queue:
            yield message_queue.popleft()


# 큐에서 메시지를 꺼내서 작업 진행
def message_parse():
    for msg in message_queue_gen():
        print(msg)
        data = msg.get('data')
        todo = msg.get('t')  # to do
        receiver = msg.get('r')  # receiver
        if data is not None and receiver in con_manager.active_connection_dict.keys():
            player_connection: PlayerConnection = con_manager.active_connection_dict[receiver].ws
            if todo == 'gd':  # game data send
                pass
            elif todo == 'go':  # game over signal send
                pass
            elif todo == 'gs':  # game start signal send
                pass
            elif todo == 'su':  # solicitor updated send
                pass
            elif todo == 'sa':  # solicit accepted send
                pass
            elif todo == 'sr':  # solicit rejected send
                pass
            elif todo == '':
                pass


@app.websocket("/ws")
async def websocket_connection(websocket: WebSocket):
    await con_manager.connect(websocket)
    player_id = await websocket.receive_text()  # 처음 받는 텍스트를 플레이어 아이디로 처리, 추후 jwt 인증 로직 넣을 예정
    player_connection = PlayerConnection(player_id=player_id, mp_manager=mp_manager, websocket=websocket)
    con_manager.active_connection_dict[player_id] = player_connection  # connection manager 객체의 active connection dict 에 {player_id : player_connection} 추가

    await receive_data(websocket, player_connection)  # 무한루프로 클라이언트에서 보내는 데이터를 받아옴.


async def receive_data(websocket, player_connection):
    try:
        while True:
            data = await websocket.receive_json()
            player_connection.parse_request(data=data)

    except WebSocketDisconnect:
        player_connection.ws.close()
        con_manager.active_connection_dict.pop(player_connection.player_id)
        # 연결 끊겼을 때 필요한 조치
