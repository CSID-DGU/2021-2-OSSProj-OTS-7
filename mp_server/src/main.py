import asyncio

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import List
from rejson import Client, Path
from mp_server.src import multiplayer_manager, player_request_handler
import pickle


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.active_connection_dict = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


app = FastAPI()
con_manager = ConnectionManager()
mp_manager = multiplayer_manager.MultiplayerManager()
active_websockets = Client(host='192.168.50.125', port=6379, db=3)


async def pickle_connection(websocket):
    return pickle.dumps(websocket)


async def set_connection_to_redis(player_id, websocket):
    pickled_connection = await pickle_connection(websocket)
    active_websockets.set(player_id, pickled_connection)


@app.websocket("/ws")
async def websocket_connection(websocket: WebSocket):
    await con_manager.connect(websocket)
    player_id = await websocket.receive_text()
    player_instance = player_request_handler.PlayerConnection(player_id, mp_manager)

    await recieve_data(websocket, player_instance)


async def recieve_data(websocket, player_instance):
    try:
        while True:
            pass
            data = await websocket.receive_json()
            await mp_manager.update_game_info(data, 'a1234', 'a1234')

            to_send = await mp_manager.get_game_info('a1234')
            # to_send = player_instance.parse_request(data=data)

            if to_send is not None:
                await websocket.send_json(to_send)

    except WebSocketDisconnect:
        player_id = con_manager.active_connection_dict.get(websocket)
        await mp_manager.clear_match_id(player_id)
        await mp_manager.remove_from_waiting_list(player_id)
        pass
        con_manager.disconnect(websocket)
