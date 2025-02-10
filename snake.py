import pygame
import models

NORTH = 0
EAST = 1
SOUTH = 2
WEST = 3

pygame.init()
screen = pygame.display.set_mode((720, 720))
clock = pygame.time.Clock()
keepRunning = True
player = models.Player(pygame.display.get_window_size()[0], pygame.display.get_window_size()[1])

def renderPlayer():
    player.renderPlayer(screen)

def renderGame():
    renderPlayer()

while keepRunning:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            keepRunning = False

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("black")

    renderGame()

    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(60)  # limits FPS to 60

pygame.quit()