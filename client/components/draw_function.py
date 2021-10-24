from pygame.draw import rect
from src.variables.ui_variables import UI_VARIABLES
from components.mino import Mino
from pygame import Rect

# screen = pygame.display.set_mode((300, 374))
# 멀티플레이시 screen 만 나눠서 사용 가능할듯
block_size = UI_VARIABLES.block_size


def draw_rect(x, y, color, screen):
    rect(
        screen,
        color,
        Rect(x, y, block_size, block_size)
    )


def draw_block(x, y, color, screen):
    rect(
        screen,
        color,
        Rect(x, y, block_size, block_size)
    )
    rect(
        screen,
        UI_VARIABLES.grey_1,
        Rect(x, y, block_size, block_size),
        1
    )  # 외곽선인듯함


def draw_mino(x: int, y: int, mino: Mino, rotate: int, screen):
    for i in range(4):
        for j in range(4):
            dx = x + block_size * j
            dy = y + block_size * i
            if mino.shape[rotate][i][j] != 0:
                draw_rect(dx, dy, mino.color, screen)


# Draw game screen
def draw_in_game_screen(next_mino: Mino, hold_mino: Mino, score: int, level: int, goal: int, screen, matrix):
    screen.fill(UI_VARIABLES.grey_1)

    # sidebar
    rect(
        screen,
        UI_VARIABLES.white,
        Rect(204, 0, 96, 374)
    )

    # draw next_mino
    draw_mino(220, 140, next_mino, 0, screen)

    # draw hold_mino
    if hold_mino is not None:
        draw_mino(220, 50, hold_mino, 0, screen)

    # Set max score
    if score > 999999:
        score = 999999

    # Draw texts
    # TODO 하드코딩 수정할것
    text_hold = UI_VARIABLES.h5.render("HOLD", 1, UI_VARIABLES.black)
    text_next = UI_VARIABLES.h5.render("NEXT", 1, UI_VARIABLES.black)
    text_score = UI_VARIABLES.h5.render("SCORE", 1, UI_VARIABLES.black)
    score_value = UI_VARIABLES.h4.render(str(score), 1, UI_VARIABLES.black)
    text_level = UI_VARIABLES.h5.render("LEVEL", 1, UI_VARIABLES.black)
    level_value = UI_VARIABLES.h4.render(str(level), 1, UI_VARIABLES.black)
    text_goal = UI_VARIABLES.h5.render("GOAL", 1, UI_VARIABLES.black)
    goal_value = UI_VARIABLES.h4.render(str(goal), 1, UI_VARIABLES.black)

    # Place texts
    screen.blit(text_hold, (215, 14))
    screen.blit(text_next, (215, 104))
    screen.blit(text_score, (215, 194))
    screen.blit(score_value, (220, 210))
    screen.blit(text_level, (215, 254))
    screen.blit(level_value, (220, 270))
    screen.blit(text_goal, (215, 314))
    screen.blit(goal_value, (220, 330))

    # Draw board
    for x in range(UI_VARIABLES.width):
        for y in range(UI_VARIABLES.height):
            dx = 17 + block_size * x
            dy = 17 + block_size * y
            draw_block(dx, dy, UI_VARIABLES.t_color[matrix[x][y + 1]], screen)
