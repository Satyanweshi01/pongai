import pygame
from utils import Ball,Bat,text
#from nn import neural_network
from nn_class import NeuralNetwork

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
bluebat = Bat(0, 180, screen, (0, 100, 255), 20, 100) #bluebat home position (0,180)
redbat = Bat(785, 180, screen, (255, 50, 50), 20, 100) #redbat home position (785,180)

#config variables
BATSENSITIVITY = 15
BATUPBOUNDARY = 0
BATDOWNBOUNDARY = 346

WALLLEFTBOUNDARY = -20
WALLRIGHTBOUNDARY = 820
velocityconst = 5 # initial velocity

# ball object 
ball = Ball(385, 210, screen,velocityconst, 10)

# neural network object
nn1 = NeuralNetwork()
nn2 = NeuralNetwork()

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
    text(f"{bluebat.score:02}", screen, (0, 240, 255),
     290, 29, font="Arial", size=20, bold=True)

    text(f"{redbat.score:02}", screen, (255, 80, 95),
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


    redbat.draw()
    bluebat.draw()    

    # collision between ball and bat
    if ball.rect.colliderect(redbat.rect):
        ball.collision(redbat.rect)

    if ball.rect.colliderect(bluebat.rect):
       ball.collision(bluebat.rect)


    #boundary check
    if ball.position.x > WALLRIGHTBOUNDARY: #820 is the right edge of the screen
        bluebat.score+=1
        ball.restart()
    if ball.position.x < WALLLEFTBOUNDARY:
        redbat.score+=1
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

    nn1_inputs = [ball.position.x,ball.position.y,ball.velocity.x,ball.velocity.y,bluebat.rect.x,bluebat.rect.y]
    nn1_decision = nn1.forward(nn1_inputs)
    if nn1_decision == 1:
        if bluebat.rect.y > BATUPBOUNDARY:
            bluebat.rect.y-=BATSENSITIVITY
    elif nn1_decision == 2:
        if bluebat.rect.y < BATDOWNBOUNDARY:
            bluebat.rect.y+=BATSENSITIVITY

    #for red bat (now it is controlled by the nn)
    # if keys[pygame.K_UP]:
    #     if redbat.rect.y > BATUPBOUNDARY:
    #         redbat.rect.y-=BATSENSITIVITY
    # if keys[pygame.K_DOWN]:
    #     if redbat.rect.y < BATDOWNBOUNDARY:
    #         redbat.rect.y+=BATSENSITIVITY


    # neural network decision making section
    # nn_decision = neural_network([ball.position.x,ball.position.y,ball.velocity.x,ball.velocity.y,redbat.rect.x,redbat.rect.y])
    nn2_inputs = [ball.position.x,ball.position.y,ball.velocity.x,ball.velocity.y,redbat.rect.x,redbat.rect.y]
    nn2_decision = nn2.forward(nn2_inputs)
    if nn2_decision == 1:
        if redbat.rect.y > BATUPBOUNDARY:
            redbat.rect.y-=BATSENSITIVITY
    elif nn2_decision == 2:
        if redbat.rect.y < BATDOWNBOUNDARY:
            redbat.rect.y+=BATSENSITIVITY
    
    pygame.display.flip()
    delta_time = clock.tick(60)/1000
    delta_time = max(0.001, min(0.1, delta_time))


pygame.quit()