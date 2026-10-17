import pygame
import time
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import copy 
import numpy as np

from random import choice,random
from config import Config
from game_comp import PaddleCreature,Ball,Bat,text
from ui_comp import centerLine


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
        self.bluebat.brain.weights_load("./goodbluebat.npz") # static weight load  

        self.redbat = PaddleCreature(
            self.config.WINDOW_WIDTH - self.config.BAT_WIDTH,
            self.config.WINDOW_HEIGHT // 2 - self.config.BAT_HEIGHT // 2,
            self.screen, (255, 50, 50), self.config.BAT_WIDTH, self.config.BAT_HEIGHT
        )
        # Ball object
        self.ball = Ball(
            self.config.CENTER_X,
            self.config.CENTER_Y,
            self.screen, self.config.BALL_SPEED, self.config.BALL_RADIUS
        )

        self.fitness = 0
        self.raw_fitness = 0

        self.sim_frames = 0
        self.t_time = 0

    def fitness_cal(self):
        self.fitness = self.redbat.fitness_cal(self.bluebat.bat) # passing bluebat's bat as opponent
        return self.fitness

    def gamestate_update(self):
        # Advance this game's simulation clock
        self.sim_frames += 1
        self.t_time = self.sim_frames // 60

        # Dynamically increase ball speed
        if self.t_time < 3:
            speed = 5
        elif self.t_time < 6:
            speed = 7
        elif self.t_time < 12:
            speed = 9
        elif self.t_time < 18:
            speed = 11
        elif self.t_time < 30:
            speed = 13
        else:
            speed = 15

        self.ball.velocityconst = (
            speed * self.config.BALL_SPEED_SCALE
        )
        self.ball.velocity_update()

        # Update ball physics
        self.ball.update()

        if self.ball.position.y > self.config.WALL_BOTTOM_BOUNDARY or self.ball.position.y < self.config.WALL_TOP_BOUNDARY: # 425 is the buttom edge of the wall
            self.ball.wallcollision() 

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

        
        redbat_inputs = [ # sending normalized inputs to the redbat's neural network
            self.ball.position.x / self.config.WINDOW_WIDTH,
            self.ball.position.y / self.config.WINDOW_HEIGHT,
            self.ball.velocity.x / 15,
            self.ball.velocity.y / 15,
            self.redbat.bat.rect.x / self.config.WINDOW_WIDTH,
            self.redbat.bat.rect.y / self.config.WINDOW_HEIGHT
        ]
        redbat_decision = self.redbat.brain.forward(redbat_inputs)
        if redbat_decision == 1:
            if self.redbat.bat.rect.y > self.config.BAT_TOP_BOUNDARY:
                self.redbat.bat.rect.y-=self.config.BAT_SENSITIVITY
        elif redbat_decision == 2:
            if self.redbat.bat.rect.y < self.config.BAT_BOTTOM_BOUNDARY:
                self.redbat.bat.rect.y+=self.config.BAT_SENSITIVITY

    def draw(self):
        # This method is called ONLY for the AI being displayed
        centerLine(screen=self.screen, config=self.config)

        self.ball.draw()
        self.redbat.bat.draw()
        self.bluebat.bat.draw()
        
    def crossover(ParentA,ParentB,screen):
        child = GameInstance(1200,700,screen)

        child.redbat.brain.hiddenlayer1.weights = np.where(
            np.random.random(
                ParentA.redbat.brain.hiddenlayer1.weights.shape
            ) < 0.5,
            ParentA.redbat.brain.hiddenlayer1.weights,
            ParentB.redbat.brain.hiddenlayer1.weights
        ).copy()

        child.redbat.brain.hiddenlayer1.biases = np.where(
            np.random.random(
                ParentA.redbat.brain.hiddenlayer1.biases.shape
            ) < 0.5,
            ParentA.redbat.brain.hiddenlayer1.biases,
            ParentB.redbat.brain.hiddenlayer1.biases
        ).copy()

        child.redbat.brain.outputlayer.weights = np.where(
            np.random.random(
                ParentA.redbat.brain.outputlayer.weights.shape
            ) < 0.5,
            ParentA.redbat.brain.outputlayer.weights,
            ParentB.redbat.brain.outputlayer.weights
        ).copy()

        child.redbat.brain.outputlayer.biases = np.where(
            np.random.random(
                ParentA.redbat.brain.outputlayer.biases.shape
            ) < 0.5,
            ParentA.redbat.brain.outputlayer.biases,
            ParentB.redbat.brain.outputlayer.biases
        ).copy()

        return child
    def mutate(self,mutation_rate):
        for array in [self.redbat.brain.hiddenlayer1.weights,self.redbat.brain.hiddenlayer1.biases,self.redbat.brain.outputlayer.weights,self.redbat.brain.outputlayer.biases]:
            mask = np.random.random(array.shape) < mutation_rate
            array[mask] += np.random.normal(
                0, 0.1, size=np.count_nonzero(mask)
            )

