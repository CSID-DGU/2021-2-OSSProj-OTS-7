from PySide2.QtWidgets import QWidget, QApplication, QVBoxLayout, QLabel, \
  QPushButton, QLineEdit
import json, requests
import sys


class online_queue(QWidget):
  def __init__(self):
    super().__init__()
    self.initialize()

  def initialize(self):
    self.layout = QVBoxLayout()
    self.label = QLabel("login success")
    self.layout.addWidget(self.label)
    self.setLayout(self.layout)
    self.setGeometry(150, 150, 200, 200)
    self.setWindowTitle('OTS')
