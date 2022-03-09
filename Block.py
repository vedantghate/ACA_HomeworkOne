import math


class Block:
    def __init__(self):
        self.tag = ""
        self.instruction = ""
        self.time = -math.inf
        self.isDirty = False
        self.isValid = False

