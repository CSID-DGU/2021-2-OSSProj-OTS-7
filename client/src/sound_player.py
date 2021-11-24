import pygame.mixer
from .consts.asset_paths import Path
from .components.sounds import SOUNDS

SOUND_BIND = {
    "BOMB_USED": SOUNDS.sfx_bomb,
    "CLOCK_USED": SOUNDS.sfx_clock,
    "NO_ITEM_REMAIN": SOUNDS.sfx_no_item,
    "LINE_ERASED": SOUNDS.sfx_single,
    "LINE_ERASED_2": SOUNDS.sfx_double,
    "LINE_ERASED_3": SOUNDS.sfx_triple,
    "LINE_ERASED_4": SOUNDS.sfx_tetris,
    "MOVE": SOUNDS.sfx_move,
    "HARD_DROP": SOUNDS.sfx_drop
}


class SoundPlayer:
    def __init__(self):
        pass

    def update_bgm(self, level):
        if level == 1:
            self.change_music(Path.bgm_1)
        elif level == 2:
            self.change_music(Path.bgm_2)
        elif level == 3:
            self.change_music(Path.bgm_3)
        elif level == 4:
            self.change_music(Path.bgm_4)

    def change_music(self, music_path: str):
        self.stop_music()
        self.play_music(music_path)

    @staticmethod
    def stop_music() -> float:
        pos = pygame.mixer.music.get_pos()  # 현재 재생상황 반환(무한반복일때 어떻게 반환되는지 모름)
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()
        return pos

    @staticmethod
    def play_music(music_path, start_point: float = None):
        pygame.mixer.music.load(music_path)
        if start_point is not None:
            pygame.mixer.music.set_pos(start_point)  # 시작지점 설정
        pygame.mixer.music.set_volume(0.7)  # 볼륨 70%
        pygame.mixer.music.play(loops=-1)  # 무한반복

    @staticmethod
    def pause_bgm():
        pygame.mixer.music.pause()

    @staticmethod
    def unpause_bgm():
        pygame.mixer.music.unpause()

    @staticmethod
    def play_sfx(to_play):
        if to_play in SOUND_BIND.keys():
            pygame.mixer.Sound.play(SOUND_BIND[to_play])

