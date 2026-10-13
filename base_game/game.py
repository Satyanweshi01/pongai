import pygame
from utils import Ball,Bat,text

#Asset created by Esoe B.Studios.

pygame.init()

#creating window
screen = pygame.display.set_mode((802, 455))
pygame.display.set_caption("Pong Ai") 

#creating clock to control the rendering
clock = pygame.time.Clock()

#adding game assets
board = pygame.image.load('./assets/Board.png').convert()
board_rect = board.get_rect()

# game loop
running = True

delta_time = 0.1


# bat objects
bluebat_img = pygame.image.load('./assets/bluebat.png').convert()
redbat_img = pygame.image.load('./assets/redbat.png').convert()

bluebat = Bat(0, 180, screen, bluebat_img) #bluebat home position (0,180)
redbat = Bat(785, 180, screen, redbat_img) #redbat home position (785,180)

# ball object 
ball_img = pygame.image.load('./assets/Ball.png').convert()
ball = Ball(385, 210, screen, ball_img)


 
frame = 0
hour = 0 
minute = 0
sec = 0
t_time = 0

while running:
    #screen.fill((0,0,0)) #fills the window with the rgb color for each iteration
    screen.blit(board)

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
    if ball.position.x > 820: #800 is the left edge of the screen
        bluebat.score+=1
        ball.restart()
    if ball.position.x < -20:
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
        if bluebat.rect.y > 0:
            bluebat.rect.y-=10
    if keys[pygame.K_s]:
        if bluebat.rect.y < 331:
            bluebat.rect.y+=10

    #for red bat
    if keys[pygame.K_UP]:
        if redbat.rect.y > 0:
            redbat.rect.y-=10
    if keys[pygame.K_DOWN]:
        if redbat.rect.y < 331:
            redbat.rect.y+=10

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

    pygame.display.flip()
    delta_time = clock.tick(60)/1000
    delta_time = max(0.001, min(0.1, delta_time))


pygame.quit()