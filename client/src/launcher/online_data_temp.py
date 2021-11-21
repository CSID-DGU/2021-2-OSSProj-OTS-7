from collections import deque


class GuiEmit:
    def __init__(self):
        self.to_handler = deque([])
        self.to_gui = deque([])

    def h_gen(self):
        while True:
            if self.to_handler:
                yield self.to_handler.popleft()

    # def g_gen(self):
    #     while True:
    #         if self.to_gui:
    #             yield self.to_gui.popleft()

    def h_append(self, t: str, d: object):
        to_emit = {
            't': t,
            'd': d
        }
        self.to_handler.append(to_emit)

