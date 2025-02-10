import pygame
import models
import agent

NORTH = 0
EAST = 1
SOUTH = 2
WEST = 3
BLOCKSIZE = models.BLOCKSIZE

SCREEN_WIDTH = 720
SCREEN_HEIGHT = 720

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
keepRunning = True
player = models.Player(pygame.display.get_window_size()[0], pygame.display.get_window_size()[1])
pellet = models.Pellet(SCREEN_WIDTH, SCREEN_HEIGHT)
score = 0
gameOver = False
gotPellet = False
episodeDisp = 0


inputQueue = []

import numpy as np

def get_state():
    head = player.getHead()
    food_x, food_y = pellet.x, pellet.y
    head_x, head_y = head.x, head.y
    direction = head.direction  # Assuming this returns NORTH, EAST, SOUTH, or WEST
    
    # Relative distance to food
    food_dx = food_x - head_x
    food_dy = food_y - head_y

    # Distance to walls
    dist_wall_up = head_y
    dist_wall_down = SCREEN_HEIGHT - (head_y + BLOCKSIZE)
    dist_wall_left = head_x
    dist_wall_right = SCREEN_WIDTH - (head_x + BLOCKSIZE)

    # One-hot encode direction
    direction_encoding = [0, 0, 0, 0]
    direction_encoding[direction] = 1

    # Final state vector
    state = np.array([
        food_dx, food_dy,
        dist_wall_up, dist_wall_down, dist_wall_left, dist_wall_right,
        *direction_encoding
    ], dtype=np.float32)

    return state


def addQ(dir):
    if len(inputQueue) > 3:
        return
    inputQueue.append(dir)

def popQ():
    if len(inputQueue) <= 0:
        return
    return inputQueue.pop(0)

def renderScore():
    font = pygame.font.Font('freesansbold.ttf', 15)
    text = font.render(f'Score: {score} Generation: {episodeDisp}', True, (0, 255, 0), (0, 0, 255))
    textRect = text.get_rect()
    textRect.center = (90, 25)
    screen.blit(text, textRect)

def renderGame():
    # Render Player
    player.renderPlayer(screen)
    # Render Pellet
    pellet.renderPellet(screen)
    renderScore()

def outOfBounds(ent1):
    return (
        ent1.x < 0 or 
        ent1.x + BLOCKSIZE > SCREEN_WIDTH or 
        ent1.y < 0 or 
        ent1.y + BLOCKSIZE > SCREEN_HEIGHT
    )

def updateGame():
    global gameOver
    global pellet
    global score
    global gotPellet
    player.updatePos()

    if models.collided(player.getHead(), pellet):
        player.addBlock()
        pellet = models.Pellet(SCREEN_WIDTH, SCREEN_HEIGHT)
        score += 1
        gotPellet = True

    if player.collidedWithSelf() or outOfBounds(player.getHead()):
        gameOver = True

