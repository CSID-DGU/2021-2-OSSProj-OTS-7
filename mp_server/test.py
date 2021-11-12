import threading
import json
import time
from client.src.online import OnlineManager

tot = OnlineManager(user_id='testuser0', game_instance=None, multiplayer_instance=None)

wct = threading.Thread(target=tot.run_forever, daemon=True)

wct.start()

time.sleep(0.1)
code_list = ['atw', 'qw']
data_list = [None, None]

def send_json(to_send):
    tot.ws.send(json.dumps(to_send))


for t, d in zip(code_list, data_list):
    send_dict = {
        't': t,
        'd': d
    }
    send_json(to_send=send_dict)
