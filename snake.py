import pygame
import models

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

def renderScore():
    font = pygame.font.Font('freesansbold.ttf', 10)
    text = font.render(f'Score {score}', True, (0, 255, 0), (0, 0, 255))
    textRect = text.get_rect()
    textRect.center = (25, 15)
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
    player.updatePos()

    if models.collided(player.getHead(), pellet):
        player.addBlock()
        pellet = models.Pellet(SCREEN_WIDTH, SCREEN_HEIGHT)
        score += 1

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
    if key == pygame.K_a:
        player.updateDir(WEST)
    elif key == pygame.K_w:
        player.updateDir(NORTH)
    elif key == pygame.K_d:
        player.updateDir(EAST)
    elif key == pygame.K_s:
        player.updateDir(SOUTH)
    elif key == pygame.K_r:
        resetGame()

while keepRunning:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            keepRunning = False
        if event.type == pygame.KEYDOWN:
            processKeyEvent(event.key)

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("black")

    if not gameOver:
        renderGame()
        updateGame()
    else:
        renderGameOver()

    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(10)  # limits FPS to 60

pygame.quit()