def renderGameOver():
    font = pygame.font.Font('freesansbold.ttf', 32)
    text = font.render('Game Over (Press R to Reset)', True, (0, 255, 0), (0, 0, 255))
    textRect = text.get_rect()
    textRect.center = (pygame.display.get_window_size()[0] // 2, pygame.display.get_window_size()[1] // 2)
    screen.blit(text, textRect)
    renderScore()

def resetGame():
    global gameOver
    global player
    global pellet
    global score
    gameOver = False
    player = models.Player(pygame.display.get_window_size()[0], pygame.display.get_window_size()[1])
    pellet = models.Pellet(SCREEN_WIDTH, SCREEN_HEIGHT)
    score = 0

def processKeyEvent(key):
    dir = None
    if key in [pygame.K_a, pygame.K_LEFT]:
        dir = WEST
    elif key in [pygame.K_w, pygame.K_UP]:
        dir = NORTH
    elif key in [pygame.K_d, pygame.K_RIGHT]:
        dir = EAST
    elif key in [pygame.K_s, pygame.K_DOWN]:
        dir = SOUTH
    elif key == pygame.K_r:
        resetGame()
        return
    
    if dir != None:
        addQ(dir)

def processInput():
    if len(inputQueue) > 0:
        dir = popQ()
        if (dir + 2) % 4 != player.getHead().direction:
            player.updateDir(dir)

def calcReward(prevState, nextState):
    global gotPellet
    if gotPellet:
        gotPellet = False
        return 5

    # Get previous and next distances to the walls
    prev_dist_wall_up, prev_dist_wall_down, prev_dist_wall_left, prev_dist_wall_right = prevState[0][2], prevState[0][3], prevState[0][4], prevState[0][5]
    next_dist_wall_up, next_dist_wall_down, next_dist_wall_left, next_dist_wall_right = nextState[0][2], nextState[0][3], nextState[0][4], nextState[0][5]
    
    # Calculate the minimum distance to the wall for both previous and next state
    prev_min_wall_dist = min(prev_dist_wall_up, prev_dist_wall_down, prev_dist_wall_left, prev_dist_wall_right)
    next_min_wall_dist = min(next_dist_wall_up, next_dist_wall_down, next_dist_wall_left, next_dist_wall_right)
    
    # Get the previous and next distances to the pellet (food_dx, food_dy)
    prev_food_dx, prev_food_dy = prevState[0][0], prevState[0][1]
    next_food_dx, next_food_dy = nextState[0][0], nextState[0][1]
    
    # Calculate the previous and next distance to the pellet
    prev_dist_to_food = np.sqrt(prev_food_dx**2 + prev_food_dy**2)
    next_dist_to_food = np.sqrt(next_food_dx**2 + next_food_dy**2)
    
    # Reward for moving towards the pellet (getting closer)
    if next_dist_to_food < prev_dist_to_food:
        food_reward = 0.5  # Positive reward for moving towards the pellet
    elif next_dist_to_food > prev_dist_to_food:
        food_reward = -0.5  # Negative reward for moving away from the pellet
    else:
        food_reward = 0  # No change in distance to the pellet
    
    # Penalty for getting closer to the wall (moving towards the walls)
    if next_min_wall_dist < prev_min_wall_dist:
        wall_penalty = -0.5  # Negative reward for getting closer to the wall
    elif next_min_wall_dist > prev_min_wall_dist:
        wall_penalty = 0.5  # Positive reward for moving away from the wall
    else:
        wall_penalty = 0  # No change in distance to the wall
    
    # Combine the food and wall rewards
    total_reward = food_reward + wall_penalty

    # If the snake collided with the wall or went out of bounds, apply a large negative penalty
    if gameOver:
        total_reward = -10  # Large penalty for game over
    
    return total_reward


    
    


    
# Game training
num_episodes = 1000  # Train for 1000 games
state_size = 10  # Based on our get_state() function
action_size = 4    
bot = agent.DQNAgent(state_size, action_size)
totalReward = 0

for episode in range(num_episodes):
    episodeDisp = episode
    print(f"Starting Episode {episode} Previous Total {totalReward}")
    state = get_state()  # Get initial state
    state = np.reshape(state, [1, state_size])
    keepRunning = True
    resetGame()
    totalReward = 0

    while keepRunning:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            if event.type == pygame.KEYDOWN:
                processKeyEvent(event.key)

        action = bot.act(state)
        prev_state = state

        addQ(action)

        processInput()
        # fill the screen with a color to wipe away anything from last frame
        screen.fill("black")

        if not gameOver:
            renderGame()
            updateGame()
        else:
            renderGameOver()
            keepRunning = False
            bot.train()

        next_state = get_state()
        next_state = np.reshape(next_state, [1, state_size])

        reward = calcReward(prev_state, next_state)        
        print(reward)

        bot.remember(prev_state, action, reward, next_state, gameOver)

        state = next_state
        totalReward += reward

        # flip() the display to put your work on screen
        pygame.display.flip()

        clock.tick(10)  # limits FPS to 60

pygame.quit()