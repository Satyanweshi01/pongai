import pygame
from utils import Ball,Bat,text

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
BATDOWNBOUNDARY = 350

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
    pygame.draw.line(
                    screen,
                    (255, 255, 255),
                    (401, 0),
                    (401, 455),
                    2
        )

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
    formatted_time = f"{hour}:{minute}:{sec}"  
    text(str(formatted_time),screen,(255,255,255),385,0)
    #print(formatted_time)

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

    #scoreboard printing
    text(str(bluebat.score),screen,(255,255,255),200,0)
    text(str(redbat.score),screen,(255,255,255),600,0)

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
    # for bludebat w,s
    if keys[pygame.K_w]:
        if bluebat.rect.y > BATUPBOUNDARY:
            bluebat.rect.y-=BATSENSITIVITY
    if keys[pygame.K_s]:
        if bluebat.rect.y < BATDOWNBOUNDARY:
            bluebat.rect.y+=BATSENSITIVITY

    #for red bat
    if keys[pygame.K_UP]:
        if redbat.rect.y > BATUPBOUNDARY:
            redbat.rect.y-=BATSENSITIVITY
    if keys[pygame.K_DOWN]:
        if redbat.rect.y < BATDOWNBOUNDARY:
            redbat.rect.y+=BATSENSITIVITY


    

    pygame.display.flip()
    delta_time = clock.tick(60)/1000
    delta_time = max(0.001, min(0.1, delta_time))


pygame.quit()