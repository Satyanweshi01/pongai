import math
import random
import pygame

class Vectorcls():
    def __init__(self,x,y):
        self.x = x
        self.y = y

    def add(vec1:Vectorcls,vec2:Vectorcls):
        vecx = vec1.x+vec2.x
        vecy = vec1.y+vec2.y
        return Vectorcls(vecx,vecy)
    def sub(vec1:Vectorcls,vec2:Vectorcls):
        vecx = vec1.x-vec2.x
        vecy = vec1.y-vec2.y
        return Vectorcls(vecx,vecy)
    def multi(vec1:Vectorcls,scalar):
        vecx = vec1.x*scalar
        vecy = vec1.y*scalar
        return Vectorcls(vecx,vecy)
    def div(vec1:Vectorcls,scalar):
        vecx = vec1.x/scalar
        vecy = vec1.y/scalar
        return Vectorcls(vecx,vecy)

    def limit(self,maxi):
        if self.mag() > maxi:
            scale = maxi/self.mag()
            self.x*=scale
            self.y*=scale

    def mag(self):
        return math.sqrt(self.x*self.x + self.y*self.y)
    
    def normalize(self):
        return Vectorcls.div(self,self.mag())
    
    def setMag(self,mag):
        vec = self.normalize()
        return Vectorcls.multi(vec,mag)
    
    def dot(a:Vectorcls,b:Vectorcls):
        angle = math.acos(((a.position.x * b.position.x)+(a.position.y*b.position.y))/a.mag()*b.mag())
        return angle

    def angle(self):
        return math.atan2(self.y, self.x)

    def setDir(a:Vectorcls,angle): # absolute direction change, it is like assigning new direction with same magnitude
        mag = a.mag()
        x = mag*math.cos(angle)
        y = mag*math.sin(angle)
        return Vectorcls(x,y)

    def rotate(a:Vectorcls,angle):
        curr_angle = a.angle()
        new_angle = curr_angle + angle
        return Vectorcls.setDir(a,new_angle)
    
    def random2d():
        vec = Vectorcls(1,1)
        angle = random.uniform(0,2*math.pi)
        vec = Vectorcls.setDir(vec,angle)
        vec.setMag(1)
        return vec


class Mover():
    def __init__(self,x,y):
        self.x =x
        self.y =y
        self.position = Vectorcls(x,y)
        self.velocity = Vectorcls(0,0)
        self.acceleration = Vectorcls(0,0)
        #self.mass = mass
        self.ap_forces = []
    def cal_acce(self):
        self.acceleration = Vectorcls.multi(self.acceleration,0)
        for i in self.ap_forces:
            #i = Vectorcls.div(i,self.mass)
            self.acceleration = Vectorcls.add(self.acceleration,i)
    def ap_force(self,force:Vectorcls):
        if force not in self.ap_forces:
            self.ap_forces.append(force)
    def update(self):
        self.velocity = Vectorcls.add(self.acceleration,self.velocity)
        self.position = Vectorcls.add(self.velocity,self.position)

#ball

class Ball(Mover):
    def __init__(self,x,y,screen,look):
        super().__init__(x,y)
        self.look = look
        self.rect = self.look.get_rect()
        self.velocity.x = random.choice([-3,3])
        self.velocity.y = random.choice([-3,3])
        self.startingpos_x = x
        self.startingpos_y = y
        self.rect.x = x
        self.rect.y = y
        self.screen = screen

    def draw(self):
        self.rect.x = self.position.x
        self.rect.y = self.position.y
        self.screen.blit(self.look, (self.rect.x,self.rect.y))
    
    def change_velocity(self): # for wall collision detection
        if self.position.y > 425 or self.position.y < 0: # 425 is the buttom edge of the wall
            self.velocity.y = -self.velocity.y

    
    def collision(self,bat): # for bat collision detection
        if bat.centerx > self.rect.centerx: # bat in the right
            if self.velocity.x > 0:
                self.velocity.x= -self.velocity.x
        elif bat.centerx < self.rect.centerx: # bat in the left
            if self.velocity.x < 0:
                self.velocity.x= -self.velocity.x

    
    def restart(self):
        #print(self.startingpos_x,self.startingpos_y)
        self.position.x = self.startingpos_x
        self.position.y = self.startingpos_y
        self.velocity.x = random.choice([-3,3])
        self.velocity.y = random.choice([-3,3])

# class Ball():
#     def __init__(self,screen):
#         self.look = pygame.image.load('./assets/Ball.png').convert()
#         self.rect = self.look.get_rect()
#         self.rect.x = 385 # middle position of ball
#         self.rect.y = 210
#         self.velocity_x = random.choice([-5,5])
#         self.velocity_y = random.choice([-5,5])
#         self.screen = screen

#     def draw(self):
#         self.screen.blit(self.look, (self.rect.x,self.rect.y))

#     def update_coor(self):
#         self.rect.x = self.rect.x + self.velocity_x
#         self.rect.y = self.rect.y + self.velocity_y
    
#     def change_velocity(self): # for wall collision detection
#         if self.rect.y > 425 or self.rect.y < 0: # 425 is the buttom edge of the wall
#             self.velocity_y= -self.velocity_y

#     def collision(self,bat): # for bat collision detection
#         if bat.centerx > self.rect.centerx: # bat in the right
#             if self.velocity_x > 0:
#                 self.velocity_x= -self.velocity_x
#         elif bat.centerx < self.rect.centerx: # bat in the left
#             if self.velocity_x < 0:
#                 self.velocity_x= -self.velocity_x

#     def reload(self):
#         self.rect.x = 385
#         self.rect.y = 210
#         self.velocity_x = random.choice([-5,5])
#         self.velocity_y = random.choice([-5,5])

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
    font = pygame.font.SysFont("Arial", 20)
    img = font.render(string, True, text_color)
    screen.blit(img,(x,y))