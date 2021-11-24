from PySide2.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit
from .. import run_game
from .login_func import request_login


class LoginWindowView(QWidget):
    def __init__(self):
        super().__init__()
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
        self.login_btn.clicked.connect(self.on_login_btn_clicked)

    def on_login_btn_clicked(self):  # override
        pass


class LoginWindow(LoginWindowView):
    def __init__(self):
        super().__init__()
        self.player_id = None

    def run_online(self):
        run_game.run_online(self.player_id)

    def on_login_btn_clicked(self):
        print('asd')
        self.player_id = self.input_email.text()
        self.run_online()
        self.close()
        # res = request_login(self.input_email.text(), self.input_pwd.text())
        # if res['msg'] != "failed":
        #     self.player_id = res['msg']
        #     self.run_online()
        #     self.close()
        # else:
        #     print("fail")

    def send_name_data(self, data):
        self.oq.name_label.setText("my name : " + data)
        self.oq.player_id = self.player_id
