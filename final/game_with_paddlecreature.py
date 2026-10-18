import os
import math
import pygame
from config import Config
from game_comp import PaddleCreature, Ball
from ui_comp import timerDisplay, scoreBoard, centerLine
from sound_effects import sound_manager
from nn_visualizer import NNVisualizer
from screens import (
    MenuScreen,
    ModeScreen,
    PauseOverlay,
    PlayButton,
    COLOR_BLACK,
    COLOR_WHITE,
    COLOR_BLUE,
    COLOR_RED
)

pygame.init()

# Window setup
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 700

config = Config(WINDOW_WIDTH, WINDOW_HEIGHT)
screen = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
pygame.display.set_caption("Pong AI") 

clock = pygame.time.Clock()

# Game States
STATE_MENU = 0
STATE_MODE = 1
STATE_COUNTDOWN = 2
STATE_GAME = 3

# Game Modes
MODE_AI = 0
MODE_HUMAN = 1

current_state = STATE_MENU
current_mode = MODE_AI
countdown_timer = 6.0
last_countdown_text = None

countdown_font = pygame.font.SysFont("Arial", 96, bold=True)

# Initialize screens and interactive controls
menu_screen = MenuScreen(width=WINDOW_WIDTH, height=WINDOW_HEIGHT)
mode_screen = ModeScreen(width=WINDOW_WIDTH, height=WINDOW_HEIGHT)
pause_overlay = PauseOverlay(width=WINDOW_WIDTH, height=WINDOW_HEIGHT)

in_game_back_btn = PlayButton(center_x=90, center_y=38, width=130, height=42, text="BACK", font_size=18)
in_game_pause_btn = PlayButton(center_x=WINDOW_WIDTH - 90, center_y=38, width=130, height=42, text="PAUSE", font_size=18)
in_game_brain_btn = PlayButton(center_x=245, center_y=38, width=150, height=42, text="AI BRAIN", font_size=17)

# Live Neural Network Visualizer
visualizer = NNVisualizer()

# Bat objects (Strictly Blue for Player, Red for AI)
bluebat = PaddleCreature(
    0, WINDOW_HEIGHT // 2 - config.BAT_HEIGHT // 2,
    screen, COLOR_BLUE, config.BAT_WIDTH, config.BAT_HEIGHT
)

redbat = PaddleCreature(
    WINDOW_WIDTH - config.BAT_WIDTH,
    WINDOW_HEIGHT // 2 - config.BAT_HEIGHT // 2,
    screen, COLOR_RED, config.BAT_WIDTH, config.BAT_HEIGHT
)

# Load trained weights strictly from training folder
current_dir = os.path.dirname(os.path.abspath(__file__))
training_weights = os.path.join(current_dir, "..", "training", "bestweight.npz")

if os.path.exists(training_weights):
    print(f"Loading trained weights from: {training_weights}")
    redbat.brain.weights_load(training_weights)
else:
    print(f"WARNING: No trained weights found at {training_weights}! Run training/gametraining.py first.")

# Ball object
ball = Ball(
    config.CENTER_X,
    config.CENTER_Y,
    screen, config.BALL_SPEED, config.BALL_RADIUS
)

# Time tracking
frame = 0
t_time = 0

paused = False
redbat_decision = 0
running = True

def toggle_pause():
    global paused
    paused = not paused
    in_game_pause_btn.set_text("PLAY" if paused else "PAUSE")

def get_ai_inputs():
    """Extracts live normalized features for neural network AI and visualizer."""
    return [
        (ball.position.x - config.CENTER_X) / config.CENTER_X,                         # [-1.0, +1.0]
        (ball.position.y - config.CENTER_Y) / config.CENTER_Y,                         # [-1.0, +1.0]
        ball.velocity.x / 15.0,                                                        # [-1.0, +1.0]
        ball.velocity.y / 15.0,                                                        # [-1.0, +1.0]
        (ball.position.y - redbat.bat.rect.centery) / config.WINDOW_HEIGHT,            # Vertical error
        (redbat.bat.rect.centery - config.CENTER_Y) / config.CENTER_Y                 # Paddle court position
    ]

