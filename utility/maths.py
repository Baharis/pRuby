import numpy as np


def polynomial(*coefficients):
    return lambda x: sum([c * x ** i for i, c in enumerate(coefficients)])


def gaussian(a, mu, si):
    return lambda x: a * np.exp(-(x - mu) ** 2 / (2. * si ** 2))


def lorentzian(a, mu, ga):
    return lambda x: (a * ga ** 2) / ((x - mu) ** 2 + ga ** 2)


class LinearSubspace:
    
    class LinearSubspaceSegment:
        def __init__(self, start, stop):
            self.start = min(start, stop)
            self.stop = max(start, stop)

        def __contains__(self, item):
            return self.start <= item <= self.stop

        def is_joint_with(self, other):
            return any((self.start in other, self.stop in other,
                        other.start in self, other.stop in self))

        def union(self, other):
            self.start = min(self.start, other.start)
            self.stop = min(self.stop, other.stop)

    def __init__(self, start, stop):
        self.segments = [self.LinearSubspaceSegment(start, stop)]

    def __add__(self, other):
        self.segments.append(other)
        self._merge()

    def __contains__(self, item):
        return any(item in sub for sub in self.segments)

    def _merge(self):
        sorted_segments = sorted(self.segments, key=lambda x: x.start)
        new_segments = [sorted_segments[0]]
        for segment in sorted_segments[1:]:
            if segment.is_joint_with(new_segments[-1]):
                new_segments[-1].union(segment)
            else:
                new_segments.append(segment)
        self.segments = new_segments
