import numpy as np


class Spectrum:
    def __init__(self, x, y):
        self.x = np.array(x)
        self.y = np.array(y)

    def trim(self, subspace):
        in_subspace = [True if x in subspace else False for x in self.x]
        return Spectrum(x=self.x[in_subspace], y=self.y[in_subspace])


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Curve:
    PRECISION = 1000

    def __init__(self, func, args):
        self.func = func
        self.args = args

    def __call__(self, x):
        return self.func(x, *self.args)

    def trim(self, subspace):
        linspace = np.linspace(min(subspace), max(subspace), self.PRECISION)
        in_subspace = [True if x in subspace else False for x in linspace]
        new_x = linspace[in_subspace]
        new_y = [self(x) for x in new_x]
        return Spectrum(x=new_x, y=new_y)
