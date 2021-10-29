class PlayerConnection:
    def __init__(self, user_id: str):
        self.status = 'hello'

    def parse_data(self, data: dict):
        data_type = data.get('type')
        if data_type is not None:
            pass