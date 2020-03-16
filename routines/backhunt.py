import numpy as np
from collections import OrderedDict
from scipy.optimize import curve_fit
from ..utility.maths import *


def default():
    return HuberlinearBackhunt


def methods():
    backhunts = HubercubicBackhunt, HuberlinearBackhunt, \
                SatellitelinearBackhunt
    dict_of_methods = OrderedDict()
    for bh in backhunts:
        dict_of_methods[bh.id] = bh
    return dict_of_methods


class TemplateBackhunt:
    def __init__(self):
        self.f = lambda x: 0.0
        self.x = np.array(list(tuple()))
        self.y = np.array(list(tuple()))

    @property
    def areas(self):
        x_beg1 = self.x[0]
        x_end1 = self.x[-1]
        return (x_beg1, x_end1),

    @property
    def curve_dependent_on_x(self):
        return lambda x, *args: self.curve(*args)(x)

    @property
    def mse(self):
        zipped = zip(self.x, self.y, self.sigma)
        e2_sum = sum([((y - self.f(x)) / s) ** 2 for x, y, s in zipped])
        return e2_sum / len(self.x)

    def curve(self, *_):
        return lambda x: 0.0

    def fit(self, dots):
        self.import_dots(dots)
        self.trim_dots_to_areas()
        precision = 1e-1
        mse_change = float('inf')
        max_cycles = 20
        while mse_change > 1 + precision and max_cycles > 0:
            prev_mse = float(self.mse)
            popt, _ = curve_fit(self.curve_dependent_on_x,
                                xdata=self.x, ydata=self.y,
                                p0=self.prediction, sigma=self.sigma)
            self.update_function(popt)
            mse_change = max(self.mse, prev_mse) / min(self.mse, prev_mse)
            max_cycles -= 1

    @property
    def quartile_delta_y(self):
        y_firstlist = list(self.y)[1:]
        y_secondlist = list(self.y)[:-1]
        zipped = zip(y_firstlist, y_secondlist)
        delta_y = list(map(lambda y: abs(y[0] - y[1]), zipped))
        delta_y.sort()
        middle_index = len(delta_y) // 4
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
    id = 'huberlinear_fit'
    name = 'Huber Linear Fit'

    def curve(self, a, b):
        return linear(a, b)

    @property
    def prediction(self):
        return self.prediction_linear

    @property
    def sigma(self):
        s = 2 * self.quartile_delta_y
        delta_y = [y - b for y, b in zip(self.y, map(self.f, self.x))]
        sigmas = [s if d < s else s * (2 * d - s) for d in delta_y]
        return np.array(sigmas)


class HubercubicBackhunt(TemplateBackhunt):
    id = 'hubercubic_fit'
    name = 'Huber Cubic Fit'

    def curve(self, a3, a2, a1, a0):
        return cubic(a3, a2, a1, a0)

    @property
    def prediction(self):
        a1, a0 = self.prediction_linear
        return 0.0, 0.0, a1, a0

    @property
    def sigma(self):
        s = 2 * self.quartile_delta_y
        delta_y = [y - b for y, b in zip(self.y, map(self.f, self.x))]
        sigmas = [s if d < s else s * (2 * d - s) for d in delta_y]
        return np.array(sigmas)


class SatellitelinearBackhunt(TemplateBackhunt):
    id = 'satellitelinear_fit'
    name = 'Satellite Linear Fit'
    satellite_fraction = 0.20

    @property
    def areas(self):
        x_beg = self.x[0]
        x_end = self.x[-1]
        x_span = x_end - x_beg
        x_beg1 = x_beg
        x_end1 = x_beg + x_span * self.satellite_fraction / 2
        x_beg2 = x_end - x_span * self.satellite_fraction / 2
        x_end2 = x_end
        return (x_beg1, x_end1), (x_beg2, x_end2)

    def curve(self, a, b):
        return linear(a, b)

    @property
    def prediction(self):
        return self.prediction_linear
