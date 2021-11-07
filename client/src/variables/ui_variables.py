import pygame
from pygame.mixer import Sound


class UI_VARIABLES:
    init_block_size = 17  # Height, width of single block
    init_board_width = 10  # Board width
    init_board_height = 20  # Board height

    init_screen_width = 300  # 초기 스크린 너비
    init_screen_height = 374  # 초기 스크린 높이
    init_rect_x = 0  # 하단 검정 박스 x 최소 좌표
    init_rect_y = 187  # 하단 검정 박스 y최소 좌표
    init_rect_width = 300  # 하단 검정 박스 너비
    init_rect_height = 187  # 하단 검정 박스 높이
    pygame.init()
    # Fonts
    font_path = "assets/fonts/OpenSans-Light.ttf"
    font_path_b = "assets/fonts/OpenSans-Bold.ttf"
    font_path_i = "assets/fonts/Inconsolata/Inconsolata.otf"

    h1 = pygame.font.Font(font_path, 50)
    h2 = pygame.font.Font(font_path, 30)
    h4 = pygame.font.Font(font_path, 20)
    h5 = pygame.font.Font(font_path, 13)
    h6 = pygame.font.Font(font_path, 10)

    h1_b = pygame.font.Font(font_path_b, 50)
    h2_b = pygame.font.Font(font_path_b, 30)

    h2_i = pygame.font.Font(font_path_i, 30)
    h5_i = pygame.font.Font(font_path_i, 13)

    # Sounds
    click_sound = Sound("assets/sounds/SFX_ButtonUp.wav")
    move_sound = Sound("assets/sounds/SFX_PieceMoveLR.wav")
    drop_sound = Sound("assets/sounds/SFX_PieceHardDrop.wav")
    single_sound = Sound("assets/sounds/SFX_SpecialLineClearSingle.wav")
    double_sound = Sound("assets/sounds/SFX_SpecialLineClearDouble.wav")
    triple_sound = Sound("assets/sounds/SFX_SpecialLineClearTriple.wav")
    tetris_sound = Sound("assets/sounds/SFX_SpecialTetris.wav")
    bgm_list = ["assets/sounds/BGM_level1.wav",
                "assets/sounds/BGM_level2.wav",
                "assets/sounds/BGM_level3.wav",
                "assets/sounds/BGM_level4.wav"]
    # Background colors
    black = (10, 10, 10) #rgb(10, 10, 10)
    white = (255, 255, 255) #rgb(255, 255, 255)
    grey_1 = (26, 26, 26) #rgb(26, 26, 26)
    grey_2 = (35, 35, 35) #rgb(35, 35, 35)
    grey_3 = (55, 55, 55) #rgb(55, 55, 55)

    # Tetrimino colors
    cyan = (69, 206, 204) #rgb(69, 206, 204) # I
    blue = (64, 111, 249) #rgb(64, 111, 249) # J
    orange = (253, 189, 53) #rgb(253, 189, 53) # L
    yellow = (246, 227, 90) #rgb(246, 227, 90) # O
    green = (98, 190, 68) #rgb(98, 190, 68) # S
    pink = (242, 64, 235) #rgb(242, 64, 235) # T
    red = (225, 13, 27) #rgb(225, 13, 27) # Z

    t_color = [grey_2, cyan, blue, orange, yellow, green, pink, red, grey_3]

    # images

    bomb_image = "assets/img/bomb.png"
    clock_image = "assets/img/clock.png"
    help_image = "assets/img/help.png"
