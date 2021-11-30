import time
from PySide2 import QtWidgets, QtCore
from PySide2.QtWidgets import QMessageBox, QWidget, QVBoxLayout, QHBoxLayout, \
    QLabel
from .gui_com import GuiCom
import os
import signal


class OnlineLobbyView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.hlayout = QHBoxLayout()
        self.v1layout = QVBoxLayout()
        self.v2layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.setLayout(self.hlayout)
        self.setLayout(self.v1layout)
        self.setLayout(self.v2layout)
        self.setGeometry(0, 0, 700, 700)
        self.setWindowTitle('OTS Lobby')
        self.name_label = QLabel("login success")
        self.layout.addWidget(self.name_label)
        self.layout.addLayout(self.hlayout)
        self.hlayout.addLayout(self.v1layout)
        self.hlayout.addLayout(self.v2layout)
        self.invite_label = QLabel("Approacher List")
        self.v1layout.addWidget(self.invite_label)

        self.list_box_approacher = QtWidgets.QListWidget()
        self.list_box_approacher.setGeometry(QtCore.QRect(250, 70, 201, 301))
        self.list_box_approacher.setDisabled(True)
        self.list_box_approacher.setObjectName("approacher_list")
        self.v1layout.addWidget(self.list_box_approacher)
        self.list_box_approacher.itemClicked.connect(self.approacher_list_item_clicked)

        self.wait_label = QLabel("Waiting List")
        self.v2layout.addWidget(self.wait_label)

        self.list_box_waiter = QtWidgets.QListWidget()
        self.list_box_waiter.setGeometry(QtCore.QRect(20, 70, 201, 301))
        self.list_box_waiter.setObjectName("waiting_list")
        self.v2layout.addWidget(self.list_box_waiter)
        self.list_box_waiter.itemClicked.connect(self.waiter_list_item_clicked)

        self.game_start_btn = QtWidgets.QPushButton("Wait for approachers")
        self.game_start_btn.setGeometry(QtCore.QRect(120, 280, 80, 26))
        self.game_start_btn.setObjectName("game_start_btn")
        self.game_start_btn.clicked.connect(self.game_start_btn_clicked)
        self.layout.addWidget(self.game_start_btn)

        self.list_item_msg_box = QtWidgets.QMessageBox()
        self.list_item_msg_box.setObjectName("list_item_msg_box")
        self.list_item_msg_box.resize(100, 80)
        self.list_item_msg_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

        self.approaching_msg_box = QtWidgets.QMessageBox()  # 대결 제안시
        self.approaching_msg_box.setObjectName('approaching_msg_box')
        self.approaching_msg_box.resize(100, 80)
        self.approaching_msg_box.setStandardButtons(QMessageBox.Cancel)

        self.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, False)  # 닫기 버튼 비활성화

    def approacher_list_item_clicked(self, item):
        pass

    def waiter_list_item_clicked(self, item):
        pass

    def game_start_btn_clicked(self):
        pass


