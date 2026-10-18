# Pongai - A Autonomous Game Agent using Neuroevolution that plays pong game really well

I always wondered what a AI, ML, Neural Network, Deep Learning truely means. So after finishing cs50, when I has to built a final project as my final assignment. I knew this was good time to explore the vast world of AI.

This project is the result of my exploration. Here I mixed up my old favourite thing with a new favourite thing - arcade game and neural networks.  

I built a AI that uses Neural Networks(written with raw python and numpy) trained via Genetic Algorithms (evolutionary strategies) to learn optimal paddle control without hardcoded rules.

---

### Techstack used -
1. pygame
2. python 3
3. numpy
4. matplotlib

For this project I have two main module- 
1. Training module(training folder) - that deals with training the neural network with the help of genetic algorithm.
2. Game module(final folder) - that deals with running the game with the trained neural network.

---

### Training Module(training folder)
In the training module - I have several modules -
1. **gametraining.py** - contains the training code that trains the neural network with the help of genetic algorithm.
   Here it has GameInstance which have all the physics and game objects, fitness function which calculate the fitness of the neural network based on the performance, gamestate_update() function which update the game state. draw() function which renders the game instance. It also has GATraining class which handles the training of the neural network using genetic algorithm. Here the neural network controls only the redbat's movement. The bluebat is controlled by a simple rule based algorithm.  

2. **game_comp.py** - contains the game code needed to create the sandbox environment for the neural network training.
   This contains Vectorcls, Mover, Bat, Ball, Paddlecreature class and also a text helper function.
   - The **Vectorcls** class is a custom class built to handle 2D vector operations.
   - **Mover** class is a base class for all the moving objects in the game. It is a child class of Vectorcls class.
   - **Bat** class is a child class of Mover class. It is a paddle used by the paddle creature to hit the ball.
   - **Ball** class is a child class of Mover class. It is the ball that is used to play the game.
   - **Paddlecreature** class is a child class of Mover class. It is a creature that controls the paddle and tries to hit the ball. It also has a neural network of its own which takes input from the game environment and produces output which controls the paddle. 

3. **nn_comp.py** - contains the neural network code that is used to train the neural network.
   This contains class **DenseLayer** - A class for neural network individual layer and **NeuralNetwork** class - A class which holds the entire neural network architecture, along with methods like clone, mutate, weights_save, weights_load, forward.
   - **clone()** and **mutate()** are two of the most important method for the genetic algorithm. They are used to create new neural networks and also to mutate the neural networks.
   - **weights_save()** and **weights_load()** are used to save and load the trained weights of the neural network.
   - **forward()** does the feedforward propagation of the neural network.

4. **ui_comp.py** - contains the ui code needed to display the game and the neural network training progress.
   This contains functions like - 
   - centerLine() - used to draw the center line of the game.
   - scoreBoard() - used to draw the scoreboard of the game.
   - timerDisplay() - used to display the timer of the game.
   - infoBoard() - used to display the info board of the game.

5. **config.py** - contains the configuration settings for the training module(sandbox environment).
   This contains a class **Config** which holds all the configuration settings for the training module(sandbox environment).

6. **bestweight.npz** - although not a module but it is a file that contains the trained weights of the neural network. It is saved in the same directory as the training module. 

---

### Currently neural network I am using have -
1. input layer(6 inputs) - with contains parameters like 
   - Ball X position
   - Ball Y position 
   - Ball X velocity 
   - Ball Y velocity 
   - Relative vertical distance between ball and paddle center
   - Paddle Y position

2. one hidden layer(8 perceptron) this uses Tanh activation function
3. output layer(3 perceptron) this uses linear activation function

#### Previous I experimented with neural network consists of-
1. input layer(6 perceptron)
2. one hidden layer(4 perceptron) this uses ReLU activation function
3. output layer(3 perceptron) this uses softmax activation function

I abondoned this architecture because it was not performing well. The ReLU activation function was causing neurons to deactivate and also softmax function was not doing anything useful.

I also used a tweaked version of genetic algorithm, Instead of using crossover and mutation to create next generation, I used only mutation to create next generation. Because I noticed that in the case of traditional genetic algorithm with crossover and mutation, the crossover destroys the good weights from the parents. 

- **Mutation-Only Reproduction**: Omitted crossover entirely, as recombining weights from two parents tended to destroy learned behaviors.
- **Tournament Selection**: Replaced roulette wheel selection with 3-way tournament selection to maintain steady selection pressure.
- **Elitism**: The best-performing network from each generation is carried over directly into the next without any mutation.
- **Decaying Mutation Step Size (sigma)**: The mutation magnitude decreases exponentially each generation (max(0.02, 0.15 * (0.98 ** gen))), shifting the algorithm from broad exploration early on to careful fine-tuning later.

