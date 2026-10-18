import os
import pygame
from config import Config
from nn_comp import NeuralNetwork
from game_comp import PaddleCreature, Ball, Bat, text
from ui_comp import timerDisplay, scoreBoard, centerLine

pygame.init()

# Window config
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 700

# Creating window
config = Config(WINDOW_WIDTH, WINDOW_HEIGHT)
screen = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
pygame.display.set_caption("Pong AI") 

# Creating clock to control the rendering
clock = pygame.time.Clock()

# Game loop
running = True
delta_time = 0.1

# Bat objects
bluebat = PaddleCreature(
    0, WINDOW_HEIGHT // 2 - config.BAT_HEIGHT // 2,
    screen, (0, 100, 255), config.BAT_WIDTH, config.BAT_HEIGHT
)

redbat = PaddleCreature(
    WINDOW_WIDTH - config.BAT_WIDTH,
    WINDOW_HEIGHT // 2 - config.BAT_HEIGHT // 2,
    screen, (255, 50, 50), config.BAT_WIDTH, config.BAT_HEIGHT
)

# Load trained neural network weights
current_dir = os.path.dirname(os.path.abspath(__file__))
final_weights = os.path.join(current_dir, "bestweight.npz")
training_weights = os.path.join(current_dir, "..", "training", "bestweight.npz")

weights_to_load = None
if os.path.exists(final_weights) and os.path.exists(training_weights):
    # Pick whichever is newer
    if os.path.getmtime(training_weights) > os.path.getmtime(final_weights):
        weights_to_load = training_weights
    else:
        weights_to_load = final_weights
elif os.path.exists(final_weights):
    weights_to_load = final_weights
elif os.path.exists(training_weights):
    weights_to_load = training_weights

if weights_to_load:
    print(f"Loading trained weights from: {weights_to_load}")
    redbat.brain.weights_load(weights_to_load)
else:
    print("WARNING: No bestweight.npz found in final/ or training/! Run training/gametraining.py first.")

# Ball object
ball = Ball(
    config.CENTER_X,
    config.CENTER_Y,
    screen, config.BALL_SPEED, config.BALL_RADIUS
)

frame = 0
hour = 0 
minute = 0
sec = 0
t_time = 0

while running:
    screen.fill((0, 0, 0))  # Black background

    centerLine(screen=screen, config=config)
    scoreBoard(screen=screen, player1=bluebat, player2=redbat, config=config)

    # Time update
    frame += 1
    if frame == 60:
        sec += 1
        t_time += 1
        frame = 0
    if sec == 60:
        minute += 1
        sec = 0
    if minute == 60:
        hour += 1
        minute = 0
    formatted_time = f"{hour:02}:{minute:02}:{sec:02}"
    timerDisplay(screen=screen, formatted_time=formatted_time, config=config)
    
    # Speed dynamism
    if t_time < 30:
        ball.velocityconst = 5 
    elif t_time < 60:
        ball.velocityconst = 7 
    elif t_time < 120:
        ball.velocityconst = 9
    elif t_time < 180:
        ball.velocityconst = 11
    elif t_time < 300:
        ball.velocityconst = 13
    else:
        ball.velocityconst = 15

    ball.velocityconst = ball.velocityconst * config.BALL_SPEED_SCALE
    ball.velocity_update()

    ball.draw()
    ball.update()

    # Wall collision with clamping to prevent jitter
    if ball.position.y > config.WALL_BOTTOM_BOUNDARY:
        ball.position.y = config.WALL_BOTTOM_BOUNDARY
        ball.wallcollision()
    elif ball.position.y < config.WALL_TOP_BOUNDARY:
        ball.position.y = config.WALL_TOP_BOUNDARY
        ball.wallcollision()

    redbat.bat.draw()
    bluebat.bat.draw()    

    # Collision between ball and paddles
    if ball.rect.colliderect(redbat.bat.rect):
        ball.paddlecollision(redbat.bat)

    if ball.rect.colliderect(bluebat.bat.rect):
        ball.paddlecollision(bluebat.bat)

    # Boundary check (scoring)
    if ball.position.x > config.WALL_RIGHT_BOUNDARY:
        bluebat.bat.score += 1
        ball.restart()
    if ball.position.x < config.WALL_LEFT_BOUNDARY:
        redbat.bat.score += 1
        ball.restart()

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                running = False

    # Keyboard input for human player (Blue bat: W/S or UP/DOWN arrows)
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w] or keys[pygame.K_UP]:
        if bluebat.bat.rect.y > config.BAT_TOP_BOUNDARY:
            bluebat.bat.rect.y -= config.BAT_SENSITIVITY
    elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
        if bluebat.bat.rect.y < config.BAT_BOTTOM_BOUNDARY:
            bluebat.bat.rect.y += config.BAT_SENSITIVITY

    # Neural network decision making for AI (Red bat)
    # Zero-centered normalized inputs matching training representation
    redbat_inputs = [
        (ball.position.x - config.CENTER_X) / config.CENTER_X,                         # [-1.0, +1.0]
        (ball.position.y - config.CENTER_Y) / config.CENTER_Y,                         # [-1.0, +1.0]
        ball.velocity.x / 15.0,                                                        # [-1.0, +1.0]
        ball.velocity.y / 15.0,                                                        # [-1.0, +1.0]
        (ball.position.y - redbat.bat.rect.centery) / config.WINDOW_HEIGHT,            # vertical error relative to bat center
        (redbat.bat.rect.centery - config.CENTER_Y) / config.CENTER_Y                 # bat position on court [-1.0, +1.0]
    ]

    redbat_decision = redbat.brain.forward(redbat_inputs)
    if redbat_decision == 1:
        if redbat.bat.rect.y > config.BAT_TOP_BOUNDARY:
            redbat.bat.rect.y -= config.BAT_SENSITIVITY
    elif redbat_decision == 2:
        if redbat.bat.rect.y < config.BAT_BOTTOM_BOUNDARY:
            redbat.bat.rect.y += config.BAT_SENSITIVITY
    
    pygame.display.flip()
    
    delta_time = clock.tick(60) / 1000
    delta_time = max(0.001, min(0.1, delta_time))

pygame.quit()