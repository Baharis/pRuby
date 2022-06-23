import enum
import numpy as np

from .curve import Curve
from ..utility.line_subset import LineSubset


class Spectrum:
    class SigmaType(enum.Enum):
        equal = 'equal'
        huber = 'huber'

    def __init__(self, x=tuple(), y=tuple(), curve=Curve(),
                 focus=LineSubset(), sigma_type='equal'):
        self.x = np.array(x)
        self.y = np.array(y)
        self.curve = curve
        self.focus = self.domain if focus == LineSubset() else focus
        self.sigma_type = sigma_type

    def __len__(self):
        return len(self.x)

    def __bool__(self):
        return len(self.x) > 0

    @property
    def sigma_type(self):
        return self._sigma_type

    @sigma_type.setter
    def sigma_type(self, value):
        self._sigma_type = self.SigmaType(value)

    @property
    def f(self):
        return np.array(list(map(self.curve, self.x)))

    @property
    def delta(self):
        return self.y - self.f

    @property
    def si(self):
        if self.sigma_type == self.SigmaType.equal:
            return np.ones_like(self.x)
        elif self.sigma_type == self.SigmaType.huber:
            tol = 0.01 * max(abs(self.delta))
            return np.array([tol ** 2 if d < tol else
                             tol * (2 * d - tol) for d in self.delta])
        else:
            raise KeyError('Unknown sigma type "{}"'.format(self.sigma_type))

    @property
    def mse(self):
        return sum((self.delta / self.si) ** 2) / len(self.delta)

    @property
    def domain(self):
        if len(self.x) == 0:
            return LineSubset()
        else:
            return LineSubset(min(self.x), max(self.x))

    @property
    def focused(self):
        return self.within(self.focus)

    def within(self, subset):
        in_subset = [True if x in subset else False for x in self.x]
        return Spectrum(self.x[in_subset], self.y[in_subset], curve=self.curve,
                        focus=subset, sigma_type=self.sigma_type.value)

    def focus_on_edge(self, width=1.0):
        sub1 = LineSubset(min(self.x), min(self.x) + width)
        sub2 = LineSubset(max(self.x) - width, max(self.x))
        self.focus = sub1 + sub2

    def focus_on_whole(self):
        self.focus = self.domain

    def focus_on_points(self, points, width=1.0):
        points_area = LineSubset([(p - width/2, p + width/2) for p in points])
        self.focus = points_area * self.domain
