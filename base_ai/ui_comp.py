import pygame
from game_comp import text

def centerLine(screen,centerx,height):
    # Draw the center line
    # Outer glow
    pygame.draw.line(
    screen, (0, 70, 100),
    (centerx, 0), (centerx, height), 6
    )

    # Bright neon center
    pygame.draw.line(
    screen, (0, 255, 255),
    (centerx, 0), (centerx, height), 2
    )
def scoreBoard(screen,player1,player2,width,height):
    panel_width = 302
    panel_height = 55

    panel_x = (width - panel_width) // 2
    panel_y = 5    

    # Scoreboard panel
    pygame.draw.rect(
        screen, (12, 18, 32),
        (panel_x, panel_y, panel_width, panel_height),
        border_radius=10
    )

    # Colored player panels
    pygame.draw.rect(
        screen, (15, 42, 58),
        (panel_x + 8, panel_y + 4, 90, 47),
        border_radius=7
    )

    pygame.draw.rect(
        screen, (55, 24, 35),
        (panel_x + 204, panel_y + 4, 90, 47),
        border_radius=7
    )

    text("PLAYER 1", screen, (0, 220, 255),
         panel_x + 29, panel_y + 6,
         font="Arial", size=10, bold=True)

    text("PLAYER 2", screen, (255, 75, 90),
         panel_x + 225, panel_y + 6,
         font="Arial", size=10, bold=True)

    # Scores
    text(f"{player1.bat.score:02}", screen,
         (0, 240, 255), panel_x + 40, panel_y + 24,
         font="Arial", size=20, bold=True)

    text(f"{player2.bat.score:02}", screen,
         (255, 80, 95), panel_x + 240, panel_y + 24,
         font="Arial", size=20, bold=True)

def timerDisplay(screen,formatted_time,width):
    # Timer
    timer_font = pygame.font.SysFont("Arial", 16, bold=True)
    timer_img = timer_font.render(
        formatted_time, True, (255, 255, 255)
    )
    timer_rect = timer_img.get_rect(center=(width//2, 25))
    screen.blit(timer_img, timer_rect)

    # VS label
    text("VS", screen, (130, 150, 175), width//2, 39,
        font="Arial", size=9, bold=True)