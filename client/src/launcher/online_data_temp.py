from collections import deque


class OnlineData:
    def __init__(self):
        self.thread_queue = deque([])

    def thread_queue_gen(self):
        while True:
            if self.thread_queue:
                yield self.thread_queue.popleft()

    def append(self, t: str, d: object):
        to_emit = {
            't': t,
            'd': d
        }
        self.thread_queue.append(to_emit)
