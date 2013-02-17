import pygame

HUMAN = pygame.image.load('human.png')

class Entity(object):
    def __init__(self, pos, image):
        self.pos    = pos
        self.image  = image

class Human(Entity):
    def __init__(self, pos):
        super(Human, self).__init__(pos, HUMAN)

