from fastapi import FastAPI, WebSocket, WebSocketDisconnect, BackgroundTasks
from typing import List
from .multiplayer_manager import MultiplayerManager
from .player_connection import PlayerConnection
from collections import deque
import threading, asyncio
import json


class ConnectionManager:
    def __init__(self):
        self.active_connection_dict = {}

    def disconnect(self, player_id: str):
        self.active_connection_dict[player_id].ws.close()
        self.active_connection_dict.pop(player_id)


app = FastAPI()
con_manager = ConnectionManager()
mp_manager = MultiplayerManager()
message_queue = deque([])
players_on_this_worker = {}


@app.on_event('startup')
async def on_startup():
    ml = threading.Thread(target=message_listen, daemon=True)
    ml.start()  # 메시지 리스너 스레드 시작
    mp = threading.Thread(target=message_process, daemon=True)
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
async def say_hi(asd):
    print('hi'+asd)


def message_process():
    loop = asyncio.new_event_loop()
    for msg in message_queue_gen():
        loop.run_until_complete(message_execute(msg))


async def message_execute(msg):
    todo = None
    msg_type = msg.get('type')
    data = json.loads(msg.get('data'))

    channel = msg.get('channel')
    print(msg)
    if msg_type == 'message':
        try:
            todo = data.get('t')
        except AttributeError:
            pass

    receiver = con_manager.active_connection_dict.get(channel)
    if receiver is not None:
        pc: PlayerConnection = con_manager.active_connection_dict[receiver]
        if todo == 'gd':  # game data send
            await pc.send_game_info()
        elif todo == 'go':  # game over(opponent) signal send
            await pc.send_event('opponent_game_over')
        elif todo == 'ms':  # match set signal
            await pc.send_event('match_set')
        elif todo == 'mc':  # match complete signal
            await pc.send_event('match_complete')
        elif todo == 'gs':  # game start signal send
            await pc.send_event('game_start')
        elif todo == 'ss':  # solicitor updated send
            await pc.send_solicitors()
        elif todo == 'sa':  # solicit accepted send
            await pc.send_event('solicit_accepted')
        elif todo == 'sr':  # solicit rejected send
            await pc.send_event('solicit_rejected')
        elif todo == 'lo':  # loser signal send
            await pc.send_event('loser')
        elif todo == 'wi':  # winner signal send
            await pc.send_event('winner')


@app.websocket("/ws")
async def websocket_connection(websocket: WebSocket):
    await websocket.accept()
    player_id = str(await websocket.receive_text())  # 처음 받는 텍스트를 플레이어 아이디로 처리, 추후 jwt 인증 로직 넣을 예정
    mp_manager.redis_pup_sub.subscribe(player_id)  # redis player_id 채널 구독

    player_connection = PlayerConnection(player_id=player_id, mp_manager=mp_manager, websocket=websocket)
    con_manager.active_connection_dict[player_id] = player_connection  # connection manager 객체의 active connection dict 에 {player_id : player_connection} 추가

    await receive_data(websocket, player_connection)  # 무한루프로 클라이언트에서 보내는 데이터를 받아옴.


async def receive_data(websocket, player_connection):
    try:
        while True:
            data = await websocket.receive_json()
            player_connection.parse_request(data=data)

    except WebSocketDisconnect:
        mp_manager.redis_pup_sub.unsubscribe(player_connection.player_id)
        con_manager.active_connection_dict.pop(player_connection.player_id)
        # 연결 끊겼을 때 필요한 조치
