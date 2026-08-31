import pygame

#Asset created by Esoe B.Studios.

pygame.init()

#creating window
screen = pygame.display.set_mode((802, 455))
pygame.display.set_caption("Pong Reimgined")

#creating clock to control the renderig
clock = pygame.time.Clock()

#adding game assets
board = pygame.image.load('./assets/Board.png').convert()
ball = pygame.image.load('./assets/Ball.png').convert()
redbat = pygame.image.load('./assets/redbat.png').convert()
bluebat = pygame.image.load('./assets/bluebat.png').convert()

# game loop
running = True

x = 401

delta_time = 0.1


# bats coordinates
bb_x = 0 #bluebat home position (0,180)
bb_y = 180

rb_x = 785 #redbat home position (785,180)
rb_y = 180 


while running:

    #screen.fill((0,0,0)) #fills the window with the rgb color for each iteration
    screen.blit(board)



    #screen.blit(ball, (x,30))

    screen.blit(ball, (385,210)) #ball home position (385,210)

    x += 50 * delta_time

    screen.blit(bluebat,(bb_x,bb_y)) #bluebat home position (0,180)
    screen.blit(redbat,(rb_x,rb_y)) #redbat home position (785,180)
    


    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False


    

    #keyboard input for bats
    keys = pygame.key.get_pressed()
    # for bludebat w,s
    if keys[pygame.K_w]:
        bb_y-=10
    if keys[pygame.K_s]:
        bb_y+=10

    #for red bat
    if keys[pygame.K_UP]:
        rb_y-=10
    if keys[pygame.K_DOWN]:
        rb_y+=10


    pygame.display.flip()
    delta_time = clock.tick(60)/1000
    delta_time = max(0.001, min(0.1, delta_time))

# any graphical element such as images is called surface

pygame.quit()