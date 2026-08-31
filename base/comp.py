import pygame

#ball
class Ball():
    def __init__(self,screen):
        self.x = 385
        self.y = 210
        self.look = pygame.image.load('./assets/Ball.png').convert()
        self.screen = screen
    def draw(self):
        self.screen.blit(self.look, (self.x,self.y))
#bat

class Bat():
    def __init__(self, x, y, screen, look):
        self.x = x
        self.y = y
        self.screen = screen
        self.look = look
    def draw(self):
        self.screen.blit(self.look, (self.x,self.y))