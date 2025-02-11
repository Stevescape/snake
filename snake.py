import pygame
import models
import agent
import numpy as np

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
oldPos = (player.getHead().x, player.getHead().y)
totalReward = 0

inputQueue = []

# def get_state():
#     head = player.getHead()
#     food_x, food_y = pellet.x, pellet.y
#     head_x, head_y = head.x, head.y
#     direction = head.direction  # Assuming this returns NORTH, EAST, SOUTH, or WEST
    
#     # Relative distance to food
#     food_dx = food_x - head_x
#     food_dy = food_y - head_y

#     # Distance to walls
#     dist_wall_up = head_y
#     dist_wall_down = SCREEN_HEIGHT - (head_y + BLOCKSIZE)
#     dist_wall_left = head_x
#     dist_wall_right = SCREEN_WIDTH - (head_x + BLOCKSIZE)

#     # One-hot encode direction
#     direction_encoding = [0, 0, 0, 0]
#     direction_encoding[direction] = 1

#     # Final state vector
#     state = np.array([
#         food_dx, food_dy,
#         dist_wall_up, dist_wall_down, dist_wall_left, dist_wall_right,
#         *direction_encoding
#     ], dtype=np.float32)

#     return state

def collide_self(player, block):
    tempPlayer = models.Player(SCREEN_WIDTH, SCREEN_HEIGHT)
    block.tail = player.getHead()
    tempPlayer.setHead(block)

    return tempPlayer.collidedWithSelf()

def get_state():
    head = player.getHead()
    food_x, food_y = pellet.x, pellet.y
    head_x, head_y = head.x, head.y
    direction = head.direction  # Assuming this returns NORTH, EAST, SOUTH, or WEST

    # Define possible moves
    block_left = models.Block(head_x - (BLOCKSIZE+10), head_y)
    block_right = models.Block(head_x + (BLOCKSIZE+10), head_y)
    block_up = models.Block(head_x, head_y - (BLOCKSIZE+10))
    block_down = models.Block(head_x, head_y + (BLOCKSIZE+10))

    # Determine dangers (collisions)
    danger_north = outOfBounds(block_up) or collide_self(player, block_up)
    danger_east = outOfBounds(block_right) or collide_self(player, block_right)
    danger_south = outOfBounds(block_down) or collide_self(player, block_down)
    danger_west = outOfBounds(block_left) or collide_self(player, block_left)


    # One-hot encode direction
    is_direction_left = direction == WEST
    is_direction_right = direction == EAST
    is_direction_up = direction == NORTH
    is_direction_down = direction == SOUTH

    # Relative position of pellet
    food_left = food_x < head_x
    food_right = food_x > head_x
    food_up = food_y < head_y
    food_down = food_y > head_y

    state = np.array([
        danger_north,
        danger_east,
        danger_south,
        danger_west,

        is_direction_left,
        is_direction_right,
        is_direction_up,
        is_direction_down,

        food_left,
        food_right,
        food_up,
        food_down
    ], dtype=int)

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
    text = font.render(f'Score: {score} Generation: {bot.generation}', True, (0, 255, 0), (0, 0, 255))
    textRect = text.get_rect()
    textRect.left = 10
    textRect.top = 10
    screen.blit(text, textRect)

    text = font.render(f'Epsilon: {bot.epsilon} Reward Score: {totalReward}', True, (0, 255, 0), (0, 0, 255))
    textRect = text.get_rect()
    textRect.left = 10
    textRect.top = SCREEN_HEIGHT - 20
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
    global oldPos

    oldPos = (player.getHead().x, player.getHead().y)
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

def calcReward():
    global gotPellet
    if gotPellet:
        gotPellet = False
        return 5
    
    prevDist = np.sqrt((oldPos[0] - pellet.x)**2 + (oldPos[1] - pellet.y)**2)
    curDist = np.sqrt((player.getHead().x - pellet.x)**2 + (player.getHead().y - pellet.y)**2)
    total_reward = 0

    if curDist < prevDist:
        total_reward += 0.5
    elif curDist > prevDist:
        total_reward += -0.5

    # If the snake collided with the wall or went out of bounds, apply a large negative penalty
    if not keepRunning:
        total_reward = -10  # Large penalty for game over
    
    return total_reward

# Game training
num_episodes = 1000  # Train for 1000 games
state_size = 12  # Based on our get_state() function
action_size = 4    
bot = agent.DQNAgent(state_size, action_size)

for episode in range(num_episodes):
    print(f"Starting Episode {episode}")
    state = get_state()  # Get initial state
    state = np.reshape(state, [1, state_size])
    keepRunning = True
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

        next_state = get_state()
        next_state = np.reshape(next_state, [1, state_size])

        reward = calcReward()        
        print(reward)

        bot.remember(prev_state, action, reward, next_state, gameOver)

        state = next_state
        totalReward += reward

        # flip() the display to put your work on screen
        pygame.display.flip()

        clock.tick(10)     
    bot.train()
    resetGame()

pygame.quit()