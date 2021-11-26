import requests
from .config import DB_SERVER_URL


async def db_post_winner(user_id: str):
    requests.post(url=DB_SERVER_URL, data={'name': user_id})


async def db_post_loser(user_id: str):
    requests.post(url=DB_SERVER_URL, data={'name': user_id})