def reset_game():
    global frame, t_time, paused, last_countdown_text, redbat_decision
    paused = False
    redbat_decision = 0
    last_countdown_text = None
    in_game_pause_btn.set_text("PAUSE")
    bluebat.bat.score = 0
    redbat.bat.score = 0
    bluebat.bat.rect.y = WINDOW_HEIGHT // 2 - config.BAT_HEIGHT // 2
    redbat.bat.rect.y = WINDOW_HEIGHT // 2 - config.BAT_HEIGHT // 2
    ball.restart()
    frame = 0
    t_time = 0
    visualizer.hide()

def draw_court(formatted_time: str = "00:00:00"):
    screen.fill(COLOR_BLACK)
    centerLine(screen=screen, config=config)
    p1_name = "PLAYER" if current_mode == MODE_AI else "PLAYER 1"
    p2_name = "AI BOT" if current_mode == MODE_AI else "PLAYER 2"
    scoreBoard(screen=screen, player1=bluebat, player2=redbat, config=config, p1_name=p1_name, p2_name=p2_name)
    timerDisplay(screen=screen, formatted_time=formatted_time, config=config)
    ball.draw()
    redbat.bat.draw()
    bluebat.bat.draw()

def draw_in_game_buttons(dt, mouse_pos, show_pause: bool = True):
    in_game_back_btn.update(dt, mouse_pos)
    in_game_back_btn.draw(screen)
    if show_pause:
        in_game_pause_btn.update(dt, mouse_pos)
        in_game_pause_btn.draw(screen)
    if current_mode == MODE_AI:
        in_game_brain_btn.set_text("AI BRAIN ON" if visualizer.is_open else "AI BRAIN")
        in_game_brain_btn.update(dt, mouse_pos)
        in_game_brain_btn.draw(screen)

def handle_player_inputs(keys):
    if current_mode == MODE_AI:
        up = keys[pygame.K_w] or keys[pygame.K_UP]
        down = keys[pygame.K_s] or keys[pygame.K_DOWN]
    else:
        up = keys[pygame.K_w]
        down = keys[pygame.K_s]
        if keys[pygame.K_UP] and redbat.bat.rect.y > config.BAT_TOP_BOUNDARY:
            redbat.bat.rect.y -= config.BAT_SENSITIVITY
        elif keys[pygame.K_DOWN] and redbat.bat.rect.y < config.BAT_BOTTOM_BOUNDARY:
            redbat.bat.rect.y += config.BAT_SENSITIVITY

    if up and bluebat.bat.rect.y > config.BAT_TOP_BOUNDARY:
        bluebat.bat.rect.y -= config.BAT_SENSITIVITY
    elif down and bluebat.bat.rect.y < config.BAT_BOTTOM_BOUNDARY:
        bluebat.bat.rect.y += config.BAT_SENSITIVITY

