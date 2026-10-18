import math
import random
import pygame
from nn_comp import NeuralNetwork


class Vectorcls():
    def __init__(self,x,y):
        self.x = x
        self.y = y

    def add(vec1,vec2):
        vecx = vec1.x+vec2.x
        vecy = vec1.y+vec2.y
        return Vectorcls(vecx,vecy)
        
    def sub(vec1,vec2):
        vecx = vec1.x-vec2.x
        vecy = vec1.y-vec2.y
        return Vectorcls(vecx,vecy)

    def multi(vec1,scalar):
        vecx = vec1.x*scalar
        vecy = vec1.y*scalar
        return Vectorcls(vecx,vecy)

    def div(vec1,scalar):
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
    
    def dot(a, b):
        denom = a.mag() * b.mag()
        if denom == 0:
            return 0.0
        val = max(-1.0, min(1.0, (a.x * b.x + a.y * b.y) / denom))
        return math.acos(val)

    def angle(self):
        return math.atan2(self.y, self.x)

    def setDir(a,angle): # absolute direction change, it is like assigning new direction with same magnitude
        mag = a.mag()
        x = mag*math.cos(angle)
        y = mag*math.sin(angle)
        return Vectorcls(x,y)

    def rotate(a,angle):
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
        self.startingpos_x = x
        self.startingpos_y = y
        self.rect.x = x
        self.rect.y = y
        self.screen = screen

        # Random serve angle between -35 and +35 degrees
        serve_angle = random.uniform(-math.pi / 5, math.pi / 5)
        direction = random.choice([-1.0, 1.0])
        self.velocity.x = direction * self.velocityconst * math.cos(serve_angle)
        self.velocity.y = self.velocityconst * math.sin(serve_angle)

    def draw(self):
        self.rect.x = round(self.position.x)
        self.rect.y = round(self.position.y)

        pygame.draw.circle(
            self.screen,
            (255, 255, 255),
            self.rect.center,
            self.radius
        )
    
    def wallcollision(self): # for wall collision detection
        self.velocity.y = -self.velocity.y

    
    def paddlecollision(self,bat): # for bat collision detection
        OFFSET = 10
        MAX_BOUNCE_ANGLE = 5 * math.pi / 18  # max 50 degrees deflection angle

        if bat.rect.centerx > self.rect.centerx: # bat on the right
            if self.velocity.x > 0:
                bat.collision += 1
                # preventing clipping
                self.position.x = min(self.position.x - OFFSET, bat.rect.left - self.radius * 2)
                self.rect.x = round(self.position.x)

                # Calculate deflection angle based on hit location relative to paddle center
                relative_y = self.rect.centery - bat.rect.centery
                half_height = max(1, bat.rect.height / 2)
                normalized_y = max(-1.0, min(1.0, relative_y / half_height))
                bounce_angle = normalized_y * MAX_BOUNCE_ANGLE

                speed = max(1.0, self.velocityconst)
                self.velocity.x = -abs(speed * math.cos(bounce_angle))
                self.velocity.y = speed * math.sin(bounce_angle)

        elif bat.rect.centerx < self.rect.centerx: # bat on the left
            if self.velocity.x < 0:
                bat.collision += 1
                self.position.x = max(self.position.x + OFFSET, bat.rect.right)
                self.rect.x = round(self.position.x)


                relative_y = self.rect.centery - bat.rect.centery
                half_height = max(1, bat.rect.height / 2)
                normalized_y = max(-1.0, min(1.0, relative_y / half_height))
                bounce_angle = normalized_y * MAX_BOUNCE_ANGLE

                speed = max(1.0, self.velocityconst)
                self.velocity.x = abs(speed * math.cos(bounce_angle))
                self.velocity.y = speed * math.sin(bounce_angle)

    def velocity_update(self):
        unit_vec = self.velocity.normalize()
        self.velocity = Vectorcls.multi(unit_vec,self.velocityconst)
    
    def restart(self):
        self.position.x = self.startingpos_x
        self.position.y = self.startingpos_y

        self.rect.x = round(self.position.x)
        self.rect.y = round(self.position.y)

        # Random serve angle between -35 and +35 degrees
        serve_angle = random.uniform(-math.pi / 5, math.pi / 5)
        direction = random.choice([-1.0, 1.0])
        speed = max(1.0, self.velocityconst)

        self.velocity.x = direction * speed * math.cos(serve_angle)
        self.velocity.y = speed * math.sin(serve_angle)

#bat
class Bat():
    def __init__(self, x, y, screen, color, width, height):
        self.color = color
        self.screen = screen
        self.width = width
        self.height = height
        self.collision = 0
        self.rect = pygame.Rect(x, y, width, height)
        self.score = 0
    def draw(self):
        pygame.draw.rect(
            self.screen,
            self.color,
            self.rect
        )
class GameInstance:
    pass

def text(string, screen, text_color, x, y,
         font="Arial", size=20, bold=False):

    font_obj = pygame.font.SysFont(font, size, bold=bold)
    img = font_obj.render(string, True, text_color)
    screen.blit(img, (x, y))

class PaddleCreature():
    def __init__(self, x, y, screen, color, width, height):
        self.brain = NeuralNetwork() # contains all the weights that will be modified during evolutionary training
        self.bat = Bat(x, y, screen, color, width, height) # contains details which needed for fitness function
        self.fitness = 0
