import pygame
import random

#ball
class Ball():
    def __init__(self,screen):
        self.look = pygame.image.load('./assets/Ball.png').convert()
        self.rect = self.look.get_rect()
        self.rect.x = 385
        self.rect.y = 210
        self.velocity_x = random.randint(-5,5)
        self.velocity_y = random.randint(-5,5)
        self.screen = screen

    def draw(self):
        self.screen.blit(self.look, (self.rect.x,self.rect.y))

    
    def update_coor(self):
        self.rect.x = self.rect.x + self.velocity_x
        self.rect.y = self.rect.y + self.velocity_y
    
    def change_velocity(self):
        if self.rect.y > 425 or self.rect.y < 0:
            self.velocity_y= -self.velocity_y
    def collision(self):
        self.velocity_x= -self.velocity_x


        

#bat
class Bat():
    def __init__(self, x, y, screen, look):
        self.screen = screen
        self.look = look
        self.rect = self.look.get_rect()
        self.rect.x = x
        self.rect.y = y
    def draw(self):
        self.screen.blit(self.look, (self.rect.x,self.rect.y))