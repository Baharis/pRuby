import numpy as np
from copy import deepcopy
from pruby.utility.line_subset import LineSubset


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


class Spectrum:
    def __init__(self, x=tuple(), y=tuple(), curve=Curve(),
                 focus=LineSubset(), sigma_type='equal'):
        self.x = np.array(x)
        self.y = np.array(y)
        self.curve = curve
        self.focus = self.domain if focus == LineSubset() else focus
        self.sigma_type = sigma_type   # 'equal' or 'huber'

    @property
    def f(self):
        return np.array(list(map(self.curve, self.x)))

    @property
    def diff(self):
        return self.y - self.f

    @property
    def si(self):
        if self.sigma_type == 'equal':
            return np.ones_like(self.x)
        elif self.sigma_type == 'huber':
            tol = 0.05 * max(abs(self.diff))
            return np.array([tol ** 2 if d < tol else
                             tol * (2 * d - tol) for d in self.diff])
        else:
            raise KeyError('Unknown sigma type "{}"'.format(self.sigma_type))

    @property
    def mse(self):
        return sum((self.diff / self.si) ** 2) / len(self.diff)

    @property
    def domain(self):
        return LineSubset(min(self.x), max(self.x))

    @property
    def focused(self):
        return self.within(self.focus)

    def within(self, subspace):
        in_subspace = [True if x in subspace else False for x in self.x]
        return Spectrum(x=self.x[in_subspace], y=self.y[in_subspace],
                        curve=self.curve, focus=subspace)

    def focus_on_edge(self, length=1):
        sub1 = LineSubset(min(self.x), min(self.x) + length)
        sub2 = LineSubset(max(self.x) - length, max(self.x))
        self.focus = sub1 + sub2

    def focus_on_whole(self):
        self.focus = self.domain

    def focus_on_points(self, points, width=1.0):
        self.focus = LineSubset([(p - width/2, p + width/2) for p in points])
