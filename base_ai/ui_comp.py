import pygame
from game_comp import text

BASE_WIDTH = 1200
BASE_HEIGHT = 700


def get_scale(width, height):
    return min(width / BASE_WIDTH, height / BASE_HEIGHT)

def centerLine(screen,config):
    scale = get_scale(config.WINDOW_WIDTH, config.WINDOW_HEIGHT)
    centerx = config.WINDOW_WIDTH//2

    pygame.draw.line(
        screen,
        (0, 70, 100),
        (centerx, 0),
        (centerx, config.WINDOW_HEIGHT),
        max(1, round(6 * scale))
    )

    pygame.draw.line(
        screen,
        (0, 255, 255),
        (centerx, 0),
        (centerx, config.WINDOW_HEIGHT),
        max(1, round(2 * scale))
    )

def scoreBoard(screen,player1,player2,config):
    width = config.WINDOW_WIDTH
    height = config.WINDOW_HEIGHT
    scale = get_scale(width, height)

    # Main scoreboard
    panel_width = round(302 * scale)
    panel_height = round(55 * scale)
    panel_x = (width - panel_width) // 2
    panel_y = round(5 * scale)

    pygame.draw.rect(
        screen,
        (12, 18, 32),
        (panel_x, panel_y, panel_width, panel_height),
        border_radius=round(10 * scale)
    )

    # Player panels
    inset = round(8 * scale)
    panel_gap = round(16 * scale)
    side_width = round(90 * scale)
    side_height = round(47 * scale)
    side_y = panel_y + round(4 * scale)

    left_x = panel_x + inset
    right_x = panel_x + panel_width - inset - side_width

    pygame.draw.rect(
        screen,
        (15, 42, 58),
        (left_x, side_y, side_width, side_height),
        border_radius=round(7 * scale)
    )

    pygame.draw.rect(
        screen,
        (55, 24, 35),
        (right_x, side_y, side_width, side_height),
        border_radius=round(7 * scale)
    )

    # Player labels, centered in their panels
    label_size = max(1, round(10 * scale))
    score_size = max(1, round(20 * scale))

    text(
        "PLAYER 1", screen, (0, 220, 255),
        left_x + round(21 * scale),
        panel_y + round(6 * scale),
        font="Arial", size=label_size, bold=True
    )

    text(
        "PLAYER 2", screen, (255, 75, 90),
        right_x + round(21 * scale),
        panel_y + round(6 * scale),
        font="Arial", size=label_size, bold=True
    )

    # Scores
    text(
        f"{player1.bat.score:02}", screen, (0, 240, 255),
        left_x + round(32 * scale),
        panel_y + round(24 * scale),
        font="Arial", size=score_size, bold=True
    )

    text(
        f"{player2.bat.score:02}", screen, (255, 80, 95),
        right_x + round(32 * scale),
        panel_y + round(24 * scale),
        font="Arial", size=score_size, bold=True
    )

def timerDisplay(screen,formatted_time,config):
    width = config.WINDOW_WIDTH
    height = config.WINDOW_HEIGHT
    scale = get_scale(width, height)

    # Timer
    timer_font = pygame.font.SysFont(
        "Arial", max(1, round(16 * scale)), bold=True
    )

    timer_img = timer_font.render(
        formatted_time, True, (255, 255, 255)
    )

    timer_rect = timer_img.get_rect(
        center=(width // 2, round(25 * scale))
    )

    screen.blit(timer_img, timer_rect)

    # VS label
    text(
        "VS", screen, (130, 150, 175),
        width // 2, round(39 * scale),
        font="Arial", size=max(1, round(9 * scale)), bold=True
    )