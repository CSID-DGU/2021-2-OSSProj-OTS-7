from pygame.mixer import Sound
from ..consts.asset_paths import Path


class SOUNDS:
    sfx_click = Sound(Path.sfx_click)
    sfx_move = Sound(Path.sfx_move)
    sfx_drop = Sound(Path.sfx_drop)
    sfx_single = Sound(Path.sfx_single)
    sfx_double = Sound(Path.sfx_double)
    sfx_triple = Sound(Path.sfx_triple)
    sfx_tetris = Sound(Path.sfx_tetris)

    sfx_bomb = Sound(Path.sfx_bomb)
    sfx_clock = Sound(Path.sfx_clock)
    sfx_no_item = Sound(Path.sfx_no_item)

    bgm_1 = Sound(Path.bgm_1)
    bgm_2 = Sound(Path.bgm_2)
    bgm_3 = Sound(Path.bgm_3)
    bgm_4 = Sound(Path.bgm_4)