import pygame
from nn_comp import NeuralNetwork
from game_comp import PaddleCreature,Ball,Bat,text
from ui_comp import timerDisplay, scoreBoard, centerLine

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

WALLUPBOUNDARY = 0
WALLDOWNBOUNDARY = 435

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

    centerLine(screen=screen)
    scoreBoard(screen=screen,player1=bluebat,player2=redbat)

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
    timerDisplay(screen=screen,formatted_time=formatted_time)

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
    if ball.position.y > WALLDOWNBOUNDARY or ball.position.y < WALLUPBOUNDARY: # 425 is the buttom edge of the wall
        ball.wallcollision()


    redbat.bat.draw()
    bluebat.bat.draw()    

    # collision between ball and bat
    if ball.rect.colliderect(redbat.bat.rect):
        ball.paddlecollision(redbat.bat)

    if ball.rect.colliderect(bluebat.bat.rect):
       ball.paddlecollision(bluebat.bat)


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