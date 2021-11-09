from .main import OTS
import webbrowser
from PyQt5.QtWidgets import *
import sys

class Launcher(QWidget):
    def __init__(self):
        self.app = QApplication(sys.argv)
        super().__init__()
        self.initialize()

        self.game_mode = None
        self.player_id = 'offline'

    def initialize(self):
        self.setGeometry(300, 300, 400, 300)
        layout = QVBoxLayout()
        self.setLayout(layout)

        single_btn = QPushButton("Single play")
        single_btn.clicked.connect(self.single_btn_clicked)
        layout.addWidget(single_btn)

        dual_btn = QPushButton("Dual play")
        dual_btn.clicked.connect(self.dual_btn_clicked)
        layout.addWidget(dual_btn)

        online_btn = QPushButton("Online play")
        single_btn.clicked.connect(self.online_btn_clicked)
        layout.addWidget(online_btn)

        signup_btn = QPushButton("Sign up")
        signup_btn.clicked.connect(self.signup_btn_clicked)
        layout.addWidget(signup_btn)

        help_btn = QPushButton("Help")
        help_btn.clicked.connect(self.help_btn_clicked)
        layout.addWidget(help_btn)

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
        screen = Launcher()
        screen.show()
        sys.exit(self.app.exec_())

    def run_game(self):
        ots = OTS(game_mode=self.game_mode, player_id=self.player_id)
        ots.main_loop()
