import pygame
from random import choice,random
from config import Config
from nn_comp import NeuralNetwork
from game_comp import PaddleCreature,Ball,Bat,text
from ui_comp import timerDisplay, scoreBoard, centerLine

pygame.init()

#window config
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 700

# WINDOW_WIDTH = 800
# WINDOW_HEIGHT = 400

# WINDOW_WIDTH = 150
# WINDOW_HEIGHT = 100

#creating window
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Pong Ai Training") 

#creating clock to control the rendering
clock = pygame.time.Clock()

# game loop
running = True
delta_time = 0.1

class GameInstance:
    """each of the gameinstance object has a redbat to train and each of the redbat has brain which is a neural network object
    Here that neural network is the DNA I have to work with.
    """
    def __init__(self,width,height,screen):
        self.config = Config(width,height)#Config(650,350)
        self.screen = screen

        # Bat objects
        self.bluebat = PaddleCreature(
            0, self.config.WINDOW_HEIGHT // 2 - self.config.BAT_HEIGHT // 2,
            self.screen, (0, 100, 255), self.config.BAT_WIDTH, self.config.BAT_HEIGHT
        )
        self.bluebat.brain.weights_load("./weights/goodbluebat.npz") # static weight load  

        self.redbat = PaddleCreature(
            self.config.WINDOW_WIDTH - self.config.BAT_WIDTH,
            self.config.WINDOW_HEIGHT // 2 - self.config.BAT_HEIGHT // 2,
            self.screen, (255, 50, 50), self.config.BAT_WIDTH, self.config.BAT_HEIGHT
        )
        self.fitness = 0
        # Ball object
        self.ball = Ball(
            self.config.CENTER_X,
            self.config.CENTER_Y,
            self.screen, self.config.BALL_SPEED, self.config.BALL_RADIUS
        )
    def fitness_cal(self):
        self.fitness = self.redbat.fitness_cal()
        return self.fitness
    def gamestate_update(self):
        self.frame = 0
        self.hour = 0 
        self.minute = 0
        self.sec = 0
        self.t_time = 0

        centerLine(screen=self.screen,config=self.config)
        # scoreBoard(screen=self.screen,player1=self.bluebat,player2=self.redbat,config=self.config)

        # time update
        self.frame += 1
        if self.frame == 60:
            self.sec += 1
            self.t_time += 1
            self.frame = 0
        if self.sec == 60:
            self.minute += 1
            self.sec = 0
        if self.minute == 60:
            self.hour += 1
            self.minute = 0
        # formatted_time = f"{self.hour:02}:{self.minute:02}:{self.sec:02}"
        # timerDisplay(screen=self.screen,formatted_time=formatted_time,config=self.config)

        # speed dynamism
        if self.t_time < 30:
            self.ball.velocityconst = 5 
        elif self.t_time < 60:
            self.ball.velocityconst = 7 
        elif self.t_time < 120:
            self.ball.velocityconst = 9
        elif self.t_time < 180:
            self.ball.velocityconst = 11
        elif self.t_time < 300:
            self.ball.velocityconst = 13
        else:
            self.ball.velocityconst = 15

        self.ball.velocityconst = self.ball.velocityconst * self.config.BALL_SPEED_SCALE
        self.ball.velocity_update()


        self.ball.draw()
        self.ball.update()
        if self.ball.position.y > self.config.WALL_BOTTOM_BOUNDARY or self.ball.position.y < self.config.WALL_TOP_BOUNDARY: # 425 is the buttom edge of the wall
            self.ball.wallcollision()


        self.redbat.bat.draw()
        self.bluebat.bat.draw()    

        # collision between ball and bat
        if self.ball.rect.colliderect(self.redbat.bat.rect):
            self.ball.paddlecollision(self.redbat.bat)

        if self.ball.rect.colliderect(self.bluebat.bat.rect):
            self.ball.paddlecollision(self.bluebat.bat)


        #boundary check
        if self.ball.position.x > self.config.WALL_RIGHT_BOUNDARY: #820 is the right edge of the screen
            self.bluebat.bat.score+=1
            self.ball.restart()
        if self.ball.position.x < self.config.WALL_LEFT_BOUNDARY:
            self.redbat.bat.score+=1
            self.ball.restart()

        # neural network decision making section
        bluebat_inputs = [self.ball.position.x,self.ball.position.y,self.ball.velocity.x,self.ball.velocity.y,self.bluebat.bat.rect.x,self.bluebat.bat.rect.y]
        bluebat_decision = self.bluebat.brain.forward(bluebat_inputs)
        if bluebat_decision == 1:
            if self.bluebat.bat.rect.y > self.config.BAT_TOP_BOUNDARY:
                self.bluebat.bat.rect.y-=self.config.BAT_SENSITIVITY
        elif bluebat_decision == 2:
            if self.bluebat.bat.rect.y < self.config.BAT_BOTTOM_BOUNDARY:
                self.bluebat.bat.rect.y+=self.config.BAT_SENSITIVITY

        
        redbat_inputs = [self.ball.position.x,self.ball.position.y,self.ball.velocity.x,self.ball.velocity.y,self.redbat.bat.rect.x,self.redbat.bat.rect.y]
        redbat_decision = self.redbat.brain.forward(redbat_inputs)
        if redbat_decision == 1:
            if self.redbat.bat.rect.y > self.config.BAT_TOP_BOUNDARY:
                self.redbat.bat.rect.y-=self.config.BAT_SENSITIVITY
        elif redbat_decision == 2:
            if self.redbat.bat.rect.y < self.config.BAT_BOTTOM_BOUNDARY:
                self.redbat.bat.rect.y+=self.config.BAT_SENSITIVITY
    def crossover(ParentA:GameInstance,ParentB:GameInstance):
        child = GameInstance(1200,700)

        child.redbat.brain.hiddenlayer1.weights = choice([ParentA.redbat.brain.hiddenlayer1.weights,ParentB.redbat.brain.hiddenlayer1.weights])
        child.redbat.brain.hiddenlayer1.biases = choice([ParentA.redbat.brain.hiddenlayer1.biases,ParentB.redbat.brain.hiddenlayer1.biases])
        child.redbat.brain.outputlayer.weights = choice([ParentA.redbat.brain.outputlayer1.weights,ParentB.redbat.brain.outputlayer1.weights])
        child.redbat.brain.outputlayer.biases = choice([ParentA.redbat.brain.outputlayer1.biases,ParentB.redbat.brain.outputlayer1.biases])
        return child
    def mutate(self,mutation_rate):
        for array in [self.redbat.brain.hiddenlayer1.weights,self.redbat.brain.hiddenlayer1.biases,self.redbat.brain.outputlayer.weights,self.redbat.brain.outputlayer.biases]:
            for element in range(len(array)):
                prob = random()
                if prob <= mutation_rate:
                    array[element] += array[element]*choice([+mutation_rate,-mutation_rate])

