from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from .redis_manager import RedisManager
from .user_instance import UserInstance
from .message_executors import UserMsgExecutor, ServerMsgExecutor
from queue import Queue
import threading
import asyncio
import json


app = FastAPI()

rd_manager = RedisManager()  # redis 관련 메소드
ume = UserMsgExecutor(rd_manager)  # 유저 메시지 파싱, 실행
sme = ServerMsgExecutor(rd_manager)  # 서버 메시지 파싱, 실행

message_queue = Queue()
players_dict = {}  # players connected to this worker process


# 시작시 메시지 리슨, 메시지 프로세스 스레드 시작
@app.on_event('startup')
async def on_startup():
    ml = threading.Thread(target=server_message_listen, daemon=True)
    ml.start()  # 메시지 리스너 스레드 시작
    loop = asyncio.get_running_loop()  # server_message_process 에 넘겨줄 async event loop
    mp = threading.Thread(target=server_message_process, args=(loop,), daemon=True)  # 메시지 프로세스 스레드
    mp.start()  # 메시지 프로세스 스레드 시작


# redis 에서 받은 메시지를 큐에 넣음. 스레드로 사용할것
def server_message_listen():
    for msg in rd_manager.msg_pubsub.listen():
        if msg.get('type') == 'message':
            message_queue.put(msg)


# 큐에서 메시지를 꺼내서 작업 진행. 스레드로 사용할것
def server_message_process(loop):
    asyncio.set_event_loop(loop)  # 인자로 넘겨받은 이벤트 루프를 set
    while True:
        msg = message_queue.get()  # 블로킹 큐
        loop.create_task(server_message_exec(msg))  # 비동기 이벤트 루프에 task 추가


# 메시지 브로커에게 받은 메시지 명령 실행, UserInstance 를 특정해서 넘겨줌.
async def server_message_exec(msg):
    msg_type = msg.get('type')
    channel: str = msg.get('channel')  # user_id 가 채널
    if channel != '$waiting':
        try:
            user: UserInstance = players_dict[channel]  # user_id 에 매핑된 플레이어 커넥션 객체
            if msg_type == 'message':
                await sme.server_msg_exec(user, msg)
        except KeyError:
            print('player connection object does not exist')
    elif channel == '$waiting':
        for user in players_dict.values():
            await sme.send_waiters(user)


@app.websocket("/ws")
async def websocket_connection(websocket: WebSocket):
    user: UserInstance = await user_instance_create(websocket)  # 연결시 플레이어 커넥션 객체를 생성하고 반환함.
    await user_message_receive(websocket, user)  # 클라이언트에서 보내는 데이터를 연결이 끝나기 전까지 받아옴.


async def user_instance_create(websocket: WebSocket) -> UserInstance:
    await websocket.accept()  # 연결 수락
    player_id = str(await websocket.receive_text())  # 처음 받는 텍스트를 플레이어 아이디로 처리, 추후 jwt 인증 로직 넣을 예정
    rd_manager.msg_pubsub.subscribe(player_id)  # redis player_id 채널 구독
    user_instance = UserInstance(player_id=player_id, websocket=websocket)
    players_dict[player_id] = user_instance
    rd_manager.msg_broker.publish('$waiting', '')
    return user_instance


async def user_message_receive(websocket, user: UserInstance):
    try:
        while True:
            try:
                msg: dict = await websocket.receive_json()  # 받은 json 형식 데이터, 딕셔너리로 자동 변환됨.
                await ume.user_msg_exec(user, msg)  # 메시지 처리
            except json.decoder.JSONDecodeError:
                print('not json type data')

    except WebSocketDisconnect:  # 연결 종료시
        await on_connection_lost(user)
        # 연결 끊겼을 때 필요한 조치
        # Todo 상대 클라이언트에 연결 끊김 알림


async def on_connection_lost(user: UserInstance):
    print(f'player {user.player_id} disconnected')
    rd_manager.msg_pubsub.unsubscribe(user.player_id)
    players_dict.pop(user.player_id)
    await rd_manager.user_connection_closed(user.player_id)
    if user.approached_to is not None:
        await rd_manager.approacher_del(user.player_id, user.approached_to)
