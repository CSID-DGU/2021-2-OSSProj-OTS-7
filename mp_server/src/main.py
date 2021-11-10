from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from .redis_manager import RedisManager
from .user_instance import UserInstance
from collections import deque
import threading
import asyncio
import json


app = FastAPI()
mp_manager = RedisManager()
message_queue = deque([])  # deque 의 popleft 와 append 는 thread safe
players_dict = {}  # players connected to this worker process


# 시작시 메시지 리슨, 메시지 프로세스 스레드 시작
@app.on_event('startup')
async def on_startup():
    ml = threading.Thread(target=message_listen, daemon=True)
    ml.start()  # 메시지 리스너 스레드 시작
    mp = threading.Thread(target=message_process, daemon=True)
    mp.start()  # 메시지 파서 스레드 시작


# redis 에서 받은 메시지를 큐에 넣음. 스레드로 사용할것
def message_listen():
    for msg in mp_manager.msg_pubsub.listen():
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
        loop.run_until_complete(broker_msg_exec(msg))


# 메시지 브로커에게 받은 메시지 명령 실행
async def broker_msg_exec(msg):
    msg_type = msg.get('type')
    channel: bytes = msg.get('channel')  # user_id 가 채널

    try:
        pc: UserInstance = players_dict[channel.decode()]  # user_id 에 매핑된 플레이어 커넥션 객체
    except KeyError:
        print('player connection object does not exist')
        pc = None

    if pc is not None and msg_type == 'message':
        await pc.server_msg_exec(msg=msg)


@app.websocket("/ws")
async def websocket_connection(websocket: WebSocket):
    player_connection: UserInstance = await connect(websocket)  # 연결시 플레이어 커넥션 객체를 생성하고 반환함.
    await receive_data(websocket, player_connection)  # 클라이언트에서 보내는 데이터를 연결이 끝나기 전까지 받아옴.


async def connect(websocket: WebSocket):
    await websocket.accept()  # 연결 수락
    player_id = str(await websocket.receive_text())  # 처음 받는 텍스트를 플레이어 아이디로 처리, 추후 jwt 인증 로직 넣을 예정
    mp_manager.msg_pubsub.subscribe(player_id)  # redis player_id 채널 구독
    player_con = UserInstance(player_id=player_id, websocket=websocket)
    players_dict[player_id] = player_con
    return player_con


async def receive_data(websocket, player_connection: UserInstance):
    try:
        while True:
            try:
                data: dict = await websocket.receive_json()  # 받은 json 형식 데이터, 딕셔너리로 자동 변환됨.
                await player_connection.user_msg_exec(msg=data)
            except json.decoder.JSONDecodeError:
                print('not json type data')

    except WebSocketDisconnect:  # 연결 종료시
        print(f'player {player_connection.player_id} disconnected')
        mp_manager.msg_pubsub.unsubscribe(player_connection.player_id)
        players_dict.pop(player_connection.player_id)
        # 연결 끊겼을 때 필요한 조치
        # Todo 상대 클라이언트에 연결 끊김 알림