class GATraining:
    def __init__(self,population_size:int,mutation_rate:int):
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.gameinstances = []
        for i in range(population_size):
            self.gameinstances.append(GameInstance(1200,700,screen))
    
    def fitness_cal(self):
        # this calculates the fitness of the gameinstances by judging it's redbat Paddlecreature 
        total_fitness = 0
        for gameinstance in self.gameinstances:
            total_fitness += gameinstance.fitness_cal()
        # now calculating normalized fitness
        for gameinstance in self.gameinstances:
            gameinstance.fitness = gameinstance.fitness/total_fitness
            print(gameinstance.fitness)
        
    def selection(self):
        childgameinstances = []
        self.fitness_cal()
        for _ in range(self.population_size):
            def get_parent():
                while True:
                    parent = choice(self.gameinstances)
                    prob = random()
                    if prob<=parentA.fitness:
                        return parent
            ParentA = get_parent()
            ParentB = get_parent()
            child = GameInstance.crossover(ParentA,ParentB)
            child.mutate(self.mutation_rate)
            childgameinstances.append(child)

        # after selection
        self.gameinstances = childgameinstances
    def reproduction(self):
        pass

while running:
    # to end the game loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((0, 0, 0))  


    
    pygame.display.flip()
    
    delta_time = clock.tick(60)/1000
    delta_time = max(0.001, min(0.1, delta_time))


pygame.quit()