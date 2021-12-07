from .config import REDIS_PORT, REDIS_HOST
from redis import Redis
import jwt
REDIS_AUTH = Redis(host=REDIS_HOST, port=REDIS_PORT, db=5, decode_responses=True)
try:
    from .secret_key import SECRET_KEY
except ModuleNotFoundError:
    SECRET_KEY = 'secret'


class ValidateError(Exception):
    print()


async def is_jwt_valid(player_id, token) -> bool:
    try:
        token_decoded = jwt.decode(token, SECRET_KEY, algorithms="HS256")
        if token_decoded.get('name') == player_id:
            return True
    except:
        return False


# async def redis_jwt_get(player_id: str) -> (str, None):  # redis 에 캐시되어있으면 str, redis 에서 값을 찾지 못하면 None
#     token = REDIS_AUTH.get(player_id)
#     return token
