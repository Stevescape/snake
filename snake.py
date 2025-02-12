# Test Comment
import pygame
import models
import agent
import numpy as np
import random
import os

NORTH = 0
EAST = 1
SOUTH = 2
WEST = 3
BLOCKSIZE = models.BLOCKSIZE

SCREEN_WIDTH = 720
SCREEN_HEIGHT = 720

def spawnPellet():
    possiblePos = [(x, y) for x in range(0, SCREEN_WIDTH, BLOCKSIZE+10) for y in range(0, SCREEN_HEIGHT, BLOCKSIZE+10)]
    snakePos = player.get_pos()
    validPos = [pos for pos in possiblePos if pos not in snakePos]
    
    pos = random.choice(validPos)

    pellet = models.Pellet(SCREEN_WIDTH, SCREEN_HEIGHT)
    pellet.x, pellet.y = pos
    return pellet

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

    grid_width = [x for x in range(player.getHead().x-((BLOCKSIZE+10)*4), player.getHead().x+((BLOCKSIZE+10)*5), BLOCKSIZE+10)]
    grid_height = [x for x in range(player.getHead().y-((BLOCKSIZE+10)*4), player.getHead().y+((BLOCKSIZE+10)*5), BLOCKSIZE+10)]
    
    grid_pos = [(x, y) for x in grid_width for y in grid_height]
    snake_pos = player.get_pos()[1:]
    food_pos = (food_x, food_y)

    grid = np.zeros((9, 9))
    for tup in grid_pos:
        x = tup[0]
        y = tup[1]
        if tup in snake_pos or coordsOutOfBounds(tup):
            grid[grid_height.index(y)][grid_width.index(x)] = 1
        if tup == (head_x, head_y):
            grid[grid_height.index(y)][grid_width.index(x)] = 2
        if tup == food_pos:
            grid[grid_height.index(y)][grid_width.index(x)] = 3
    
    

    grid = np.array([grid]).reshape(9, 9, 1)

    printGrid(grid)

    # state = np.array([
    #     danger_north,
    #     danger_east,
    #     danger_south,
    #     danger_west,

    #     is_direction_left,
    #     is_direction_right,
    #     is_direction_up,
    #     is_direction_down,

    #     food_left,
    #     food_right,
    #     food_up,
    #     food_down
    # ], dtype=int)

    state = np.array([
        is_direction_left,
        is_direction_right,
        is_direction_up,
        is_direction_down,

        food_left,
        food_right,
        food_up,
        food_down
    ], dtype=int)

    return grid, state

def printGrid(grid):
    for row in grid:
        r = ""
        for elements in row:
            for element in elements:
                if element == 0:
                    r += "⬜"
                elif element == 1:
                    r += "🟥"
                elif element == 2:
                    r += "🟦"
                elif element == 3:
                    r += "⬛"
        print(r)

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

    text = font.render(f'Step: {step_count} Since Last Pellet: {step_last_pellet}', True, (0, 255, 0), (0, 0, 255))
    textRect = text.get_rect()
    textRect.right = SCREEN_WIDTH - 10
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
        ent1.x + BLOCKSIZE+10 > SCREEN_WIDTH or 
        ent1.y < 0 or 
        ent1.y + BLOCKSIZE+10 > SCREEN_HEIGHT
    )

