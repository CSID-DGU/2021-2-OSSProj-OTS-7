from .config import REDIS_PORT, REDIS_HOST
from redis import Redis
from . import api_requests

REDIS_AUTH = Redis(host=REDIS_HOST, port=REDIS_PORT, db=5, decode_responses=True)


class ValidateError(Exception):
    print()


async def is_jwt_valid(player_id, jwt) -> bool:
    if jwt == await redis_jwt_get(player_id):  # redis 에 캐시되어있을 경우
        return True
    else:  # redis 기록에 없거나, 인증에 실패한 경우 인증 서버에 요청
        is_valid: bool = await api_requests.auth_jwt_validate(player_id, jwt)
        if is_valid is not None:
            return is_valid
        else:
            print(f"JWT Validation Failed. {player_id=}, {jwt=}")
            raise ValidateError


async def redis_jwt_get(player_id: str) -> (str, None):  # redis 에 캐시되어있으면 str, redis 에서 값을 찾지 못하면 None
    jwt = REDIS_AUTH.get(player_id)
    return jwt
