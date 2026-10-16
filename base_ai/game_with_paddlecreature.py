import pygame
from nn_comp import NeuralNetwork
from game_comp import PaddleCreature,Ball,Bat,text
from ui_comp import timerDisplay, scoreBoard, centerLine

pygame.init()

#window config
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 700

#creating window
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Pong Ai") 

#creating clock to control the rendering
clock = pygame.time.Clock()

# game loop
running = True
delta_time = 0.1

#config variables
BAT_WIDTH = 20
BAT_HEIGHT = 100
BAT_SENSITIVITY = 15

BAT_UP_BOUNDARY = 0
BAT_DOWN_BOUNDARY = WINDOW_HEIGHT - BAT_HEIGHT

WALL_LEFT_BOUNDARY = -20
WALL_RIGHT_BOUNDARY = WINDOW_WIDTH 

WALL_UP_BOUNDARY = 0
WALL_DOWN_BOUNDARY = WINDOW_HEIGHT 

velocityconst = 5 # initial velocity

# Bat objects
bluebat = PaddleCreature(
    0, WINDOW_HEIGHT // 2 - BAT_HEIGHT // 2,
    screen, (0, 100, 255), BAT_WIDTH, BAT_HEIGHT
)

redbat = PaddleCreature(
    WINDOW_WIDTH - BAT_WIDTH,
    WINDOW_HEIGHT // 2 - BAT_HEIGHT // 2,
    screen, (255, 50, 50), BAT_WIDTH, BAT_HEIGHT
)

# Ball object
ball = Ball(
    WINDOW_WIDTH // 2 - 10,
    WINDOW_HEIGHT // 2 - 10,
    screen, velocityconst, 10
)

frame = 0
hour = 0 
minute = 0
sec = 0
t_time = 0

while running:
    #screen.fill((0,0,0)) #fills the window with the rgb color for each iteration
    screen.fill((0, 0, 0))  # Black background

    centerLine(screen=screen,centerx=WINDOW_WIDTH//2,height=WINDOW_HEIGHT)
    scoreBoard(screen=screen,player1=bluebat,player2=redbat,width=WINDOW_WIDTH,height=WINDOW_WIDTH)

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
    timerDisplay(screen=screen,formatted_time=formatted_time,width=WINDOW_WIDTH)

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


    ball.draw()
    ball.update()
    if ball.position.y > WALL_DOWN_BOUNDARY or ball.position.y < WALL_UP_BOUNDARY: # 425 is the buttom edge of the wall
        ball.wallcollision()


    redbat.bat.draw()
    bluebat.bat.draw()    

    # collision between ball and bat
    if ball.rect.colliderect(redbat.bat.rect):
        ball.paddlecollision(redbat.bat)

    if ball.rect.colliderect(bluebat.bat.rect):
       ball.paddlecollision(bluebat.bat)


    #boundary check
    if ball.position.x > WALL_RIGHT_BOUNDARY: #820 is the right edge of the screen
        bluebat.bat.score+=1
        ball.restart()
    if ball.position.x < WALL_LEFT_BOUNDARY:
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
        if bluebat.bat.rect.y > BAT_UP_BOUNDARY:
            bluebat.bat.rect.y-=BAT_SENSITIVITY
    elif bluebat_decision == 2:
        if bluebat.bat.rect.y < BAT_DOWN_BOUNDARY:
            bluebat.bat.rect.y+=BAT_SENSITIVITY

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
        if redbat.bat.rect.y > BAT_UP_BOUNDARY:
            redbat.bat.rect.y-=BAT_SENSITIVITY
    elif redbat_decision == 2:
        if redbat.bat.rect.y < BAT_DOWN_BOUNDARY:
            redbat.bat.rect.y+=BAT_SENSITIVITY
    
    pygame.display.flip()
    
    delta_time = clock.tick(60)/1000
    delta_time = max(0.001, min(0.1, delta_time))


pygame.quit()