def coordsOutOfBounds(tup):
    return (
        tup[0] < 0 or 
        tup[0] + BLOCKSIZE+10 > SCREEN_WIDTH or 
        tup[1] < 0 or 
        tup[1] + BLOCKSIZE+10 > SCREEN_HEIGHT
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
        pellet = spawnPellet()
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
    global gameOver, player, pellet, score, step_count, step_last_pellet
    gameOver = False
    player = models.Player(pygame.display.get_window_size()[0], pygame.display.get_window_size()[1])
    pellet = spawnPellet()
    score = 0
    step_count = 0
    step_last_pellet = 0

def saveModel():
    i = 1
    while os.path.exists(f"rons/RonV{i}.keras"):
        i += 1
    bot.model.save(f"rons/RonV{i}.keras")

def processKeyEvent(key):
    dir = None
    global clockSpeed
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
    elif key == pygame.K_1:
        clockSpeed = 10
    elif key == pygame.K_2:
        clockSpeed = 20
    elif key == pygame.K_3:
        clockSpeed = 30
    elif key == pygame.K_4:
        clockSpeed = 40
    elif key == pygame.K_5:
        clockSpeed = 50
    elif key == pygame.K_6:
        clockSpeed = 60
    elif key == pygame.K_7:
        clockSpeed = 120
    elif key == pygame.K_0:
        if bot.store == None:
            bot.store = bot.epsilon
            bot.epsilon = 0
        else:
            bot.epsilon = bot.store
            bot.store = None
    elif key == pygame.K_k:
        saveModel()
    elif key == pygame.K_p:
        global pause
        pause = False if pause else True
    
    if dir != None:
        addQ(dir)

def processInput():
    if len(inputQueue) > 0:
        dir = popQ()
        if (dir + 2) % 4 != player.getHead().direction:
            player.updateDir(dir)

def calcReward():
    global gotPellet, step_count, step_last_pellet
    total_reward = 0
    if step_last_pellet > 100:
        total_reward -= 1

    if gotPellet:
        total_reward += 20
        gotPellet = False
        step_last_pellet = 0
        return total_reward
    
    prevDist = np.sqrt((oldPos[0] - pellet.x)**2 + (oldPos[1] - pellet.y)**2)
    curDist = np.sqrt((player.getHead().x - pellet.x)**2 + (player.getHead().y - pellet.y)**2)
    step_last_pellet += 1
    step_count += 1

    if curDist < prevDist:
        total_reward += 0.5
    elif curDist > prevDist:
        total_reward += -1

    # If the snake collided with the wall or went out of bounds, apply a large negative penalty
    if not keepRunning:
        death_amount = -10 + ((bot.generation // 100) * -20)
        if death_amount < death_cap:
            death_amount = death_cap
        death_amount = -10
        total_reward += death_amount  # Large penalty for game over 
        print(f"Death Amount: {death_amount}")
    
    return total_reward

# Game Parameters
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
keepRunning = True
player = models.Player(pygame.display.get_window_size()[0], pygame.display.get_window_size()[1])
score = 0
gameOver = False
gotPellet = False
episodeDisp = 0
oldPos = (player.getHead().x, player.getHead().y)
totalReward = 0
clockSpeed = 10
pellet = spawnPellet()
inputQueue = []
step_count = 0
step_last_pellet = 0
pause = False

# Game Training
num_episodes = 10000  # Train for 1000 games
state_size = 8 # Based on our get_state() function
action_size = 4    
bot = agent.DQNAgent(state_size, action_size)
death_cap = -50

for episode in range(num_episodes):
    print(f"Starting Episode {episode}")
    grid, state = get_state()  # Get initial state
    state = np.reshape(state, [1, state_size])
    keepRunning = True
    totalReward = 0

    while keepRunning:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            if event.type == pygame.KEYDOWN:
                processKeyEvent(event.key)
        if pause:
            continue

        action = bot.act(grid, state)
        prev_state = state
        prev_grid = grid

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

        next_grid, next_state = get_state()
        next_state = np.reshape(next_state, [1, state_size])

        reward = calcReward()
        print(reward)

        bot.remember(prev_grid, prev_state, action, reward, next_grid, next_state, gameOver)

        state = next_state
        grid = next_grid
        totalReward += reward
        totalReward = round(totalReward, 2)

        # flip() the display to put your work on screen
        pygame.display.flip()

        clock.tick(clockSpeed)
    renderScore()
    pygame.display.flip()
    bot.train()
    resetGame()

saveModel()
pygame.quit()