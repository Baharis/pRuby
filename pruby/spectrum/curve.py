import numpy as np


class Curve:
    def __init__(self, func=lambda x: 0, args=tuple()):
        self.func = func
        self.args = args
        self.uncs = tuple(np.zeros_like(args))

    def __call__(self, *args):
        if len(args) == 1:
            return self.func(*args, *self.args)
        else:
            return self.func(*args)