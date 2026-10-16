import pygame
from game_comp import text
def centerLine(screen):
    # Draw the center line
    # Outer glow
    pygame.draw.line(
    screen, (0, 70, 100),
    (401, 0), (401, 455), 6
    )

    # Bright neon center
    pygame.draw.line(
    screen, (0, 255, 255),
    (401, 0), (401, 455), 2
    )
def scoreBoard(screen,player1,player2):
    # Scoreboard panel
    pygame.draw.rect(
    screen, (12, 18, 32),
    (250, 5, 302, 55),
    border_radius=10
    )

    # Colored player panels
    pygame.draw.rect(
    screen, (15, 42, 58),
    (258, 9, 90, 47),
    border_radius=7
    )

    pygame.draw.rect(
    screen, (55, 24, 35),
    (454, 9, 90, 47),
    border_radius=7
    )

    # Player labels
    text("PLAYER 1", screen, (0, 220, 255), 279, 11,
        font="Arial", size=10, bold=True)

    text("PLAYER 2", screen, (255, 75, 90), 475, 11,
        font="Arial", size=10, bold=True)

    # Scores
    text(f"{player1.bat.score:02}", screen, (0, 240, 255),
        290, 29, font="Arial", size=20, bold=True)

    text(f"{player2.bat.score:02}", screen, (255, 80, 95),
        490, 29, font="Arial", size=20, bold=True)

def timerDisplay(screen,formatted_time):
    # Timer
    timer_font = pygame.font.SysFont("Arial", 16, bold=True)
    timer_img = timer_font.render(
        formatted_time, True, (255, 255, 255)
    )
    timer_rect = timer_img.get_rect(center=(401, 25))
    screen.blit(timer_img, timer_rect)

    # VS label
    text("VS", screen, (130, 150, 175), 395, 39,
        font="Arial", size=9, bold=True)