import requests
import threading
from PySide2 import QtWidgets, QtCore
from PySide2.QtCore import QFile, QIODevice
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, \
    QLineEdit, QApplication, QHBoxLayout

from ..consts.asset_paths import Path
from ..display_drawer import DisplayDrawer
from ..game_instance import GameInstance
from ..main import OTS
from ..online_handler import OnlineHandler


class login_window(QWidget):
    def __init__(self):
        super().__init__()
        self.initialize()
        self.oq = online_queue()
        self.player_id = ""
    def initialize(self):
        self.login_url = Path.login_url # 차후변경
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

    def login_btn_clicked(self):
        self.res = requests.post(self.login_url, data={'email': self.input_email.text(), 'password' : self.input_pwd.text()})
        self.player_id = self.res.json()['msg']
        if(self.res.json()['msg'] != "failed"):
            print("login")
            print(f"{self.res.json()['msg']}")
            self.send_name_data(self.res.json()['msg'])
            self.oq.show()
        else:
            print("fail")

    def send_name_data(self,data):
        self.oq.name_label.setText("my name : " + data)
        self.oq.player_id = self.player_id
class online_queue(QWidget):
    def __init__(self):
        super().__init__()
        self.player_id = ""
        self.initialize()

    def initialize(self):
        self.layout = QVBoxLayout()
        self.hlayout = QHBoxLayout()
        self.v1layout = QVBoxLayout()
        self.v2layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.setLayout(self.hlayout)
        self.setLayout(self.v1layout)
        self.setLayout(self.v2layout)
        self.setGeometry(0, 0, 468, 485)
        self.setWindowTitle('OTS')

        self.name_label = QLabel("login success")
        self.layout.addWidget(self.name_label)

        self.layout.addLayout(self.hlayout)
        self.hlayout.addLayout(self.v1layout)
        self.hlayout.addLayout(self.v2layout)
        self.invite_label = QLabel("Invite List")
        self.v1layout.addWidget(self.invite_label)

        self.invite_list = QtWidgets.QListView()
        self.invite_list.setGeometry(QtCore.QRect(250, 70, 201, 301))
        self.invite_list.setObjectName("invite_list")
        self.v1layout.addWidget(self.invite_list)

        self.lobby_label = QLabel("Lobby List")
        self.v2layout.addWidget(self.lobby_label)

        self.lobby_list = QtWidgets.QListWidget()
        self.lobby_list.setGeometry(QtCore.QRect(20, 70, 201, 301))
        self.lobby_list.setObjectName("lobby_list")
        self.v2layout.addWidget(self.lobby_list)

        self.game_start_btn = QtWidgets.QPushButton("GAME START")
        self.game_start_btn.setGeometry(QtCore.QRect(120, 280, 80, 26))
        self.game_start_btn.setObjectName("game_start_btn")
        self.game_start_btn.clicked.connect(self.game_start_btn_clicked)
        self.layout.addWidget(self.game_start_btn)

    def game_start_btn_clicked(self):
        t = threading.Thread(target=self.run_online)
        t.start()

    def init_objs(self, is_mp: bool):
        if not is_mp:
            gi = GameInstance()
            oi = None
        else:
            gi = GameInstance(is_multiplayer=True)
            oi = GameInstance()
        dd = DisplayDrawer(game_instance=gi, multiplayer_instance=oi)
        from client.src.event_handler import EventHandler
        eh = EventHandler(game_instance=gi, display_drawer=dd)
        ots = OTS(game_instance=gi, display_drawer=dd, event_handler=eh)
        if is_mp:
            oh = OnlineHandler(user_id=self.player_id, game_instance=gi, opponent_instance=oi)
        else:
            oh = None
        return ots, oh

    def run_online(self):
        ots, oh = self.init_objs(is_mp=True)
        oh.ws_thread.start()
        ots.main_loop()
