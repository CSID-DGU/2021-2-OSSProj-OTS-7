import requests
from .config import DB_SERVER_URL
from .secret_key import SECRET_KEY



async def db_post_winner(user_id: str):
    requests.post(url=DB_SERVER_URL, data={'name': user_id, 'key': SECRET_KEY})


async def db_post_loser(user_id: str):
    requests.post(url=DB_SERVER_URL, data={'name': user_id, 'key': SECRET_KEY})
