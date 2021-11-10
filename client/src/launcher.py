from PySide6.QtGui import *
from PySide6.QtWidgets import *
from .variables.ui_variables import UI_VARIABLES as uv
from .main import OTS
import webbrowser
import sys


class Launcher(QWidget):
    def __init__(self):
        self.app = QApplication(sys.argv)
        QWidget.__init__(self)
        self.game_mode = None
        self.player_id = 'offline'
        self.initialize()

    def initialize(self):

        self.setGeometry(300, 300, 400, 300)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.setWindowTitle('OTS')
        self.setWindowIcon(QIcon(QPixmap(uv.tetris_image)))

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

    def single_btn_clicked(self):
        self.game_mode = 'single'
        self.run_game()
        sys.exit(self.app.exec_())

    def dual_btn_clicked(self):
        self.game_mode = 'dual'
        self.run_game()
        sys.exit(self.app.exec_())

    def online_btn_clicked(self):
        self.game_mode = 'online'
        self.run_game()
        sys.exit(self.app.exec_())

    def signup_btn_clicked(self):
        webbrowser.open("https://ots.prvt.dev/")

    def help_btn_clicked(self):
        webbrowser.open("https://github.com/CSID-DGU/2021-2-OSSProj-OTS-7/blob/main/client/assets/img/help.png?raw=true")

    def run_launcher(self):
        self.app.exec_()

    def run_game(self):
        ots = OTS(game_mode=self.game_mode, player_id=self.player_id)
        ots.main_loop()
