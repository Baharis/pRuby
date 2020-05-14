import numpy as np
from copy import deepcopy
from pruby.utility.line_subset import LineSubset


class Spectrum:

    def __init__(self, x=tuple(), y=tuple()):
        self.x = np.array(x)
        self.y = np.array(y)

    def within(self, subspace):
        in_subspace = [True if x in subspace else False for x in self.x]
        new = deepcopy(self)
        new.x = self.x[in_subspace]
        new.y = self.y[in_subspace]
        return new



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
