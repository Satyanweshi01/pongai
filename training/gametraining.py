import os
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
from ui_comp import centerLine, infoBoard


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
    Here that neural network's weights and biases are the DNA I have to work with.
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

        # Wall collision detection with boundary clamping
        if self.ball.position.y <= self.config.WALL_TOP_BOUNDARY:
            self.ball.position.y = self.config.WALL_TOP_BOUNDARY
            self.ball.rect.y = round(self.ball.position.y)
            self.ball.velocity.y = abs(self.ball.velocity.y)
        elif self.ball.position.y >= self.config.WALL_BOTTOM_BOUNDARY - self.ball.radius * 2:
            self.ball.position.y = self.config.WALL_BOTTOM_BOUNDARY - self.ball.radius * 2
            self.ball.rect.y = round(self.ball.position.y)
            self.ball.velocity.y = -abs(self.ball.velocity.y) 

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

        # Rule-based blue bat opponent (tuned speed so red can score on steep returns)
        blue_speed = max(8, round(self.config.BAT_SENSITIVITY * 0.75))
        if self.ball.position.y < self.bluebat.bat.rect.centery - 10:
            if self.bluebat.bat.rect.y > self.config.BAT_TOP_BOUNDARY:
                self.bluebat.bat.rect.y -= blue_speed
        elif self.ball.position.y > self.bluebat.bat.rect.centery + 10:
            if self.bluebat.bat.rect.y < self.config.BAT_BOTTOM_BOUNDARY:
                self.bluebat.bat.rect.y += blue_speed

        
        redbat_inputs = [ # zero-centered normalized inputs to the redbat's neural network (-1.0 to 1.0)
            (self.ball.position.x - self.config.CENTER_X) / self.config.CENTER_X, #-1.0 is left edge(blue side), +1.0 is right edge(red side)
            (self.ball.position.y - self.config.CENTER_Y) / self.config.CENTER_Y, #-1.0 is top edge, 0.0 is mid-table ,+1.0 is bottom edge
            self.ball.velocity.x / 15, # negative is moving left, positive is moving right
            self.ball.velocity.y / 15, # negative is moving up, positive is moving down
            (self.ball.position.y - self.redbat.bat.rect.centery) / self.config.WINDOW_HEIGHT, # negative means ball is above paddle center, positive means ball is below paddle center, 0.0 is at the center
            (self.redbat.bat.rect.centery - self.config.CENTER_Y) / self.config.CENTER_Y # negative means paddle is in upper half of the table, positive means paddle is in lower half of the table, 0.0 is at the center
        ]
        redbat_decision = self.redbat.brain.forward(redbat_inputs)
        self.last_action = redbat_decision
        if redbat_decision == 1:
            if self.redbat.bat.rect.y > self.config.BAT_TOP_BOUNDARY:
                self.redbat.bat.rect.y-=self.config.BAT_SENSITIVITY
        elif redbat_decision == 2:
            if self.redbat.bat.rect.y < self.config.BAT_BOTTOM_BOUNDARY:
                self.redbat.bat.rect.y+=self.config.BAT_SENSITIVITY

    def draw(self, gen=0, best_fitness=0.0, all_time_best_fitness=0.0, speed=1):
        # This method is called ONLY for the AI being displayed
        centerLine(screen=self.screen, config=self.config)

        self.ball.draw()
        self.redbat.bat.draw()
        self.bluebat.bat.draw()

        # info board
        infoBoard(
            screen=self.screen,
            gen=gen,
            best_fitness=best_fitness,
            all_time_best_fitness=all_time_best_fitness,
            blue_score=self.bluebat.bat.score,
            red_score=self.redbat.bat.score,
            rally_deflections=self.redbat.bat.collision,
            last_action=self.last_action,
            speed=speed,
            config=self.config
        )

        
    @staticmethod
    def clone(ParentA, screen):
        child = GameInstance(1200, 700, screen)
        child.redbat.brain = ParentA.redbat.brain.clone()
        return child

    def mutate(self, mutation_rate, sigma=0.1):
        self.redbat.brain.mutate(mutation_rate, sigma=sigma) 



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
        self.all_time_best_fitness = -float("inf") # -float("inf") is used to produce negative infinity so even if fitness is in negative the best gets saved
        self.simulation_steps_per_frame = 1  
        self.paused = False
        self.saved_on_exit = False

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



        
    def selection(self):
        childgameinstances = []
        
        self.fitness_cal()

        best_individual = max(self.gameinstances,key=lambda x: x.raw_fitness)
        best_fitness = best_individual.raw_fitness
        self.best_fitness = best_fitness

        # Save only if a new all-time best record is achieved
        if best_fitness > self.all_time_best_fitness:
            self.all_time_best_fitness = best_fitness
            save_path = os.path.join(os.path.dirname(__file__), "bestweight")
            best_individual.redbat.brain.weights_save(save_path)
            print(f"New all-time best weights saved! Gen: {self.gen} | Fitness: {best_fitness:.4f}")
        
        self.update_graph()
        self.gen += 1

        elite = GameInstance.clone(best_individual,self.screen) # straight way cloning the parent to avoid the crossover distruction and making the process mutation only
        childgameinstances.append(elite)

        current_sigma = max(0.02, 0.15 * (0.98 ** self.gen))

        def get_parent(): # switching to tournament selection method
            contestants = [
                choice(self.gameinstances)
                for _ in range(3)
            ]
            return max(
                contestants,
                key=lambda individual: individual.raw_fitness
            )

        for _ in range(self.population_size-1):
            child = GameInstance.clone(get_parent(),self.screen) # straight way cloning the parent to avoid the crossover distruction and making the process mutation only
            child.mutate(self.mutation_rate, sigma=current_sigma)
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
            all_time_best_fitness=self.all_time_best_fitness,
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

    def save_on_exit(self, manual=False):
        if not manual and self.saved_on_exit:
            return

        save_path = os.path.join(os.path.dirname(__file__), "bestweight")

        # Check current ongoing population for any individual with higher fitness
        best_candidate = None
        best_candidate_fitness = self.all_time_best_fitness

        for gameinstance in self.gameinstances:
            current_fit = gameinstance.fitness_cal()
            if current_fit > best_candidate_fitness:
                best_candidate_fitness = current_fit
                best_candidate = gameinstance

        if best_candidate is not None:
            self.all_time_best_fitness = best_candidate_fitness
            best_candidate.redbat.brain.weights_save(save_path)
            prefix = "Manual save" if manual else "Exit save"
            print(f"{prefix}: New best weights saved! Gen: {self.gen} | Fitness: {best_candidate_fitness:.4f}")
        elif manual:
            print(f"Manual save: All-time best weights already up-to-date (Fitness: {self.all_time_best_fitness:.4f})")
        else:
            if self.all_time_best_fitness != -float("inf"):
                print(f"Training finished. All-time best weights preserved with fitness: {self.all_time_best_fitness:.4f}")
            else:
                # If stopped in Generation 0 before any generation completed
                best_ind = max(self.gameinstances, key=lambda x: x.fitness_cal())
                best_ind.redbat.brain.weights_save(save_path)
                self.all_time_best_fitness = best_ind.fitness_cal()
                print(f"Exit save: Gen 0 baseline weights saved with fitness: {self.all_time_best_fitness:.4f}")

        if not manual:
            self.saved_on_exit = True


if __name__ == "__main__":
    ga = GATraining(100, 0.05, screen)  

    try:
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
                    elif event.key == pygame.K_s:
                        ga.save_on_exit(manual=True)
                    elif event.key in (pygame.K_ESCAPE, pygame.K_q):
                        running = False
                        print("Exiting training session...")

            ga.reproduction()
            
            pygame.display.flip()
            clock.tick(60)
    except KeyboardInterrupt:
        print("\nTraining interrupted by user (Ctrl+C).")
    finally:
        ga.save_on_exit()
        pygame.quit()
        plt.close("all")