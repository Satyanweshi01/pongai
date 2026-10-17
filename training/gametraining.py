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
        self.total_miss_error = 0.0
        self.last_action = 0

        self.sim_frames = 0
        self.t_time = 0

    def fitness_cal(self):
        # rewarding for hits
        hit_reward = 3.0 * self.redbat.bat.collision

        # Reward for sccoring
        score_reward = 10.0 * self.redbat.bat.score

        # penalty for missing the ball
        miss_penalty = -3.0 * self.bluebat.bat.score

        # distance penalty
        distance_penalty = -2.0 * self.total_miss_error
        self.fitness = hit_reward + score_reward + miss_penalty + distance_penalty
        return self.fitness

    def gamestate_update(self):
        # Advance this game's simulation clock
        self.sim_frames += 1
        if self.sim_frames < 180:
            speed = 5
        elif self.sim_frames < 360:
            speed = 7
        elif self.sim_frames < 720:
            speed = 9
        elif self.sim_frames < 1080:
            speed = 11
        elif self.sim_frames < 1800:
            speed = 13
        else:
            speed = 15

        self.ball.velocityconst = (
            speed * self.config.BALL_SPEED_SCALE
        )
        self.ball.velocity_update()

        # Update ball physics
        self.ball.update()

        # Synchronize collision rectangle with physics position
        self.ball.rect.x = round(self.ball.position.x)
        self.ball.rect.y = round(self.ball.position.y)

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
            # calculation of the distance error
            error = abs(self.ball.position.y - self.redbat.bat.rect.centery) / self.config.WINDOW_HEIGHT
            self.total_miss_error+= error

            self.ball.restart()
        if self.ball.position.x < self.config.WALL_LEFT_BOUNDARY:
            self.redbat.bat.score+=1
            self.ball.restart()

        # Rule-based blue bat opponent
        if self.ball.position.y < self.bluebat.bat.rect.centery - 10:
            if self.bluebat.bat.rect.y > self.config.BAT_TOP_BOUNDARY:
                self.bluebat.bat.rect.y -= self.config.BAT_SENSITIVITY
        elif self.ball.position.y > self.bluebat.bat.rect.centery + 10:
            if self.bluebat.bat.rect.y < self.config.BAT_BOTTOM_BOUNDARY:
                self.bluebat.bat.rect.y += self.config.BAT_SENSITIVITY

        
        redbat_inputs = [ # sending normalized inputs to the redbat's neural network
            self.ball.position.x / self.config.WINDOW_WIDTH,
            self.ball.position.y / self.config.WINDOW_HEIGHT,
            self.ball.velocity.x / 15,
            self.ball.velocity.y / 15,
            self.redbat.bat.rect.x / self.config.WINDOW_WIDTH,
            self.redbat.bat.rect.y / self.config.WINDOW_HEIGHT
        ]
        redbat_decision = self.redbat.brain.forward(redbat_inputs)
        self.last_action = redbat_decision
        if redbat_decision == 1:
            if self.redbat.bat.rect.y > self.config.BAT_TOP_BOUNDARY:
                self.redbat.bat.rect.y-=self.config.BAT_SENSITIVITY
        elif redbat_decision == 2:
            if self.redbat.bat.rect.y < self.config.BAT_BOTTOM_BOUNDARY:
                self.redbat.bat.rect.y+=self.config.BAT_SENSITIVITY

    def draw(self, gen=0, best_fitness=0.0, speed=1):
        # This method is called ONLY for the AI being displayed
        centerLine(screen=self.screen, config=self.config)

        self.ball.draw()
        self.redbat.bat.draw()
        self.bluebat.bat.draw()

        # info board
        hud_surface = pygame.Surface((270, 130), pygame.SRCALPHA)
        hud_surface.fill((8, 14, 26, 210))  # dark glassmorphism panel
        self.screen.blit(hud_surface, (15, 15))
        pygame.draw.rect(self.screen, (0, 220, 255), (15, 15, 270, 130), width=1, border_radius=6)

        font_large = pygame.font.SysFont("Arial", 18, bold=True)
        font_small = pygame.font.SysFont("Arial", 13, bold=True)

        action_names = {0: "HOLD [ — ]", 1: "UP [ ▲ ]", 2: "DOWN [ ▼ ]"}
        WHITE = (255, 255, 255)

        gen_text = font_large.render(f"GENERATION: {gen:03d}", True, WHITE)
        fit_text = font_large.render(f"BEST FIT: {best_fitness:+.2f}", True, WHITE)
        score_text = font_small.render(f"SCORE: Blue {self.bluebat.bat.score:02d} | Red {self.redbat.bat.score:02d}", True, WHITE)
        hits_text = font_small.render(f"RALLY DEFLECTIONS: {self.redbat.bat.collision}", True, WHITE)
        act_text = font_small.render(f"AI ACTION: {action_names.get(self.last_action, 'UNKNOWN')}", True, WHITE)
        speed_text = font_small.render(f"SPEED: {speed}x  [↑/↓ Speed, SPACE Pause]", True, WHITE)

        self.screen.blit(gen_text, (25, 20))
        self.screen.blit(fit_text, (25, 42))
        self.screen.blit(score_text, (25, 65))
        self.screen.blit(hits_text, (25, 82))
        self.screen.blit(act_text, (25, 99))
        self.screen.blit(speed_text, (25, 118))
        
    def clone(ParentA,screen):
        child = GameInstance(1200,700,screen)

        # child.redbat.brain.hiddenlayer1.weights = np.where(
        #     np.random.random(
        #         ParentA.redbat.brain.hiddenlayer1.weights.shape
        #     ) < 0.5,
        #     ParentA.redbat.brain.hiddenlayer1.weights,
        #     ParentB.redbat.brain.hiddenlayer1.weights
        # ).copy()

        # child.redbat.brain.hiddenlayer1.biases = np.where(
        #     np.random.random(
        #         ParentA.redbat.brain.hiddenlayer1.biases.shape
        #     ) < 0.5,
        #     ParentA.redbat.brain.hiddenlayer1.biases,
        #     ParentB.redbat.brain.hiddenlayer1.biases
        # ).copy()

        # child.redbat.brain.outputlayer.weights = np.where(
        #     np.random.random(
        #         ParentA.redbat.brain.outputlayer.weights.shape
        #     ) < 0.5,
        #     ParentA.redbat.brain.outputlayer.weights,
        #     ParentB.redbat.brain.outputlayer.weights
        # ).copy()

        # child.redbat.brain.outputlayer.biases = np.where(
        #     np.random.random(
        #         ParentA.redbat.brain.outputlayer.biases.shape
        #     ) < 0.5,
        #     ParentA.redbat.brain.outputlayer.biases,
        #     ParentB.redbat.brain.outputlayer.biases
        # ).copy() this code just randomly picks the parent weights and combines them to create a child that is fine for other scenerio but for case of neural network it breaks them
        child.redbat.brain.hiddenlayer1.weights = ParentA.redbat.brain.hiddenlayer1.weights.copy()
        child.redbat.brain.hiddenlayer1.biases = ParentA.redbat.brain.hiddenlayer1.biases.copy()
        child.redbat.brain.outputlayer.weights = ParentA.redbat.brain.outputlayer.weights.copy()
        child.redbat.brain.outputlayer.biases = ParentA.redbat.brain.outputlayer.biases.copy()

        return child
    def mutate(self,mutation_rate):
        for weights in [self.redbat.brain.hiddenlayer1.weights, self.redbat.brain.outputlayer.weights]:
            mask = np.random.random(weights.shape) < mutation_rate
            weights[mask] += np.random.normal(0, 0.1, size= np.count_nonzero(mask))
            np.clip(weights, -3.0, 3.0, out = weights)

        bias_mutation_rate = max(0.20, mutation_rate*3)
        for biases in [self.redbat.brain.hiddenlayer1.biases, self.redbat.brain.outputlayer.biases]:
            mask = np.random.random(biases.shape) < bias_mutation_rate
            biases[mask] += np.random.normal(0, 0.1, size= np.count_nonzero(mask))
            np.clip(biases, -3.0, 3.0, out = biases) 



