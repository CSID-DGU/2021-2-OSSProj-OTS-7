import threading

import requests
from PySide2.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, \
    QLineEdit
from .online_lobby import OnlineLobby
from .online_data_temp import GuiEmit
from ..consts.asset_paths import Path
from ..display_drawer import DisplayDrawer
from ..event_handler import EventHandler
from ..game_instance import GameInstance
from ..main import OTS
from ..online_handler import OnlineHandler


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.login_url = Path.login_url  # 차후변경
        self.layout = QVBoxLayout()
        self.label = QLabel("please login")
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)
        self.setGeometry(150, 150, 200, 200)
        self.setWindowTitle('OTS')

        self.input_email = QLineEdit()
        self.input_email.setPlaceholderText('email 입력')
        self.layout.addWidget(self.input_email)
        self.input_pwd = QLineEdit()
        self.input_pwd.setPlaceholderText('비밀번호 입력')
        self.layout.addWidget(self.input_pwd)

        self.login_btn = QPushButton("Login")
        self.layout.addWidget(self.login_btn)
        self.login_btn.clicked.connect(self.login_btn_clicked)

        self.player_id = ""
        self.online_data = GuiEmit()
        self.oq = OnlineLobby(gui_emit=self.online_data)

    # 이하 ots 세팅, 실행 코드
    def init_objs(self, is_mp: bool):
        if not is_mp:
            gi = GameInstance()
            oi = None
            od = None
        else:
            gi = GameInstance(is_multiplayer=True)
            oi = GameInstance()
            od = self.online_data
        dd = DisplayDrawer(game_instance=gi, multiplayer_instance=oi)
        eh = EventHandler(game_instance=gi, display_drawer=dd)
        ots = OTS(game_instance=gi, display_drawer=dd, event_handler=eh)
        if is_mp:
            oh = OnlineHandler(user_id=self.player_id, game_instance=gi, opponent_instance=oi, online_data=od,
                               online_lobby=self.oq)
        else:
            oh = None
        return ots, oh

    # def run_game(self):
    #     ots, oh = self.init_objs(is_mp=False)
    #     ots.main_loop()

    def run_online(self):
        ots, oh = self.init_objs(is_mp=True)
        oh.ws_thread.start()
        oh.gui_emit_thread.start()
        oh.game_instance.status = 'mp_hello'

        t = threading.Thread(target=ots.main_loop, daemon=True)
        t.start()

    def login_btn_clicked(self):
        # res = requests.post(self.login_url,
        #                     data={'email': self.input_email.text(), 'password': self.input_pwd.text()})
        # self.player_id = res.json()['msg']
        # if res.json()['msg'] != "failed":
        #     print("login")
        #     print(f"{res.json()['msg']}")
        #     self.send_name_data(res.json()['msg'])
        #     self.run_online()
        #     self.setVisible(False)
        #     self.oq.show()
        #
        # else:
        #     print("fail")
        self.player_id = self.input_email.text()
        self.send_name_data(self.player_id)
        self.run_online()
        self.setVisible(False)
        self.oq.show()

    def send_name_data(self, data):
        self.oq.name_label.setText("my name : " + data)
        self.oq.player_id = self.player_id
