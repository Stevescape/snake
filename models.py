import pygame

NORTH = 0
EAST = 1
SOUTH = 2
WEST = 3

class Player:
    def __init__(self, screenX, screenY):
        head = Block()
        head.setX(screenX//2) 
        head.setY(screenY//2)
        head.setDir(NORTH)
        self.head = head

    def setHead(self, head):
        self.head = head
    
    def getHead(self):
        return self.head
    
    def addBlock(self, x, y, dir):
        new = Block()
        new.setX(x)
        new.setY(y)
        new.setDir(dir)
        self.head.addToTail(new)

    def renderPlayer(self, screen):
        self.head.renderBlock(screen)
        
        

class Block:
    def __init__(self):
        self.tail = None
        self.x = None
        self.y = None
        self.direction = NORTH
    
    def setTail(self, node):
        self.tail = node
    
    def setX(self, xpos):
        self.x = xpos

    def setY(self, ypos):
        self.y = ypos
    
    def setDir(self, direction):
        self.direction = direction

    def addToTail(self, block):
        if (self.tail == None):
            self.tail = block
            return
        self.addToTail(self.tail)

    def renderBlock(self, screen):
        rect = (self.x, self.y, 20, 20)
        pygame.draw.rect(screen, (0, 255, 0), rect, 0)
        if self.tail != None:
            self.tail.renderBlock(screen)