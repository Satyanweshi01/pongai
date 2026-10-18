import pygame
from game_comp import text

BASE_WIDTH = 1200
BASE_HEIGHT = 700


def get_scale(width, height):
    return min(width / BASE_WIDTH, height / BASE_HEIGHT)

def centerLine(screen,config):
    scale = get_scale(config.WINDOW_WIDTH, config.WINDOW_HEIGHT)
    

    pygame.draw.line(
        screen,
        (0, 70, 100),
        (config.CENTER_X, 0),
        (config.CENTER_X, config.WINDOW_HEIGHT),
        max(1, round(6 * scale))
    )

    pygame.draw.line(
        screen,
        (0, 255, 255),
        (config.CENTER_X, 0),
        (config.CENTER_X, config.WINDOW_HEIGHT),
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


def infoBoard(
    screen,
    gen=0,
    best_fitness=0.0,
    all_time_best_fitness=0.0,
    blue_score=0,
    red_score=0,
    rally_deflections=0,
    last_action=0,
    speed=1,
    config=None
):
    width = config.WINDOW_WIDTH if config else screen.get_width()
    height = config.WINDOW_HEIGHT if config else screen.get_height()
    scale = get_scale(width, height)

    hud_width = round(400 * scale)
    hud_height = round(145 * scale)
    hud_x = round(15 * scale)
    hud_y = round(15 * scale)

    # Dark translucent background panel
    hud_surface = pygame.Surface((hud_width, hud_height), pygame.SRCALPHA)
    pygame.draw.rect(
        hud_surface,
        (8, 14, 26, 210),
        (0, 0, hud_width, hud_height),
        border_radius=round(8 * scale)
    )
    screen.blit(hud_surface, (hud_x, hud_y))

    font_large = pygame.font.SysFont("Arial", max(1, round(18 * scale)), bold=True)
    font_small = pygame.font.SysFont("Arial", max(1, round(13 * scale)), bold=True)

    action_names = {0: "HOLD [ — ]", 1: "UP [ ▲ ]", 2: "DOWN [ ▼ ]"}
    WHITE = (255, 255, 255)

    record_str = f"{all_time_best_fitness:+.2f}" if all_time_best_fitness != -float("inf") else "0.00"
    gen_text = font_large.render(f"GENERATION: {gen:03d}", True, WHITE)
    fit_text = font_small.render(f"CURR FIT: {best_fitness:+.2f} | ALL-TIME: {record_str}", True, WHITE)
    score_text = font_small.render(f"SCORE: Blue {blue_score:02d} | Red {red_score:02d}", True, WHITE)
    hits_text = font_small.render(f"RALLY DEFLECTIONS: {rally_deflections}", True, WHITE)
    act_text = font_small.render(f"AI ACTION: {action_names.get(last_action, 'UNKNOWN')}", True, WHITE)
    speed_text = font_small.render(f"SPEED: {speed}x  [↑/↓ Speed, SPACE Pause, S Save, ESC Quit]", True, WHITE)

    screen.blit(gen_text, (hud_x + round(10 * scale), hud_y + round(5 * scale)))
    screen.blit(fit_text, (hud_x + round(10 * scale), hud_y + round(27 * scale)))
    screen.blit(score_text, (hud_x + round(10 * scale), hud_y + round(50 * scale)))
    screen.blit(hits_text, (hud_x + round(10 * scale), hud_y + round(67 * scale)))
    screen.blit(act_text, (hud_x + round(10 * scale), hud_y + round(84 * scale)))
    screen.blit(speed_text, (hud_x + round(10 * scale), hud_y + round(103 * scale)))