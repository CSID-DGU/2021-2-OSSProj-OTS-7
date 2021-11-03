from .main import OTS
from tkinter import *
import webbrowser
from PIL import Image
from .variables.ui_variables import UI_VARIABLES as uv


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

        self.signup_btn = Button(text='Sign Up', width=15, command=self.signup_btn,)
        self.signup_btn.pack()

        self.help_btn = Button(text='Help', width=15, command=self.help_btn,)
        self.help_btn.pack()

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

    def signup_btn(self):
        webbrowser.open("https://otsauth.loca.lt/")

    def help_btn(self):
        image = Image.open(uv.help_image)
        image.show()

    def run_game(self):
        self.tk.destroy()
        ots = OTS(game_mode=self.game_mode, player_id=self.player_id)
        ots.main_loop()
