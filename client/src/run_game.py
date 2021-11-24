import threading
from .game_instance import GameInstance
from .online_handler import OnlineHandler
from .display_drawer import DisplayDrawer
from .event_handler import EventHandler
from .main import OTS
from .launcher.gui_com import GuiCom
from .launcher.online_lobby import OnlineLobby


def init_objs(player_id: (str, None), is_mp: bool) -> tuple:
    if is_mp:
        game_instance = GameInstance(is_multiplayer=True)
        opponent_game_instance = GameInstance()
    else:
        game_instance = GameInstance()
        opponent_game_instance = None

    display_drawer = DisplayDrawer(game_instance=game_instance, multiplayer_instance=opponent_game_instance)
    event_handler = EventHandler(game_instance=game_instance, display_drawer=display_drawer)
    ots_main = OTS(game_instance=game_instance, display_drawer=display_drawer, event_handler=event_handler)

    if is_mp:
        gui_com = GuiCom()
        online_lobby = OnlineLobby(gui_com)
        online_handler = OnlineHandler(user_id=player_id,
                                       game_instance=game_instance,
                                       opponent_instance=opponent_game_instance,
                                       online_data=gui_com,
                                       online_lobby=online_lobby)
    else:
        online_handler = None
        online_lobby = None
    return ots_main, online_handler, online_lobby


def run_single() -> None:
    ots, oh, ol = init_objs(None, False)
    ots.main_loop()


def run_online(player_id) -> None:
    ots, oh, ol = init_objs(player_id=player_id, is_mp=True)

    ol.show()
    oh.ws_thread.start()
    oh.gui_emit_thread.start()
    oh.game_instance.status = 'mp_hello'

    t = threading.Thread(target=ots.main_loop, daemon=True)
    t.start()