class GATraining:
    def __init__(self,population_size:int,mutation_rate:float,screen):
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.screen = screen
        self.gen = 0
        self.gameinstances = []
        for i in range(population_size):
            self.gameinstances.append(GameInstance(1200,700,screen))

        self.steps_per_generation = 1200  # fast generation cycles for time-lapse
        self.steps_this_generation = 0

        self.best_to_render = self.gameinstances[0]
        self.best_fitness = 0.0
        self.simulation_steps_per_frame = 1  
        self.paused = False

        self.generation_history = []
        self.average_fitness_history = []

        # Matplotlib interactive graph
        plt.ion()

        self.fig, self.ax = plt.subplots(figsize=(9, 5))
        self.line, = self.ax.plot([], [], "b-o", markersize=4)

        self.ax.set_title("Average Fitness per Generation")
        self.ax.set_xlabel("Generation")
        self.ax.set_ylabel("Average Fitness")
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
            f"Average fitness: {average_fitness:.4f} | "
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
        self.best_fitness = best_fitness
        best_individual.redbat.brain.weights_save("bestweight")
        
        self.update_graph()
        self.gen += 1

        elite = GameInstance.clone(best_individual,self.screen) # straight way cloning the parent to avoid the crossover distruction and making the process mutation only
        childgameinstances.append(elite)


        for _ in range(self.population_size-1):
            def get_parent(): # switching to tornament selection method
                contestants = [
                    choice(self.gameinstances)
                    for _ in range(3)
                ]
                return max(
                    contestants,
                    key=lambda individual: individual.raw_fitness
                )
            # ParentA = get_parent()
            # ParentB = get_parent()
            # child = GameInstance.crossover(ParentA,ParentB,self.screen)
            child = GameInstance.clone(get_parent(),self.screen) # straight way cloning the parent to avoid the crossover distruction and making the process mutation only
            child.mutate(self.mutation_rate)
            childgameinstances.append(child)

        # after selection
        self.gameinstances = childgameinstances
        self.best_to_render = self.gameinstances[0] # storing the elite to render


    def reproduction(self):
        if not self.paused:
            # Advance every individual's simulation with fast-forward steps
            for _ in range(self.simulation_steps_per_frame):
                for gameinstance in self.gameinstances:
                    gameinstance.gamestate_update()

                self.steps_this_generation += 1

            # Finish the generation after the fixed step budget
            if self.steps_this_generation >= self.steps_per_generation:
                self.selection()
                self.steps_this_generation = 0

        # Render only the best individual with HUD
        self.screen.fill((0, 0, 0))

        self.best_to_render.draw(
            gen=self.gen,
            best_fitness=self.best_fitness,
            speed=self.simulation_steps_per_frame
        )



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

ga = GATraining(80, 0.05, screen)  

while running:
    # to end the game loop or handle interactive speed controls
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                ga.simulation_steps_per_frame = min(30, ga.simulation_steps_per_frame + 2)
                print(f"Simulation fast-forward speed: {ga.simulation_steps_per_frame}x")
            elif event.key == pygame.K_DOWN:
                ga.simulation_steps_per_frame = max(1, ga.simulation_steps_per_frame - 2)
                print(f"Simulation fast-forward speed: {ga.simulation_steps_per_frame}x")
            elif event.key == pygame.K_SPACE:
                ga.paused = not ga.paused
                print("Simulation Paused" if ga.paused else "Simulation Resumed")


    ga.reproduction()
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
plt.close("all")