import numpy as np


class Spectrum:
    def __init__(self, x=tuple(), y=tuple()):
        self.x = np.array(x)
        self.y = np.array(y)

    def __len__(self):
        return len(self.x)


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Curve:
    PRECISION = 1000

    def __init__(self, func, args):
        self.func = func
        self.args = args
        self.uncs = np.zeros_like(args)

    def __call__(self, *args):
        return self.func(*args)

    @property
    def fixed(self):
        return Curve(func=lambda x: self(x, self.args), args=tuple())

    def project(self, subspace):
        linspace = np.linspace(min(subspace), max(subspace), self.PRECISION)
        in_subspace = [True if x in subspace else False for x in linspace]
        new_x = linspace[in_subspace]
        new_y = tuple([self.fixed(x) for x in new_x])
        return Spectrum(x=new_x, y=new_y)
