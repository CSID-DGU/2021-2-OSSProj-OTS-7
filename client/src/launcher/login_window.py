from PySide2.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit
from .. import run_game
from .login_func import request_login


class LoginWindowView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        # self.label = QLabel("Please Login")
        # self.layout.addWidget(self.label)
        self.setLayout(self.layout)
        # self.setGeometry(150, 150, 200, 200)
        self.setWindowTitle('OTS')

        self.input_name = QLineEdit()
        self.input_name.setPlaceholderText('ID')
        self.layout.addWidget(self.input_name)
        self.input_pwd = QLineEdit()
        self.input_pwd.setPlaceholderText('Password')
        self.input_pwd.setEchoMode(QLineEdit.Password)
        self.layout.addWidget(self.input_pwd)

        self.login_btn = QPushButton("Login")
        self.layout.addWidget(self.login_btn)
        self.login_btn.clicked.connect(self.on_login_btn_clicked)

    def on_login_btn_clicked(self):  # override
        pass


class LoginWindow(LoginWindowView):
    def __init__(self, is_test_mode=False):
        super().__init__()
        self.player_id = None
        self.jwt = None
        self.test_mode = is_test_mode

    def run_online(self):
        run_game.run_online(self.player_id, self.jwt)

    def on_login_btn_clicked(self):
        if self.test_mode:
            self.player_id = self.input_name.text()
            self.run_online()
            self.close()
        else:
            if self.req_auth() is True:
                self.run_online()
                self.close()

    def req_auth(self):
        res: dict = request_login(self.input_name.text(), self.input_pwd.text())
        print(res)
        if res['msg'] != "failed":
            self.player_id = res['msg'][0]
            self.jwt = res['msg'][1]
            print(res)
            return True
        else:
            print("fail")
            return False
