import pygame
from config import Config
from nn_comp import NeuralNetwork
from game_comp import PaddleCreature,Ball,Bat,text
from ui_comp import timerDisplay, scoreBoard, centerLine

pygame.init()

#window config
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 700

# WINDOW_WIDTH = 800
# WINDOW_HEIGHT = 400

# WINDOW_WIDTH = 150
# WINDOW_HEIGHT = 100

#creating window
config = Config(WINDOW_WIDTH,WINDOW_HEIGHT)
screen = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
pygame.display.set_caption("Pong Ai") 

#creating clock to control the rendering
clock = pygame.time.Clock()

# game loop
running = True
delta_time = 0.1

# Bat objects
bluebat = PaddleCreature(
    0, WINDOW_HEIGHT // 2 - config.BAT_HEIGHT // 2,
    screen, (0, 100, 255), config.BAT_WIDTH, config.BAT_HEIGHT
)

redbat = PaddleCreature(
    WINDOW_WIDTH - config.BAT_WIDTH,
    WINDOW_HEIGHT // 2 - config.BAT_HEIGHT // 2,
    screen, (255, 50, 50), config.BAT_WIDTH, config.BAT_HEIGHT
)

#redbat.brain.weights_load("goodredbat.npz") # here the trained weights will get loaded

# Ball object
ball = Ball(
    config.CENTER_X,
    config.CENTER_Y,
    screen, config.BALL_SPEED, config.BALL_RADIUS
)

frame = 0
hour = 0 
minute = 0
sec = 0
t_time = 0

while running:
    #screen.fill((0,0,0)) #fills the window with the rgb color for each iteration
    screen.fill((0, 0, 0))  # Black background

    centerLine(screen=screen,config=config)
    scoreBoard(screen=screen,player1=bluebat,player2=redbat,config=config)

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
    timerDisplay(screen=screen,formatted_time=formatted_time,config=config)
    
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

    ball.velocityconst = ball.velocityconst * config.BALL_SPEED_SCALE
    ball.velocity_update()


    ball.draw()
    ball.update()
    if ball.position.y > config.WALL_BOTTOM_BOUNDARY or ball.position.y < config.WALL_TOP_BOUNDARY: # 425 is the buttom edge of the wall
        ball.wallcollision()


    redbat.bat.draw()
    bluebat.bat.draw()    

    # collision between ball and bat
    if ball.rect.colliderect(redbat.bat.rect):
        ball.paddlecollision(redbat.bat)

    if ball.rect.colliderect(bluebat.bat.rect):
       ball.paddlecollision(bluebat.bat)


    #boundary check
    if ball.position.x > config.WALL_RIGHT_BOUNDARY: #820 is the right edge of the screen
        bluebat.bat.score+=1
        ball.restart()
    if ball.position.x < config.WALL_LEFT_BOUNDARY:
        redbat.bat.score+=1
        ball.restart()

    # to end the game loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False



    #keyboard input for bats
    keys = pygame.key.get_pressed()

    #for bludebat w,s 
    if keys[pygame.K_w]:
        if bluebat.bat.rect.y > config.BAT_TOP_BOUNDARY:
            bluebat.bat.rect.y-=config.BAT_SENSITIVITY
    elif keys[pygame.K_s]:
        if bluebat.bat.rect.y < config.BAT_BOTTOM_BOUNDARY:
            bluebat.bat.rect.y+=config.BAT_SENSITIVITY

    # bluebat_inputs = [ball.position.x,ball.position.y,ball.velocity.x,ball.velocity.y,bluebat.bat.rect.x,bluebat.bat.rect.y]
    # bluebat_decision = bluebat.brain.forward(bluebat_inputs)
    # if bluebat_decision == 1:
    #     if bluebat.bat.rect.y > config.BAT_TOP_BOUNDARY:
    #         bluebat.bat.rect.y-=config.BAT_SENSITIVITY
    # elif bluebat_decision == 2:
    #     if bluebat.bat.rect.y < config.BAT_BOTTOM_BOUNDARY:
    #         bluebat.bat.rect.y+=config.BAT_SENSITIVITY

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
        if redbat.bat.rect.y > config.BAT_TOP_BOUNDARY:
            redbat.bat.rect.y-=config.BAT_SENSITIVITY
    elif redbat_decision == 2:
        if redbat.bat.rect.y < config.BAT_BOTTOM_BOUNDARY:
            redbat.bat.rect.y+=config.BAT_SENSITIVITY
    
    pygame.display.flip()
    
    delta_time = clock.tick(60)/1000
    delta_time = max(0.001, min(0.1, delta_time))


pygame.quit()