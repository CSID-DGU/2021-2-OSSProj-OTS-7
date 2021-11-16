import pygame
pygame.init()
try:
    icon = pygame.image.load("assets/img/tetris.png")
except FileNotFoundError:
    import os
    print(__file__)
    os.chdir(__file__.replace('/src/__init__.py', ''))  # 작업 경로를 client 폴더로 변경
finally:
    icon = pygame.image.load("assets/img/tetris.png")

pygame.display.set_icon(icon)
