import threading
import time
import pygame

TICK_TIME = 0.1

class Simulator(threading.Thread):
    def __init__(self):
        super(Simulator, self).__init__()
        self.daemon     = True
        # TODO instead of a simple list this should be a quadtree
        self.entities   = []
        self.tick       = 0

    def run(self):
        self.running = True
        while self.running:
            self.tick += 1
            time.sleep(TICK_TIME)

    def stop(self):
        self.running = False

    def get_entities(self, viewport):
        def visible(entity):
            return viewport.contains(pygame.Rect(entity.pos, (1, 1)))
        return filter(visible, self.entities)

    def add_entity(self, entity):
        self.entities.append(entity)

