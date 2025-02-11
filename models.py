import pygame
import random

NORTH = 0
EAST = 1
SOUTH = 2
WEST = 3
BLOCKSIZE = 20

def collided(ent1, ent2):
    return (
        ent1.x < ent2.x + BLOCKSIZE and
        ent1.x + BLOCKSIZE > ent2.x and
        ent1.y < ent2.y + BLOCKSIZE and
        ent1.y + BLOCKSIZE > ent2.y
    )

class Player:
    def __init__(self, screenX, screenY):
        head = Block()
        head.setX(screenX//2) 
        head.setY(screenY//2)
        head.setDir(NORTH)
        self.head = head
        self.addBlock()
        self.addBlock()
        self.addBlock()
        self.addBlock()

    def setHead(self, head):
        self.head = head
    
    def getHead(self):
        return self.head
    
    def addBlock(self):
        self.head.addToTail()

    def renderPlayer(self, screen):
        self.head.renderBlock(screen, (0, 255, 255))

    def updatePos(self):
        self.head.updatePos()

    def updateDir(self, dir):
        self.head.setDir(dir)

    def collidedWithSelf(self):
        return self.collideTail(self.head.tail)
    
    def collideTail(self, tail):
        if tail == None:
            return False

        if collided(self.head, tail):
            return True
        else:
            return self.collideTail(tail.tail)
        
        
class Pellet:
    def __init__(self, width, height):
        self.x = random.randint(0, width)
        self.y = random.randint(0, height)
        
        self.x = self.x - (self.x % 30)
        self.y = self.y - (self.y % 30)

        
    def renderPellet(self, screen):
        rect = (self.x, self.y, BLOCKSIZE, BLOCKSIZE)
        pygame.draw.rect(screen, (255, 255, 255), rect, 0)


class Block:
    def __init__(self, x=None, y=None):
        self.tail = None
        self.x = x
        self.y = y
        self.speed = BLOCKSIZE+10
        self.direction = NORTH


    def setTail(self, node):
        self.tail = node
    
    def setSpeed(self, speed):
        self.speed = speed

    def setX(self, xpos):
        self.x = xpos

    def setY(self, ypos):
        self.y = ypos
    
    def setDir(self, direction):
        self.direction = direction

    def addToTail(self):
        if (self.tail == None):
            new = Block()
            diff = BLOCKSIZE + 10
            if self.direction == NORTH:
                new.setX(self.x)
                new.setY(self.y + diff)
            elif self.direction == EAST:
                new.setX(self.x - diff)
                new.setY(self.y)
            elif self.direction == SOUTH:
                new.setX(self.x)
                new.setY(self.y - diff)
            else:
                new.setX(self.x + diff)
                new.setY(self.y)
            new.setDir(self.direction)
            self.tail = new
            return
        self.tail.addToTail()

    def renderBlock(self, screen, color):
        rect = (self.x, self.y, BLOCKSIZE, BLOCKSIZE)
        pygame.draw.rect(screen, color, rect, 0)
        if self.tail != None:
            self.tail.renderBlock(screen, (0, 255, 0))

    def updatePos(self):
        if self.tail != None:
            self.tail.updatePos()

        if self.direction == NORTH:
            self.setY(self.y - self.speed)
        elif self.direction == EAST:
            self.setX(self.x + self.speed)
        elif self.direction == SOUTH:
            self.setY(self.y + self.speed)
        else:
            self.setX(self.x - self.speed)
        
        if self.tail != None:
            self.tail.setDir(self.direction)
        