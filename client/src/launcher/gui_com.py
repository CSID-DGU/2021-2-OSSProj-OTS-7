from queue import Queue


class GuiCom:
    def __init__(self):
        self.to_handler = Queue()

    def put(self, t: str, d: object):
        to_put = {
            't': t,
            'd': d
        }
        self.to_handler.put(to_put, block=False)
