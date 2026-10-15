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
    def __init__(self,x,y,screen,velocityconst,radius):
        super().__init__(x,y)
        self.velocityconst = velocityconst
        self.radius = radius
        self.rect = pygame.Rect(
            x, y,
            self.radius * 2,
            self.radius * 2
        )
        self.velocity.x = random.choice([-self.velocityconst,self.velocityconst])
        self.velocity.y = random.choice([-self.velocityconst,self.velocityconst])
        self.startingpos_x = x
        self.startingpos_y = y
        self.rect.x = x
        self.rect.y = y
        self.screen = screen

    def draw(self):
        self.rect.x = round(self.position.x)
        self.rect.y = round(self.position.y)

        pygame.draw.circle(
            self.screen,
            (255, 255, 255),
            self.rect.center,
            self.radius
        )
    
    def change_velocity(self): # for wall collision detection
        WALLUPBOUNDARY = 0
        WALLDOWNBOUNDARY = 435

        if self.position.y > WALLDOWNBOUNDARY or self.position.y < WALLUPBOUNDARY: # 425 is the buttom edge of the wall
            self.velocity.y = -self.velocity.y

    
    def collision(self,bat): # for bat collision detection
        OFFSET = 10
        if bat.centerx > self.rect.centerx: # bat in the right
            if self.velocity.x > 0:
                self.position.x = self.position.x - OFFSET
                self.velocity.x= -self.velocity.x
        elif bat.centerx < self.rect.centerx: # bat in the left
            if self.velocity.x < 0:
                self.position.x = self.position.x + OFFSET
                self.velocity.x= -self.velocity.x
    def velocity_update(self):
        unit_vec = self.velocity.normalize()
        self.velocity = Vectorcls.multi(unit_vec,self.velocityconst)
    
    def restart(self):
        #print(self.startingpos_x,self.startingpos_y)
        self.position.x = self.startingpos_x
        self.position.y = self.startingpos_y
        self.velocity.x = random.choice([-self.velocityconst,self.velocityconst])
        self.velocity.y = random.choice([-self.velocityconst,self.velocityconst])

#bat
class Bat():
    def __init__(self, x, y, screen, color, width, height):
        self.color = color
        self.screen = screen
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x, y, width, height)
        self.score = 0
    def draw(self):
        pygame.draw.rect(
            self.screen,
            self.color,
            self.rect
        )


def text(string, screen, text_color, x, y,
         font="Arial", size=20, bold=False):

    font_obj = pygame.font.SysFont(font, size, bold=bold)
    img = font_obj.render(string, True, text_color)
    screen.blit(img, (x, y))