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


while running:

    #screen.fill((0,0,0)) #fills the window with the rgb color for each iteration
    screen.blit(board)



    #screen.blit(ball, (x,30))

    screen.blit(ball, (385,210)) # home position (385,210)

    x += 50 * delta_time




    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False





    pygame.display.flip()
    delta_time = clock.tick(60)/1000
    delta_time = max(0.001, min(0.1, delta_time))

# any graphical element such as images is called surface

pygame.quit()