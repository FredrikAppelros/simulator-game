import threading
import time

TICK_TIME = 0.1

class Simulator(threading.Thread):
    def __init__(self):
        super(Simulator, self).__init__()
        self.daemon = True

    def run(self):
        self.running = True
        while self.running:
            time.sleep(TICK_TIME)

    def stop(self):
        self.running = False

    def get_entities(self, pos, size):
        return []

