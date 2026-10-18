import pygame
from game_comp import text

BASE_WIDTH = 1200
BASE_HEIGHT = 700

# Color Palette: ONLY Black, White, Blue, and Red
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_BLUE = (0, 140, 255)
COLOR_RED = (255, 50, 50)


def get_scale(width, height):
    return min(width / BASE_WIDTH, height / BASE_HEIGHT)


def centerLine(screen, config):
    scale = get_scale(config.WINDOW_WIDTH, config.WINDOW_HEIGHT)
    
    # Outer dim neon glow
    pygame.draw.line(
        screen,
        (0, 45, 90),
        (config.CENTER_X, 0),
        (config.CENTER_X, config.WINDOW_HEIGHT),
        max(1, round(6 * scale))
    )

    # Core blue line
    pygame.draw.line(
        screen,
        COLOR_BLUE,
        (config.CENTER_X, 0),
        (config.CENTER_X, config.WINDOW_HEIGHT),
        max(1, round(2 * scale))
    )


def scoreBoard(screen, player1, player2, config, p1_name="PLAYER", p2_name="AI BOT"):
    width = config.WINDOW_WIDTH
    height = config.WINDOW_HEIGHT
    scale = get_scale(width, height)

    # Main scoreboard panel
    panel_width = round(340 * scale)
    panel_height = round(64 * scale)
    panel_x = (width - panel_width) // 2
    panel_y = round(8 * scale)

    # Dark background panel
    pygame.draw.rect(
        screen,
        (6, 8, 14),
        (panel_x, panel_y, panel_width, panel_height),
        border_radius=round(10 * scale)
    )

    # Player 1 panel (Blue theme)
    inset = round(8 * scale)
    side_width = round(110 * scale)
    side_height = round(50 * scale)
    side_y = panel_y + round(7 * scale)

    left_x = panel_x + inset
    right_x = panel_x + panel_width - inset - side_width

    pygame.draw.rect(
        screen,
        (10, 25, 50),
        (left_x, side_y, side_width, side_height),
        border_radius=round(8 * scale)
    )
    pygame.draw.rect(
        screen,
        COLOR_BLUE,
        (left_x, side_y, side_width, side_height),
        width=1,
        border_radius=round(8 * scale)
    )

    # Player 2 panel (Red theme)
    pygame.draw.rect(
        screen,
        (50, 12, 18),
        (right_x, side_y, side_width, side_height),
        border_radius=round(8 * scale)
    )
    pygame.draw.rect(
        screen,
        COLOR_RED,
        (right_x, side_y, side_width, side_height),
        width=1,
        border_radius=round(8 * scale)
    )

    # Labels and scores using old font (Arial)
    label_font = pygame.font.SysFont("Arial", max(1, round(11 * scale)), bold=True)
    score_font = pygame.font.SysFont("Arial", max(1, round(22 * scale)), bold=True)

    # Labels
    p1_label = label_font.render(p1_name, True, COLOR_BLUE)
    p2_label = label_font.render(p2_name, True, COLOR_RED)
    screen.blit(p1_label, p1_label.get_rect(center=(left_x + side_width // 2, side_y + round(14 * scale))))
    screen.blit(p2_label, p2_label.get_rect(center=(right_x + side_width // 2, side_y + round(14 * scale))))

    # Scores
    p1_score = score_font.render(f"{player1.bat.score:02d}", True, COLOR_WHITE)
    p2_score = score_font.render(f"{player2.bat.score:02d}", True, COLOR_WHITE)
    screen.blit(p1_score, p1_score.get_rect(center=(left_x + side_width // 2, side_y + round(35 * scale))))
    screen.blit(p2_score, p2_score.get_rect(center=(right_x + side_width // 2, side_y + round(35 * scale))))


def timerDisplay(screen, formatted_time, config):
    width = config.WINDOW_WIDTH
    height = config.WINDOW_HEIGHT
    scale = get_scale(width, height)

    # Timer and VS label using old font (Arial)
    timer_font = pygame.font.SysFont("Arial", max(1, round(16 * scale)), bold=True)
    vs_font = pygame.font.SysFont("Arial", max(1, round(10 * scale)), bold=True)

    # Timer display
    timer_img = timer_font.render(formatted_time, True, COLOR_WHITE)
    timer_rect = timer_img.get_rect(center=(width // 2, round(25 * scale)))
    screen.blit(timer_img, timer_rect)

    # VS label
    vs_img = vs_font.render("VS", True, COLOR_WHITE)
    vs_rect = vs_img.get_rect(center=(width // 2, round(46 * scale)))
    screen.blit(vs_img, vs_rect)