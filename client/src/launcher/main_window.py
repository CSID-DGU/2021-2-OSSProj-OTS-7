import threading
from PySide2.QtGui import QIcon, QPixmap
from PySide2.QtWidgets import QWidget, QVBoxLayout, QPushButton, QApplication, \
    QLabel
from ..consts.asset_paths import Path as Path
from ..main import OTS
from ..game_instance import GameInstance
from ..display_drawer import DisplayDrawer
from ..event_handler import EventHandler
from ..online_handler import OnlineHandler
from .login_window import login_window
import webbrowser
import sys


class Launcher(QWidget):
    def __init__(self):
        self.app = QApplication(sys.argv)
        QWidget.__init__(self)
        self.game_mode = None
        self.player_id = 'offline'
        self.initialize()
        self.lw = login_window()

    def initialize(self):

        self.setGeometry(300, 300, 400, 300)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.setWindowTitle('OTS')
        self.setWindowIcon(QIcon(QPixmap(Path.tetris_image)))

        self.single_btn = QPushButton("Single play")
        self.single_btn.clicked.connect(self.single_btn_clicked)
        self.layout.addWidget(self.single_btn)

        self.dual_btn = QPushButton("Dual play")
        self.dual_btn.clicked.connect(self.dual_btn_clicked)
        self.layout.addWidget(self.dual_btn)

        self.online_btn = QPushButton("Online play")
        self.online_btn.clicked.connect(self.online_btn_clicked)
        self.layout.addWidget(self.online_btn)

        self.signup_btn = QPushButton("Sign up")
        self.signup_btn.clicked.connect(self.signup_btn_clicked)
        self.layout.addWidget(self.signup_btn)

        self.help_btn = QPushButton("Help")
        self.help_btn.clicked.connect(self.help_btn_clicked)
        self.layout.addWidget(self.help_btn)
        self.show()

    def set_launch_btns_disabled(self):
        self.single_btn.setDisabled(1)
        self.dual_btn.setDisabled(1)
        self.online_btn.setDisabled(1)

    def single_btn_clicked(self):
        self.set_launch_btns_disabled()
        t = threading.Thread(target=self.run_game)
        t.start()

    def dual_btn_clicked(self):
        self.set_launch_btns_disabled()
        print('추가예정')
        sys.exit(self.app.exec_())

    def online_btn_clicked(self):

        self.lw.show()
        # self.set_launch_btns_disabled()
        # t = threading.Thread(target=self.run_online)
        # t.start()

    def signup_btn_clicked(self):
        webbrowser.open("https://ots.prvt.dev/")

    def help_btn_clicked(self):
        webbrowser.open("https://github.com/CSID-DGU/2021-2-OSSProj-OTS-7/blob/main/client/assets/img/help.png?raw=true")

    def run_launcher(self):
        self.app.exec_()

    # 이하 ots 세팅, 실행 코드
    def init_objs(self, is_mp: bool):
        if not is_mp:
            gi = GameInstance()
            oi = None
        else:
            gi = GameInstance(is_multiplayer=True)
            oi = GameInstance()
        dd = DisplayDrawer(game_instance=gi, multiplayer_instance=oi)
        eh = EventHandler(game_instance=gi, display_drawer=dd)
        ots = OTS(game_instance=gi, display_drawer=dd, event_handler=eh)
        if is_mp:
            oh = OnlineHandler(user_id=self.player_id, game_instance=gi, opponent_instance=oi)
        else:
            oh = None
        return ots, oh

    def run_game(self):
        ots, oh = self.init_objs(is_mp=False)
        ots.main_loop()

    def run_online(self):
        ots, oh = self.init_objs(is_mp=True)
        oh.ws_thread.start()
        ots.main_loop()
