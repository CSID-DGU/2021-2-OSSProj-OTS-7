from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from .multiplayer_manager import MultiplayerManager
from .player_connection import PlayerConnection
from collections import deque
import threading
import asyncio
import json


class ConnectionManager:
    def __init__(self):
        self.active_connection_dict = {}

    def disconnect(self, player_id: str):
        self.active_connection_dict[player_id].ws.close()  # 소켓 닫음
        self.active_connection_dict.pop(player_id)  # 딕셔너리 pop


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


# redis 에서 받은 메시지를 큐에 넣음. 스레드로 사용할것
def message_listen():
    for msg in mp_manager.redis_pup_sub.listen():
        if msg.get('type') == 'message':
            message_queue.append(msg)


# 메시지 큐 제너레이터
def message_queue_gen():
    while True:
        if message_queue:
            yield message_queue.popleft()


# 큐에서 메시지를 꺼내서 작업 진행. 스레드로 사용할것
def message_process():
    loop = asyncio.new_event_loop()
    for msg in message_queue_gen():
        loop.run_until_complete(message_execute(msg))


msg_code_map = {
    b'go': 'opponent_game_over',
    b'ms': 'match_set',
    b'mc': 'match_complete',
    b'gs': 'game_start',
    b'sa': 'solicit_accepted',
    b'sr': 'solicit_rejected',
    b'lo': 'loser',
    b'wi': 'winner'
}


# 메시지 명령 실행
async def message_execute(msg):
    msg_type = msg.get('type')
    channel = msg.get('channel')  # user_id 가 채널
    try:
        pc: PlayerConnection = con_manager.active_connection_dict[channel]  # user_id 에 매핑된 플레이어 커넥션 객체
    except KeyError:
        print('player connection object does not exist')
        pc = None

    print(msg)
    print(msg.get('data'))

    if pc is not None and msg_type == 'message':
        msg_code = msg.get('data')  # 명령 코드

        if msg_code == b'gd':
            await pc.send_game_info()  # 현재 게임 상황 전송
        elif msg_code == b'ss':
            await pc.send_solicitors()  # 현재 solicitor 목록 전송
        else:
            val = msg_code_map.get(msg_code)
            if val is not None:
                # await pc.send_event(val)
                print(val)
            else:
                print('invalid code')


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
            await player_connection.parse_request(data=data)

    except WebSocketDisconnect:
        mp_manager.redis_pup_sub.unsubscribe(player_connection.player_id)
        con_manager.active_connection_dict.pop(player_connection.player_id)
        # 연결 끊겼을 때 필요한 조치
