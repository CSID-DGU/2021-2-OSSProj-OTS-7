from queue import Queue


class GuiCom:
    def __init__(self):
        self.handler_queue = Queue()

    @staticmethod
    def build_dict(t, d):
        to_put = {
            't': t,
            'd': d
        }
        return to_put

    def to_handler(self, t: str, d: object):
        to_put = self.build_dict(t, d)
        self.handler_queue.put(to_put, block=False)
