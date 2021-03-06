import requests
from .config import DB_SERVER_URL
try:
    from .secret_key import SECRET_KEY

    def db_post_winner(user_id: str):
        try:
            requests.post(url=DB_SERVER_URL + '/histories/winner', data={'name': user_id, 'key': SECRET_KEY}, timeout=2)
        except requests.exceptions.Timeout:
            print('timeout')

    def db_post_loser(user_id: str):
        try:
            requests.post(url=DB_SERVER_URL + '/histories/loser', data={'name': user_id, 'key': SECRET_KEY}, timeout=2)
        except requests.exceptions.Timeout:
            print('timeout')

except ModuleNotFoundError:
    def db_post_winner(user_id: str):
        print(f'module not found err \n winner {user_id=}')
        pass

    def db_post_loser(user_id: str):
        print(f'module not found err \n loser {user_id=}')
        pass

# async def auth_jwt_validate(user_id: str, jwt: str) -> bool:
#     pass
#
