from PySide2.QtWidgets import QWidget, QApplication, QVBoxLayout, QLabel, \
    QPushButton, QLineEdit
from .online_queue import online_queue
import json, requests
import sys


class login_window(QWidget):
    def __init__(self):
        super().__init__()
        self.initialize()
        self.oq = online_queue()
    def initialize(self):
        self.login_url = "http://localhost:8080/users/login" # 차후변경
        self.layout = QVBoxLayout()
        self.label = QLabel("please login")
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)
        self.setGeometry(150, 150, 200, 200)
        self.setWindowTitle('OTS')

        self.login_btn = QPushButton("Login")
        self.layout.addWidget(self.login_btn)
        self.login_btn.clicked.connect(self.login_btn_clicked)

        self.input_email = QLineEdit()
        self.input_email.setPlaceholderText('email 입력')
        self.layout.addWidget(self.input_email)
        self.input_pwd = QLineEdit()
        self.input_pwd.setPlaceholderText('비밀번호 입력')
        self.layout.addWidget(self.input_pwd)

    def login_btn_clicked(self):
        self.res = requests.post(self.login_url, data={'email': self.input_email.text(), 'password' : self.input_pwd.text()})
        if(self.res.json()['msg'] != "failed"):
            print("login")
            print(f"name :  {self.res.json()}")
            self.oq.show()
        else:
            print("fail")