while running:
    dt = clock.tick(60) / 1000.0
    dt = max(0.001, min(0.1, dt))
    mouse_pos = pygame.mouse.get_pos()

    # =========================================================================
    # EVENT HANDLING
    # =========================================================================
    for event in pygame.event.get():
        # Dedicated event routing for secondary visualizer window
        if visualizer.is_open and getattr(event, "window", None) == visualizer.window:
            visualizer.handle_event(event, pause_callback=toggle_pause)
            continue

        if event.type == pygame.QUIT:
            running = False

        if current_state == STATE_MENU:
            action = menu_screen.handle_event(event)
            if action == "PLAY":
                current_state = STATE_MODE
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        elif current_state == STATE_MODE:
            action = mode_screen.handle_event(event)
            if action == "VS_AI":
                current_mode = MODE_AI
                reset_game()
                countdown_timer = 6.0
                current_state = STATE_COUNTDOWN
            elif action == "VS_HUMAN":
                current_mode = MODE_HUMAN
                reset_game()
                countdown_timer = 6.0
                current_state = STATE_COUNTDOWN
            elif action == "BACK":
                current_state = STATE_MENU
                visualizer.hide()

        elif current_state == STATE_COUNTDOWN:
            if in_game_back_btn.handle_event(event):
                current_state = STATE_MODE
                visualizer.hide()
            elif current_mode == MODE_AI and in_game_brain_btn.handle_event(event):
                visualizer.toggle()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                sound_manager.play_click()
                current_state = STATE_MODE
                visualizer.hide()
            elif current_mode == MODE_AI and event.type == pygame.KEYDOWN and event.key == pygame.K_b:
                visualizer.toggle()

        elif current_state == STATE_GAME:
            if paused:
                # Handle pause overlay events (RESUME, RESTART, MODE, MENU)
                pause_action = pause_overlay.handle_event(event)
                if pause_action == "RESUME":
                    paused = False
                    in_game_pause_btn.set_text("PAUSE")
                elif pause_action == "RESTART":
                    reset_game()
                    countdown_timer = 6.0
                    current_state = STATE_COUNTDOWN
                elif pause_action == "MODE":
                    paused = False
                    current_state = STATE_MODE
                    in_game_pause_btn.set_text("PAUSE")
                    visualizer.hide()
                elif pause_action == "MENU":
                    paused = False
                    current_state = STATE_MENU
                    in_game_pause_btn.set_text("PAUSE")
                    visualizer.hide()

                # Top bar buttons also respond while paused
                if in_game_pause_btn.handle_event(event):
                    paused = False
                    in_game_pause_btn.set_text("PAUSE")
                elif in_game_back_btn.handle_event(event):
                    paused = False
                    current_state = STATE_MODE
                    in_game_pause_btn.set_text("PAUSE")
                    visualizer.hide()
                elif current_mode == MODE_AI and in_game_brain_btn.handle_event(event):
                    visualizer.toggle()
            else:
                # In active gameplay
                if in_game_pause_btn.handle_event(event):
                    paused = True
                    in_game_pause_btn.set_text("PLAY")
                elif in_game_back_btn.handle_event(event):
                    current_state = STATE_MODE
                    visualizer.hide()
                elif current_mode == MODE_AI and in_game_brain_btn.handle_event(event):
                    visualizer.toggle()
                elif event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_SPACE, pygame.K_p, pygame.K_ESCAPE):
                        paused = True
                        in_game_pause_btn.set_text("PLAY")
                        sound_manager.play_click()
                    elif event.key == pygame.K_r:
                        reset_game()
                        countdown_timer = 6.0
                        current_state = STATE_COUNTDOWN
                        sound_manager.play_click()
                    elif current_mode == MODE_AI and event.key == pygame.K_b:
                        visualizer.toggle()

    # =========================================================================
    # STATE: MENU
    # =========================================================================
    if current_state == STATE_MENU:
        menu_screen.update(dt, mouse_pos)
        menu_screen.draw(screen)

    # =========================================================================
    # STATE: MODE SELECTION
    # =========================================================================
    elif current_state == STATE_MODE:
        mode_screen.update(dt, mouse_pos)
        mode_screen.draw(screen)

    # =========================================================================
    # STATE: COUNTDOWN BEFORE MATCH
    # =========================================================================
    elif current_state == STATE_COUNTDOWN:
        countdown_timer -= dt

        # Players can adjust paddle positions before game starts
        handle_player_inputs(pygame.key.get_pressed())

        # Ball stays stationary at center until countdown ends
        ball.position.x = config.CENTER_X
        ball.position.y = config.CENTER_Y

        if countdown_timer <= 0:
            ball.restart()
            current_state = STATE_GAME

        # Render Court
        draw_court("00:00:00")

        # Animated countdown counter with pop-in pop-out (5, 4, 3, 2, 1, then START!)
        display_text = str(max(1, math.ceil(countdown_timer) - 1)) if countdown_timer > 1.0 else "START!"

        # Play countdown audio on each number/text pop-in
        if display_text != last_countdown_text:
            last_countdown_text = display_text
            if display_text == "START!":
                sound_manager.play_start()
            else:
                sound_manager.play_countdown()

        # Normalized progress of the current 1-second interval: 0.0 -> 1.0
        t = math.ceil(countdown_timer) - countdown_timer

        # Pop in (0.0 to 0.20s): snappy elastic overshoot into full view
        if t < 0.20:
            p = t / 0.20
            scale = 1.0 + 2.70158 * ((p - 1.0) ** 3) + 1.70158 * ((p - 1.0) ** 2)
            alpha = min(255, int(p * 350))
        # Hold (0.20 to 0.80s): crisp static display
        elif t < 0.80:
            scale = 1.0
            alpha = 255
        # Pop out (0.80 to 1.0s): quickly shrinks away into next number / match start
        else:
            p_out = (t - 0.80) / 0.20
            scale = max(0.01, 1.0 - (p_out ** 1.8))
            alpha = max(0, int(255 * (1.0 - p_out)))

        if scale > 0.01 and alpha > 0:
            base_surf = countdown_font.render(display_text, True, COLOR_WHITE)
            scaled_surf = pygame.transform.rotozoom(base_surf, 0, scale)
            scaled_surf.set_alpha(alpha)
            screen.blit(scaled_surf, scaled_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)))

        # Header buttons during countdown
        draw_in_game_buttons(dt, mouse_pos, show_pause=False)

    # =========================================================================
    # STATE: IN-GAME (USER VS TRAINED AI OR HUMAN)
    # =========================================================================
    elif current_state == STATE_GAME:
        if not paused:
            # Time update
            frame += 1
            if frame >= 60:
                t_time += 1
                frame = 0

            # Dynamic speed progression
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
            ball.update()

            # Wall collision with clamping to prevent multi-frame jitter
            if ball.position.y > config.WALL_BOTTOM_BOUNDARY and ball.velocity.y > 0:
                ball.position.y = config.WALL_BOTTOM_BOUNDARY
                ball.wallcollision()
                sound_manager.play_wall_hit()
            elif ball.position.y < config.WALL_TOP_BOUNDARY and ball.velocity.y < 0:
                ball.position.y = config.WALL_TOP_BOUNDARY
                ball.wallcollision()
                sound_manager.play_wall_hit()

            # Paddle collisions (Realistic deflection angles + surface clamping)
            if ball.rect.colliderect(redbat.bat.rect):
                prev_vx = ball.velocity.x
                ball.paddlecollision(redbat.bat)
                if ball.velocity.x != prev_vx:
                    sound_manager.play_paddle_hit()

            if ball.rect.colliderect(bluebat.bat.rect):
                prev_vx = ball.velocity.x
                ball.paddlecollision(bluebat.bat)
                if ball.velocity.x != prev_vx:
                    sound_manager.play_paddle_hit()

            # Scoring & Boundary check
            if ball.position.x > config.WALL_RIGHT_BOUNDARY:
                bluebat.bat.score += 1
                ball.restart()
                sound_manager.play_score()
            if ball.position.x < config.WALL_LEFT_BOUNDARY:
                redbat.bat.score += 1
                ball.restart()
                sound_manager.play_score()

            # Paddle control based on game mode
            keys = pygame.key.get_pressed()
            handle_player_inputs(keys)

            if current_mode == MODE_AI:
                # Neural network AI decision making (Red bat)
                redbat_inputs = get_ai_inputs()
                redbat_decision = redbat.brain.forward(redbat_inputs)

                # Vertical distance between ball and paddle center
                error_y = ball.position.y - redbat.bat.rect.centery

                # Deadband: if ball is aligned within central paddle area (+/- 10px), hold still (STAY)
                if abs(error_y) < 10:
                    redbat_decision = 0

                # Clamped step size: prevent overshooting target Y, eliminating 60Hz vibration/jitter
                step = min(config.BAT_SENSITIVITY, max(1, int(abs(error_y))))

                if redbat_decision == 1 and redbat.bat.rect.y > config.BAT_TOP_BOUNDARY:
                    redbat.bat.rect.y -= step
                elif redbat_decision == 2 and redbat.bat.rect.y < config.BAT_BOTTOM_BOUNDARY:
                    redbat.bat.rect.y += step

        # Render Court & Game
        draw_court(f"{t_time // 3600:02}:{(t_time % 3600) // 60:02}:{t_time % 60:02}")

        # Update and render in-game navigation and pause/play controls
        draw_in_game_buttons(dt, mouse_pos, show_pause=True)

        # Interactive Pause Overlay
        if paused:
            pause_overlay.update(dt, mouse_pos)
            pause_overlay.draw(screen)

    # Update and draw live neural network visualizer if open
    if current_mode == MODE_AI and visualizer.is_open:
        visualizer.update_and_draw(dt, redbat.brain, get_ai_inputs(), is_paused=paused, active_decision=redbat_decision if not paused else 0)

    pygame.display.flip()

visualizer.destroy()
pygame.quit()