#### The sandbox environment I used to train the ai consists of- 
1. Rule based opponent (blue bat)
2. Same physics as the game
3. Fixed simulation steps(3600) each generation.

It took me a lot of time to experiment with neural network architecture, activation functions, fitness function, population size, mutation rate and simulation steps to get the results I wanted.  

---

### Game module (final folder)
The game module contains the finished, fully playable Pong game that integrates the trained neural network, sound effects, retro arcade aesthetics, and an interactive real-time neural network visualizer.

In the game module - I have several files:
1. **game_with_paddlecreature.py** - The main entry point to run the game. It controls the overall game loop and state machine:
   - `STATE_MENU`: Main start screen with neon particle effects and title.
   - `STATE_MODE`: Screen to pick between "Player vs AI" and "Player vs Player".
   - `STATE_COUNTDOWN`: 3-second animated countdown before kick-off.
   - `STATE_GAME`: The active match with real-time scoring, boundary physics, and in-game navigation buttons (Back, Pause, AI Brain).

2. **nn_visualizer.py** - An interactive, real-time Neural Network Visualizer (`NNVisualizer`). Clicking the **"AI BRAIN"** button opens a live diagnostic window displaying:
   - All 6 input neurons with live normalized values.
   - All 8 hidden layer neurons showing weighted sums ($z$), bias values, and $tanh(z)$ activations.
   - The 3 output neurons highlighting the winning decision (`STAY`, `UP`, or `DOWN`).
   - Synaptic connection lines with dynamic green pulse animations reflecting signal transmission.

3. **screens.py** - Contains the visual screens and UI components:
   - `MenuScreen`: Main menu with animated ambient particles and the arcade title.
   - `ModeScreen`: Mode selection interface.
   - `PauseOverlay`: Dark semi-transparent pause menu allowing the player to Resume, Restart, Change Mode, or Return to Main Menu.
   - `PlayButton`: Interactive button class featuring hover animations and click effects.
   - `Title`: Renders the stylized title using the arcade pixel font.
   - `Particle`: Neon floating particle system used for background visual ambiance.

4. **sound_effects.py** - Contains the `SoundManager` class that manages low-latency procedural audio playback for:
   - Paddle collisions and wall bounces.
   - Goal scoring.
   - Match countdown beeps and game start sound.
   - Button click feedback.
   - Gracefully falls back if no audio hardware is detected.

5. **ui_comp.py** - Renders the in-game HUD:
   - `centerLine()`: Center court line with layered neon blue glow.
   - `scoreBoard()`: Modern dark-themed scoreboard with dedicated player panels.
   - `timerDisplay()`: In-game match duration display.

6. **game_comp.py** - Shares the exact physics components (`Ball`, `Bat`, `PaddleCreature`, `Mover`, `Vectorcls`) with the training environment to ensure identical gameplay dynamics.

7. **nn_comp.py** - Loads the trained weights from `bestweight.npz` and runs the feedforward inference using `tanh` hidden activations and linear logits for action selection. It also provides `get_forward_details()` to supply live matrix telemetry to the visualizer.

8. **config.py** - Central configuration class defining table dimensions (1200x700), paddle speeds, ball physics, and boundaries.

---

### Game Modes & Controls

#### Game Modes:
1. **Player vs AI (Default)**: Play against the neural network AI (Red Paddle). The AI paddle features deadband smoothing to avoid jitter while maintaining lightning-fast reaction speed.
2. **Player vs Player (Local 2-Player)**: Play against a friend on the same keyboard.

#### Controls:
- **Player 1 (Blue Paddle):** `W` (Up) / `S` (Down) or `UP` / `DOWN` arrow keys (in 1-Player mode).
- **Player 2 (Red Paddle - 2P Mode):** `UP` / `DOWN` arrow keys.
- **Pause Game:** Press `P` or click the in-game **PAUSE** button.
- **Toggle AI Brain Visualizer:** Click the **AI BRAIN** button in the top left.
- **Navigation:** Mouse click on interactive UI buttons.

---

### How to Run

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Satyanweshi01/pongai.git
   cd pongai
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirement.txt
   ```

3. **Play the game:**
   ```bash
   python3 final/game_with_paddlecreature.py
   ```

4. **(Optional) Run AI Training:**
   ```bash
   python3 training/gametraining.py
   ```

---

### Credits & Licenses
- **Pixel Font:** [Karmatic Arcade](https://www.dafont.com/karmatic-arcade.font) by Vic Fieger (Free for Commercial/Personal Use - FFC License).
- **Audio Effects:** Procedurally synthesized waveforms (CC0 1.0 Public Domain).
