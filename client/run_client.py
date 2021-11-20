try:
    from client.src.launcher.main_window import Launcher
except ModuleNotFoundError:
    from src.launcher.main_window import Launcher

if __name__ == '__main__':
    lc = Launcher()
    lc.run_launcher()