class GATraining:
    def __init__(self,population_size:int,mutation_rate:int,screen,gameplay):
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.screen = screen
        self.gen = 0
        self.start = time.perf_counter()
        self.gameinstances = []
        for i in range(population_size):
            self.gameinstances.append(GameInstance(1200,700,screen))

        self.GAMEPLAY = gameplay

        self.generation_history = []
        self.average_fitness_history = []

        # Matplotlib interactive graph
        plt.ion()

        self.fig, self.ax = plt.subplots(figsize=(9, 5))
        self.line, = self.ax.plot([], [], "b-o", markersize=4)

        self.ax.set_title("Average Raw Fitness per Generation")
        self.ax.set_xlabel("Generation")
        self.ax.set_ylabel("Average Raw Fitness")
        self.ax.grid(True, alpha=0.3)

        plt.show(block=False)

    def fitness_cal(self):
        raw_fitness_values = []

        # Evaluate every individual
        for gameinstance in self.gameinstances:
            raw_fitness = gameinstance.fitness_cal()
            gameinstance.raw_fitness = raw_fitness
            raw_fitness_values.append(raw_fitness)

        # Track actual average fitness
        average_fitness = (
            sum(raw_fitness_values) / len(raw_fitness_values)
        )

        self.generation_history.append(self.gen)
        self.average_fitness_history.append(average_fitness)

        print(
            f"Generation: {self.gen} | "
            f"Average raw fitness: {average_fitness:.4f} | "
            f"Best raw fitness: {max(raw_fitness_values):.4f}"
        )

        # Shift fitness values to make them nonnegative
        min_fitness = min(raw_fitness_values)

        selection_weights = [
            fitness - min_fitness + 1e-6
            for fitness in raw_fitness_values
        ]

        total_fitness = sum(selection_weights)

        # Normalize into selection probabilities
        for i, gameinstance in enumerate(self.gameinstances):
            gameinstance.fitness = (
                selection_weights[i] / total_fitness
            )

        
    def selection(self):
        childgameinstances = []
        
        self.fitness_cal()

        best_individual = max(self.gameinstances,key=lambda x: x.raw_fitness)
        best_fitness = best_individual.raw_fitness
        best_individual.redbat.brain.weights_save("bestweight")
        
        self.update_graph()
        self.gen += 1

        elite = GameInstance.crossover( # adding elitism to the GA- Picking up the best individual from the previous generation and adding it to the current generation without mutation
            best_individual,
            best_individual,
            self.screen
        )
        childgameinstances.append(elite)


        for _ in range(self.population_size-1):
            def get_parent():
                while True:
                    parent = choice(self.gameinstances)
                    prob = random()
                    if prob<=parent.fitness:
                        return parent
            ParentA = get_parent()
            ParentB = get_parent()
            child = GameInstance.crossover(ParentA,ParentB,self.screen)
            child.mutate(self.mutation_rate)
            childgameinstances.append(child)

        # after selection
        self.gameinstances = childgameinstances

    def reproduction(self):
        end = time.perf_counter()

        # Evaluate and evolve after the evaluation period
        if end - self.start >= self.GAMEPLAY:
            self.selection()
            self.start = time.perf_counter()

        # Simulate every individual without rendering
        for gameinstance in self.gameinstances:
            gameinstance.gamestate_update()

        # Render only the elite (first individual)
        self.screen.fill((0, 0, 0))

        best = self.gameinstances[0]
        best.draw()



    def update_graph(self):
        self.line.set_data(
            self.generation_history,
            self.average_fitness_history
        )

        self.ax.relim()
        self.ax.autoscale_view()

        self.fig.canvas.draw_idle()
        self.fig.canvas.flush_events()
        plt.pause(0.001)

ga = GATraining(1000,0.01,screen,60)

while running:
    # to end the game loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False


    ga.reproduction()
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
plt.close("all")