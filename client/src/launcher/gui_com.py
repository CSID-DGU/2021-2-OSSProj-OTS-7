from queue import Queue


# PySide2로 구현한 런처가 온라인 핸들러와 통신하기 위한 클래스
# 온라인 핸들러는 이 클래스를 이용해서 수신하고, PySide2로 구현한 런처는 시그널을 이용해서 수신함.
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
