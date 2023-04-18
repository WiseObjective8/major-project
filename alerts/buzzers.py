import pyfirmata as pf

class Buzzers:
    def __init__(self):
        self.board = pf.Arduino('COM5')
