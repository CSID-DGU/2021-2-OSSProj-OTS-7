from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import List
from multiplayer_manager import MultiplayerManager
from player_request_handler import PlayerConnection
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
async def on_startup():  # 프로세스 생성시 redis 메시지 채널 구독, 이후 while 문으로 메시지 전달 받아서 명령 실행
    ml = threading.Thread(target=message_listen, daemon=True)
    ml.start()  # 메시지 리스너 스레드 시작, fastapi 에서 스레드 동작 되는지 확인 필요
    while True:
        if message_queue:
            message = message_queue.popleft()
            await message_parse(message=message)


# 큐에서 메시지를 꺼내서 작업 진행
async def message_parse(message):
    data: dict = json.loads(message)
    todo = data.get('t')  # to do
    receiver = data.get('r')  # receiver
    if receiver in con_manager.active_connection_dict.keys():
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


# redis 에서 받은 메시지를 큐에 넣음.
def message_listen():
    while True:
        message = mp_manager.redis_pup_sub.get_message()
        message_queue.append(message)


@app.websocket("/ws")
async def websocket_connection(websocket: WebSocket):
    await con_manager.connect(websocket)
    player_id = await websocket.receive_text()
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
