import requests
from .config import DB_SERVER_URL
try:
    from .secret_key import SECRET_KEY

    async def db_post_winner(user_id: str):
        try:
            requests.post(url=DB_SERVER_URL + '/winner', data={'name': user_id, 'key': SECRET_KEY}, timeout=2)
        except requests.exceptions.Timeout:
            print('timeout')

    async def db_post_loser(user_id: str):
        try:
            requests.post(url=DB_SERVER_URL + '/loser', data={'name': user_id, 'key': SECRET_KEY}, timeout=2)
        except requests.exceptions.Timeout:
            print('timeout')

except ModuleNotFoundError:
    async def db_post_winner(user_id: str):
        print(f'module not found err \n winner {user_id=}')
        pass

    async def db_post_loser(user_id: str):
        print(f'module not found err \n loser {user_id=}')
        pass

# async def auth_jwt_validate(user_id: str, jwt: str) -> bool:
#     pass
#
