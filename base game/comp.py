import pygame
import random

#ball
class Ball():
    def __init__(self,screen):
        self.look = pygame.image.load('./assets/Ball.png').convert()
        self.rect = self.look.get_rect()
        self.rect.x = 385 # middle position of ball
        self.rect.y = 210
        self.velocity_x = random.choice([-5,5])
        self.velocity_y = random.choice([-5,5])
        self.screen = screen

    def draw(self):
        self.screen.blit(self.look, (self.rect.x,self.rect.y))

    def update_coor(self):
        self.rect.x = self.rect.x + self.velocity_x
        self.rect.y = self.rect.y + self.velocity_y
    
    def change_velocity(self): # for wall collision detection
        if self.rect.y > 425 or self.rect.y < 0: # 425 is the buttom edge of the wall
            self.velocity_y= -self.velocity_y

    def collision(self,bat): # for bat collision detection
        if bat.centerx > self.rect.centerx: # bat in the right
            if self.velocity_x > 0:
                self.velocity_x= -self.velocity_x
        elif bat.centerx < self.rect.centerx: # bat in the left
            if self.velocity_x < 0:
                self.velocity_x= -self.velocity_x

    def reload(self):
        self.rect.x = 385
        self.rect.y = 210
        self.velocity_x = random.choice([-5,5])
        self.velocity_y = random.choice([-5,5])

#bat
class Bat():
    def __init__(self, x, y, screen, look):
        self.screen = screen
        self.look = look
        self.rect = self.look.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.score = 0
    def draw(self):
        self.screen.blit(self.look, (self.rect.x,self.rect.y))



def text(string,screen, text_color, x, y):
    font = pygame.font.SysFont("Arial", 30)
    img = font.render(string, True, text_color)
    screen.blit(img,(x,y))
