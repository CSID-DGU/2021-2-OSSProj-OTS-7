import threading
from PySide2 import QtWidgets, QtCore
from PySide2.QtWidgets import QMessageBox, QWidget, QVBoxLayout, QHBoxLayout, \
    QLabel
from PySide2.QtCore import SIGNAL, Signal
from .online_data_temp import OnlineData


class OnlineLobby(QWidget):
    signal = Signal(str)
    def __init__(self, online_data: OnlineData):
        super().__init__()
        self.player_id = ""
        self.initialize()
        self.waitting_list = ["a", "b", "c", "d"]
        self.inviting_list = ["e", "f", "g", "h"]
        self.set_invitings()
        self.set_waiting()
        self.online_data = online_data

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
        self.invite_label = QLabel("Inviting List")
        self.v1layout.addWidget(self.invite_label)

        self.invite_list_widget = QtWidgets.QListWidget()
        self.invite_list_widget.setGeometry(QtCore.QRect(250, 70, 201, 301))
        self.invite_list_widget.setObjectName("invite_list")
        self.v1layout.addWidget(self.invite_list_widget)
        self.invite_list_widget.itemClicked.connect(self.invite_clicked)

        self.wait_label = QLabel("Waiting List")
        self.v2layout.addWidget(self.wait_label)

        self.wait_list_widget = QtWidgets.QListWidget()
        self.wait_list_widget.setGeometry(QtCore.QRect(20, 70, 201, 301))
        self.wait_list_widget.setObjectName("waiting_list")
        self.v2layout.addWidget(self.wait_list_widget)
        self.wait_list_widget.itemClicked.connect(self.wait_clicked)

        self.game_start_btn = QtWidgets.QPushButton("GAME START")
        self.game_start_btn.setGeometry(QtCore.QRect(120, 280, 80, 26))
        self.game_start_btn.setObjectName("game_start_btn")
        self.game_start_btn.clicked.connect(self.game_start_btn_clicked)
        self.layout.addWidget(self.game_start_btn)

        self.invite_msg_box = QtWidgets.QMessageBox()
        self.invite_msg_box.setObjectName("invite_msg_box")
        self.invite_msg_box.resize(100, 80)
        self.invite_msg_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

        self.wait_msg_box = QtWidgets.QMessageBox()
        self.wait_msg_box.setObjectName("wait_dialog_box")
        self.wait_msg_box.resize(100, 80)
        self.wait_msg_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

    def game_start_btn_clicked(self):
        t = threading.Thread(target=self.run_online)
        t.start()

    def invite_clicked(self, item):
        self.invite_msg_box.show()
        self.invite_msg_box.setText(item.text() + " 대결 수락")
        self.invite_return = self.invite_msg_box.exec()
        if self.invite_return == QMessageBox.Ok:
            print("대결 시작")
            self.online_data.message_queue.append(item.text())
        else:
            self.invite_msg_box.destroy()

    def wait_clicked(self, item):
        self.wait_msg_box.show()
        self.wait_msg_box.setText(item.text() + " 초대")
        self.wait_return = self.wait_msg_box.exec()
        if self.wait_return == QMessageBox.Ok:
            print("초대")

        else:
            self.wait_msg_box.destroy()

    def set_waiting(self):
        for i in range(len(self.waitting_list)):
            self.wait_list_widget.addItem(self.waitting_list[i])

    def set_invitings(self):
        for i in range(len(self.inviting_list)):
            self.invite_list_widget.addItem(self.inviting_list[i])
