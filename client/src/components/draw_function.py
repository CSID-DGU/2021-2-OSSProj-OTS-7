import pygame
from pygame.draw import rect
from ..variables.ui_variables import UI_VARIABLES
from .mino import Mino
from pygame import Rect

# screen = pygame.display.set_mode((300, 374))
# 멀티플레이시 screen 만 나눠서 사용 가능할듯
BLOCK_SIZE: int = UI_VARIABLES.init_block_size


# 정사각형 그리는 코드
def draw_rect(x: int, y: int, color: int, screen):
    rect(
        screen,
        color,
        Rect(x, y, BLOCK_SIZE, BLOCK_SIZE)
    )


# 외곽선을 포함하여 정사각형 그리는 코드
def draw_block(x: int, y: int, color: int, screen):
    # 정사각형
    draw_rect(x, y, color, screen)
    # 외곽선
    rect(
        screen,
        UI_VARIABLES.grey_1,
        Rect(x, y, BLOCK_SIZE, BLOCK_SIZE),
        1
    )


# Mino 객체의 값을 참조하여 화면에 그림. 다음 미노와 홀드한 미노를 그리는데 사용됨.
def draw_mino(x: int, y: int, mino: Mino, rotate: int, screen):
    for i in range(4):
        for j in range(4):
            dx = x + BLOCK_SIZE * j
            dy = y + BLOCK_SIZE * i
            if mino.shape[rotate][i][j] != 0:
                draw_rect(dx, dy, mino.color, screen)


def draw_game_instance(game_instance, screen, x_mod: int = 0):
    # sidebar
    rect(
        screen,
        UI_VARIABLES.white,
        Rect(204+x_mod, 0, 96, 374)
    )

    # draw next_mino
    draw_mino(220+x_mod, 90, game_instance.next_mino, 0, screen)

    # draw hold_mino
    if game_instance.hold_mino is not None:
        draw_mino(220+x_mod, 30, game_instance.hold_mino, 0, screen)

    # Set max score
    if game_instance.score > 999999:
        score = 999999
    # item image
    bomb_image = pygame.image.load("assets/img/bomb.png")
    bomb_image = pygame.transform.scale(bomb_image, (30, 30))
    left_bomb = pygame.transform.scale(bomb_image, (15, 15))

    clock_image = pygame.image.load("assets/img/clock.png")
    clock_image = pygame.transform.scale(clock_image, (30, 30))
    left_clock = pygame.transform.scale(clock_image, (15, 15))

    # 현재 사용 가능한 item, Left item 보여줌
    if game_instance.my_item_list:
        if game_instance.my_item_list[0] == "bomb":
            screen.blit(bomb_image, [x_mod+215, 335])
        elif game_instance.my_item_list[0] == "clock":
            screen.blit(clock_image, [x_mod + 215, 335])

    screen.blit(left_bomb, [x_mod + 255, 335])
    screen.blit(left_clock, [x_mod + 255, 355])

    # texts
    # TODO 하드코딩 수정할것
    text_hold = UI_VARIABLES.h5.render("HOLD", 1, UI_VARIABLES.black)
    text_next = UI_VARIABLES.h5.render("NEXT", 1, UI_VARIABLES.black)
    text_score = UI_VARIABLES.h5.render("SCORE", 1, UI_VARIABLES.black)
    score_value = UI_VARIABLES.h4.render(str(game_instance.score), 1, UI_VARIABLES.black)
    text_level = UI_VARIABLES.h5.render("LEVEL", 1, UI_VARIABLES.black)
    level_value = UI_VARIABLES.h4.render(str(game_instance.level), 1, UI_VARIABLES.black)
    text_goal = UI_VARIABLES.h5.render("GOAL", 1, UI_VARIABLES.black)
    goal_value = UI_VARIABLES.h4.render(str(game_instance.goal), 1, UI_VARIABLES.black)
    text_item = UI_VARIABLES.h5.render("ITEM    LEFT", 1, UI_VARIABLES.black)

    bomb_count = 0
    clock_count = 0
    if game_instance.my_item_list:
        bomb_count = game_instance.my_item_list.count('bomb')
        clock_count = game_instance.my_item_list.count('clock')

    left_item_bomb = UI_VARIABLES.h6.render("x " + str(bomb_count), 1, UI_VARIABLES.black)
    left_item_clock = UI_VARIABLES.h6.render("x " + str(clock_count), 1, UI_VARIABLES.black)

    # draw texts to screen
    screen.blit(text_hold, (x_mod+215, 15))
    screen.blit(text_next, (x_mod+215, 70))
    screen.blit(text_score, (x_mod+215, 134))
    screen.blit(score_value, (x_mod+220, 154))
    screen.blit(text_level, (x_mod+215, 194))
    screen.blit(level_value, (x_mod+220, 214))
    screen.blit(text_goal, (x_mod+215, 254))
    screen.blit(goal_value, (x_mod+220, 274))
    screen.blit(text_item, (x_mod + 215, 314))
    screen.blit(left_item_bomb, (x_mod + 275, 335))
    screen.blit(left_item_clock, (x_mod + 275, 355))

    # draw board to screen
    for x in range(UI_VARIABLES.init_board_width):
        for y in range(UI_VARIABLES.init_board_height):
            dx = x_mod + 17 + BLOCK_SIZE * x
            dy = 17 + BLOCK_SIZE * y
            draw_block(dx, dy, UI_VARIABLES.t_color[game_instance.board.temp_matrix[x][y + 1]], screen)


# Draw game screen
def draw_in_game_screen(game_instance, screen, multiplayer_instance=None):
    screen.fill(UI_VARIABLES.grey_1)

    draw_game_instance(game_instance=game_instance, screen=screen)
    if multiplayer_instance is not None:
        draw_game_instance(game_instance=multiplayer_instance, screen=screen, x_mod=300)
