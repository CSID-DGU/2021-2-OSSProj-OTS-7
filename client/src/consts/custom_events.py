from pygame.locals import USEREVENT

custom_events = dict(
    # 상태 업데이트
    DISPLAY_UPDATE_REQUIRED=USEREVENT + 1,
    LEVEL_UP=USEREVENT + 2,
    GAME_OVER=USEREVENT + 3,
    PAUSE=USEREVENT + 4,

    # 멀티플레이 이벤트
    MP_SERVER_CONNECTED=USEREVENT + 11,
    MP_SERVER_DISCONNECTED=USEREVENT + 12,
    MP_GAME_START=USEREVENT + 13,
    MP_GAME_OVER=USEREVENT + 14,
    MP_INNIT=USEREVENT + 15,

    # 소리 재생용
    ROTATE=USEREVENT + 20,
    MOVE=USEREVENT + 21,
    HARD_DROP=USEREVENT + 22,


    LINE_ERASED=USEREVENT + 31,
    LINE_ERASED_2=USEREVENT + 32,
    LINE_ERASED_3=USEREVENT + 33,
    LINE_ERASED_4=USEREVENT + 34,

    BOMB_USED=USEREVENT + 40,
    CLOCK_USED=USEREVENT + 41,
    NO_ITEM_REMAIN=USEREVENT + 42,
)

custom_events_reversed = {}
for key, val in custom_events.items():
    custom_events_reversed[val] = key
