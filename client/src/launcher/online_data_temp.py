from collections import deque


class OnlineData:
    def __init__(self):
        self.message_queue = deque([])

    def message_queue_gen(self):
        while True:
            if self.message_queue:
                yield self.message_queue.popleft()