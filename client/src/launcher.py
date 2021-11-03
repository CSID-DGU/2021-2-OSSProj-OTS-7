from .main import OTS
from tkinter import *


class Launcher:
    def __init__(self):
        self.tk = Tk()
        self.tk.title('OTS Launcher')

        # 설정
        self.game_mode = None
        self.player_id = 'offline'

        # 구성요소
        self.single_btn = Button(text='Single Play', width=15, command=self.on_single_btn,)
        self.single_btn.pack()

        self.multi_btn = Button(text='Dual Play', width=15, command=self.on_dual_btn,)
        self.multi_btn.pack()

        self.online_btn = Button(text='Online Play', width=15, command=self.on_online_btn,)
        self.online_btn.pack()

    def run_launcher(self):
        self.tk.mainloop()

    def on_single_btn(self):
        self.game_mode = 'single'
        self.run_game()

    def on_dual_btn(self):
        self.game_mode = 'dual'
        self.run_game()

    def on_online_btn(self):
        self.game_mode = 'online'
        self.run_game()

    def run_game(self):
        self.tk.destroy()
        ots = OTS(game_mode=self.game_mode, player_id=self.player_id)
        ots.main_loop()
