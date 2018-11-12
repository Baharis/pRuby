import numpy as np
from collections import OrderedDict
from scipy.optimize import curve_fit


def default():
    return HuberlinearBackhunt


def methods():
    backhunts = HuberlinearBackhunt, SatellitelinearBackhunt
    dict_of_methods = OrderedDict()
    for bh in backhunts:
        dict_of_methods[bh.id] = bh
    return dict_of_methods


def linear(a, b):
    return lambda x: a * x + b


def quadratic(a, b, c):
    return lambda x: a * x**2 + b * x + c


class TemplateBackhunt:
    def __init__(self):
        self.f = lambda x: 0.0
        self.x = np.array(list(tuple()))
        self.y = np.array(list(tuple()))

    @property
    def areas(self):
        x_beg1 = float('-inf')
        x_end1 = float('inf')
        return (x_beg1, x_end1),

    @property
    def mse(self):
        zipped = zip(self.x, self.y, self.sigma)
        e2_sum = sum([((y - self.f(x)) / s) ** 2 for x, y, s in zipped])
        return e2_sum / len(self.x)

    def curve(self, *_):
        return lambda x: 0.0

    @property
    def curve_dependent_on_x(self):
        return lambda x, *args: self.curve(*args)(x)

    def fit(self, dots):
        self.import_dots(dots)
        self.trim_dots_to_areas()
        precision = 1e-3 * self.median_delta_y
        delta_mse = float('inf')
        while delta_mse > precision:
            previous_mse = self.mse
            popt, _ = curve_fit(self.curve_dependent_on_x,
                                xdata=self.x, ydata=self.y,
                                p0=self.prediction, sigma=self.sigma)
            delta_mse = abs(self.mse - previous_mse)
        self.update_function(popt)

    @property
    def median_delta_y(self):
        y_firstlist = list(self.y)[1:]
        y_secondlist = list(self.y)[:-1]
        zipped = zip(y_firstlist, y_secondlist)
        delta_y = list(map(lambda y1, y2: abs(y1 - y2), zipped))
        delta_y.sort()
        middle_index = len(delta_y) // 2
        return delta_y[middle_index]

    def import_dots(self, dots):
        self.x = np.array(dots[:, 0])
        self.y = np.array(dots[:, 1])

    @property
    def prediction(self):
        return tuple()

    @property
    def prediction_linear(self):
        a = (self.y[-1] - self.y[0]) / (self.x[-1] - self.x[0])
        b = self.y[0] - a * self.x[0]
        return a, b

    @property
    def sigma(self):
        return np.ones(len(self.x))

    def trim_dots_to_areas(self):
        indices_in_area = np.zeros(len(self.x), dtype=bool)
        for area in self.areas:
            left, right = area
            for i, x in enumerate(self.x):
                if left <= x <= right:
                    indices_in_area[i] = True
        self.x = self.x[indices_in_area]
        self.y = self.y[indices_in_area]

    def update_function(self, popt):
        self.f = lambda x: self.curve(*popt)(x)


class HuberlinearBackhunt(TemplateBackhunt):

    @property
    def prediction(self):
        return self.prediction_linear

    @property
    def sigma(self):
        s = self.median_delta_y
        delta_y = [y - b for y, b in zip(self.y, map(self.f, self.x))]
        sigmas = [d ** -2 if d < s else 1 / (s * (2 * d - s)) for d in delta_y]
        return np.array(sigmas)


class SatellitelinearBackhunt(TemplateBackhunt):
    satellite_fraction = 0.20

    @property
    def areas(self):
        x_beg = self.x[0]
        x_end = self.x[-1]
        x_span = x_end - x_beg
        x_beg1 = float('-inf')
        x_end1 = x_beg + x_span * self.satellite_fraction / 2
        x_beg2 = x_end - x_span * self.satellite_fraction / 2
        x_end2 = float('inf')
        return (x_beg1, x_end1), (x_beg2, x_end2)

    @property
    def prediction(self):
        return self.prediction_linear


