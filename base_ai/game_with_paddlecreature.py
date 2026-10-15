import pygame
from utils import Ball,Bat,text
from nn_class import NeuralNetwork, PaddleCreature

pygame.init()

#creating window
screen = pygame.display.set_mode((802, 455))
pygame.display.set_caption("Pong Ai") 

#creating clock to control the rendering
clock = pygame.time.Clock()

# game loop
running = True

delta_time = 0.1


# bat objects
bluebat = PaddleCreature(0, 180, screen, (0, 100, 255), 20, 100) #bluebat home position (0,180)
redbat = PaddleCreature(785, 180, screen, (255, 50, 50), 20, 100) #redbat home position (785,180)

#config variables
BATSENSITIVITY = 15
BATUPBOUNDARY = 0
BATDOWNBOUNDARY = 346

WALLLEFTBOUNDARY = -20
WALLRIGHTBOUNDARY = 820
velocityconst = 5 # initial velocity

# ball object 
ball = Ball(385, 210, screen,velocityconst, 10)

frame = 0
hour = 0 
minute = 0
sec = 0
t_time = 0

while running:
    #screen.fill((0,0,0)) #fills the window with the rgb color for each iteration
    screen.fill((0, 0, 0))  # Black background

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
    text(f"{bluebat.bat.score:02}", screen, (0, 240, 255),
     290, 29, font="Arial", size=20, bold=True)

    text(f"{redbat.bat.score:02}", screen, (255, 80, 95),
     490, 29, font="Arial", size=20, bold=True)
    # time update
    frame += 1
    if frame == 60:
        sec += 1
        t_time += 1
        frame = 0
    if sec == 60:
        minute += 1
        sec = 0
    if minute == 60:
        hour += 1
        minute = 0
    formatted_time = f"{hour:02}:{minute:02}:{sec:02}"

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

    # speed dynamism
    if t_time < 30:
        ball.velocityconst = 5 
    elif t_time < 60:
        ball.velocityconst = 7 
    elif t_time < 120:
        ball.velocityconst = 9
    elif t_time < 180:
        ball.velocityconst = 11
    elif t_time < 300:
        ball.velocityconst = 13
    else:
        ball.velocityconst = 15

    ball.velocity_update()
    #print(ball.velocityconst)


    ball.draw()
    ball.update()
    ball.change_velocity()


    redbat.bat.draw()
    bluebat.bat.draw()    

    # collision between ball and bat
    if ball.rect.colliderect(redbat.bat.rect):
        ball.collision(redbat.bat)

    if ball.rect.colliderect(bluebat.bat.rect):
       ball.collision(bluebat.bat)


    #boundary check
    if ball.position.x > WALLRIGHTBOUNDARY: #820 is the right edge of the screen
        bluebat.bat.score+=1
        ball.restart()
    if ball.position.x < WALLLEFTBOUNDARY:
        redbat.bat.score+=1
        ball.restart()

    # to end the game loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False



    #keyboard input for bats
    keys = pygame.key.get_pressed()

    # for bludebat w,s (now it is controlled by the nn)
    # if keys[pygame.K_w]:
    #     if bluebat.rect.y > BATUPBOUNDARY:
    #         bluebat.rect.y-=BATSENSITIVITY
    # if keys[pygame.K_s]:
    #     if bluebat.rect.y < BATDOWNBOUNDARY:
    #         bluebat.rect.y+=BATSENSITIVITY

    bluebat_inputs = [ball.position.x,ball.position.y,ball.velocity.x,ball.velocity.y,bluebat.bat.rect.x,bluebat.bat.rect.y]
    bluebat_decision = bluebat.brain.forward(bluebat_inputs)
    if bluebat_decision == 1:
        if bluebat.bat.rect.y > BATUPBOUNDARY:
            bluebat.bat.rect.y-=BATSENSITIVITY
    elif bluebat_decision == 2:
        if bluebat.bat.rect.y < BATDOWNBOUNDARY:
            bluebat.bat.rect.y+=BATSENSITIVITY

    #for red bat (now it is controlled by the nn)
    # if keys[pygame.K_UP]:
    #     if redbat.rect.y > BATUPBOUNDARY:
    #         redbat.rect.y-=BATSENSITIVITY
    # if keys[pygame.K_DOWN]:
    #     if redbat.rect.y < BATDOWNBOUNDARY:
    #         redbat.rect.y+=BATSENSITIVITY


    # neural network decision making section
    redbat_inputs = [ball.position.x,ball.position.y,ball.velocity.x,ball.velocity.y,redbat.bat.rect.x,redbat.bat.rect.y]
    redbat_decision = redbat.brain.forward(redbat_inputs)
    if redbat_decision == 1:
        if redbat.bat.rect.y > BATUPBOUNDARY:
            redbat.bat.rect.y-=BATSENSITIVITY
    elif redbat_decision == 2:
        if redbat.bat.rect.y < BATDOWNBOUNDARY:
            redbat.bat.rect.y+=BATSENSITIVITY
    
    pygame.display.flip()
    delta_time = clock.tick(60)/1000
    delta_time = max(0.001, min(0.1, delta_time))


pygame.quit()