import numpy as np


class Spectrum:
    def __init__(self, x=tuple(), y=tuple()):
        self.x = np.array(x)
        self.y = np.array(y)

    def __len__(self):
        return len(self.x)

    def __iter__(self):
        yield from list(zip(self.x, self.y))

    def trim(self, limits):
        new_points = [point for point in list(self) if point[0] in limits]
        self.x = np.array([point[0] for point in new_points])
        self.y = np.array([point[1] for point in new_points])


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
        if len(args) == 1:
            return self.func(*args, *self.args)
        else:
            return self.func(*args)

    def project(self, subspace):
        linspace = np.linspace(min(subspace), max(subspace), self.PRECISION)
        in_subspace = [True if x in subspace else False for x in linspace]
        new_x = linspace[in_subspace]
        new_y = tuple([self(x) for x in new_x])
        return Spectrum(x=new_x, y=new_y)
    # TODO eventually move this to drawing routines