class OnlineLobby(OnlineLobbyView):
    class SigObj(QtCore.QObject):
        signal = QtCore.Signal(object)

    def __init__(self, gui_com: GuiCom, player_id: str, sig_obj: SigObj = None):
        super().__init__()
        self.player_id = player_id

        self.waiter_list = []
        self.approacher_list = []
        self.waiter_update()
        self.approacher_update()

        self.gui_emit = gui_com
        self.status = 'hello'

        self.waiting = False
        if sig_obj is None:
            self.sig_obj = self.SigObj()
        self.signal = self.sig_obj.signal
        self.signal.connect(self.signal_parse)
        self.set_view_hello()

    def init(self):
        self.status = ''
        self.setHidden(False)
        self.list_box_clear(self.list_box_waiter)
        self.list_box_clear(self.list_box_approacher)
        self.set_status_hello()


    def set_view_waiting(self):
        self.list_box_waiter.setDisabled(True)
        self.list_box_approacher.setDisabled(False)
        self.game_start_btn.setText('Waiting... Click to cancel')

    def set_view_hello(self):
        self.list_box_waiter.setDisabled(False)
        self.list_box_approacher.setDisabled(True)
        self.game_start_btn.setText('Click to wait for approachers')

    def set_status_waiting(self):
        self.status = 'waiting'
        self.set_view_waiting()
        self.emit_to_handler(t='wa')

    def set_status_hello(self):
        if self.status == 'approaching':
            self.emit_to_handler(t='ac')
        elif self.status == 'waiting':
            self.emit_to_handler(t='wr')
        self.status = 'hello'
        self.set_view_hello()

    def set_view_approaching(self):
        self.list_box_approacher.setDisabled(True)
        self.list_box_waiter.setDisabled(True)
        self.game_start_btn.setText('Approaching... Click to cancel')

    def set_status_approaching(self):
        self.status = 'approaching'
        self.set_view_approaching()

    def game_start_btn_clicked(self):
        if self.status == 'hello':
            self.set_status_waiting()
        elif self.status == 'waiting':
            self.set_status_hello()
        elif self.status == 'approaching':
            self.set_status_hello()

    def approacher_list_item_clicked(self, item):
        self.list_item_msg_box_dialog(item, t='ha', alt_t='hr', msg='의 대결 제안 수락')

    def waiter_list_item_clicked(self, item):
        if self.list_item_msg_box_dialog(item, t='a', msg='에게 대결 제안'):
            self.set_status_approaching()
        else:
            self.set_status_hello()

    def list_item_msg_box_dialog(self, item, t: str, msg: str, alt_t: str = None) -> bool:
        # t - 코드, msg- 표시될 텍스트, alt_t - 취소시 실행할 코드
        self.list_item_msg_box.show()
        user_id = item.text()
        self.list_item_msg_box.setText(user_id + msg)

        msg_box_return = self.list_item_msg_box.exec()
        if msg_box_return == QMessageBox.Ok:
            print(user_id + msg)
            self.emit_to_handler(t=t, d=user_id)
            return True
        else:
            if alt_t is not None:
                self.emit_to_handler(t=alt_t, d=user_id)
            self.list_item_msg_box.close()
            return False

    def list_box_add(self, listbox: QtWidgets.QListWidget, ref: list):
        for itm in ref:
            if itm != self.player_id:
                listbox.addItem(itm)

    @staticmethod
    def list_box_clear(listbox: QtWidgets.QListWidget):
        lc = listbox.count()
        for i in range(lc):
            listbox.takeItem(0)

    def list_box_update(self, listbox: QtWidgets.QListWidget, ref: list):
        self.list_box_clear(listbox=listbox)
        self.list_box_add(listbox=listbox, ref=ref)

    def waiter_update(self):
        self.list_box_update(self.list_box_waiter, self.waiter_list)

    def approacher_update(self):
        self.list_box_update(self.list_box_approacher, self.approacher_list)

    def emit_to_handler(self, t: str, d: object = None):
        self.gui_emit.to_handler(t, d)

    def signal_parse(self, sig: dict):
        if sig['t'] == 'server_connection_lost':
            self.on_server_connection_lost()  # 서버 연결 끊김
        elif sig['t'] == 'approach_rejected':
            self.on_approach_rejected()  # 제안 거절됨
        elif sig['t'] == 'game_start':
            self.on_match_start()  # 게임 시작
        elif sig['t'] == 'init':
            self.init()  # 초기화

    def on_server_connection_lost(self):
        msg_box = QtWidgets.QMessageBox()
        msg_box.critical(self, 'Server Connection Lost', '서버와의 연결이 끊어졌습니다.')
        msg_box.resize(100, 80)
        msg_box.setStandardButtons(QMessageBox.Ok)
        res = msg_box.result()
        if res == 0:  # msg_box 버튼 눌렀을 때
            os.kill(os.getpid(), signal.SIGTERM)  # POSIX 신호인데 윈도우에서 일단 동작을 함.

    def on_approach_rejected(self):
        self.set_status_hello()

    def on_match_start(self):
        self.setHidden(True)


