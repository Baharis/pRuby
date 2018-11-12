import numpy as np
from collections import OrderedDict
from scipy.signal import find_peaks_cwt
from scipy.optimize import curve_fit, minimize_scalar

fit_range = 0.40
# TODO add background subtraction deinitely


def default():
    return GaussPeakhunt


def methods():
    peakhunts = GaussPeakhunt, GausslorentzPeakhunt, PseudovoigtPeakhunt
    dict_of_methods = OrderedDict()
    for ph in peakhunts:
        dict_of_methods[ph.id] = ph
    return dict_of_methods


def gauss(a, mu, si):
    """	Input:  a, mu, si - gaussian coeffitients               (float)
        Return:	gauss function of an 'x' parameter              (float)
        Descr.: Produce G(x)-type function with fixed parameters"""
    return lambda x: a * np.exp(-(x - mu) ** 2 / (2. * si ** 2))


def lorentz(a, mu, ga):
    """	Input: x - value and a=I, mu=x_0, ga - lorentz f. coeffitients  (float)
        Return:	value of function with desired parameters in x (float)
        Descr.: Calculate L-type function for given x and parameters"""
    return lambda x: (a * ga ** 2) / ((x - mu) ** 2 + ga ** 2)


class TemplatePeakhunt:
    fit_range_multiplier = 1.0

    def __init__(self):
        self.f = lambda x: 0.0
        self.mse = float('inf')
        self.r1_int = float()
        self.r1_val = float()
        self.r1_unc = float()
        self.r2_int = float()
        self.r2_val = float()
        self.r2_unc = float()
        self.x = np.array(list(tuple()))
        self.y = np.array(list(tuple()))

    @property
    def areas(self):
        x_beg1 = self.r2_val - fit_range * self.fit_range_multiplier
        x_end1 = self.r2_val + fit_range * self.fit_range_multiplier
        x_beg2 = self.r1_val - fit_range * self.fit_range_multiplier
        x_end2 = self.r1_val + fit_range * self.fit_range_multiplier
        return (x_beg1, x_end1), (x_beg2, x_end2)

    def calculate_mse(self):
        e2_sum = sum([(y - self.f(x)) ** 2 for x, y in zip(self.x, self.y)])
        self.mse = e2_sum / len(self.x)
        print(self.mse)

    def curve(self, *_):
        return lambda x: 0.0

    @property
    def curve_dependent_on_x(self):
        return lambda x, *args: self.curve(*args)(x)

    def find_peak_candidates(self):
        peak_indexes = find_peaks_cwt(vector=self.y, widths=[5, 5, 5, 5, 5])
        peaks = np.array([(self.x[i], self.y[i]) for i in peak_indexes])
        peaks = peaks[peaks[:, 1].argsort()[::-1]]
        second_not_found = len(peaks) == 1
        second_out_of_range = not(peaks[0][0] - 2 < peaks[1][0] < peaks[0][0])
        if second_not_found or second_out_of_range:
            peaks = np.array(((peaks[0, 0], peaks[0, 1]),
                              (peaks[0, 0] - 1.5, 0.5 * peaks[0, 1])))
        self.r1_val = peaks[0, 0]
        self.r1_unc = 1.0
        self.r1_int = peaks[0, 1]
        self.r2_val = peaks[1, 0]
        self.r2_unc = 1.0
        self.r2_int = peaks[1, 1]

    def fit(self, dots):
        self.import_dots(dots=dots)
        self.find_peak_candidates()
        self.trim_dots_to_areas()
        one_over_y = [1/max(abs(y), 1e-9) for y in self.y]
        popt, pcov = curve_fit(self.curve_dependent_on_x,
                               xdata=self.x, ydata=self.y,
                               p0=self.prediction, sigma=one_over_y)
        popt, pcov = curve_fit(self.curve_dependent_on_x,
                               xdata=self.x, ydata=self.y, p0=popt)
        sigma = np.sqrt(np.diag(pcov))
        self.update_function(popt)
        self.update_r1_and_r2_horizontal(popt, sigma)
        self.update_r1_and_r2_vertical()
        self.calculate_mse()

    def import_dots(self, dots):
        self.x = np.array(dots[:, 0])
        self.y = np.array(dots[:, 1])

    @property
    def peak_broadening(self):
        return 1.0 + 0.1 * (self.r1_val - 695.0)

    @property
    def prediction(self):
        return tuple()

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

    def update_r1_and_r2_horizontal(self, popt, sigma):
        pass

    def update_r1_and_r2_vertical(self):
        self.r1_int = self.f(self.r1_val)
        self.r2_int = self.f(self.r2_val)


class GaussPeakhunt(TemplatePeakhunt):
    id = 'gauss_fit'
    name = 'Gauss Fit'
    fit_range_multiplier = 1.0

    def curve(self, a1, mu1, si1, a2, mu2, si2):
        return lambda x: gauss(a1, mu1, si1)(x) + gauss(a2, mu2, si2)(x)

    @property
    def prediction(self):
        a1 = self.r1_int
        mu1 = self.r1_val
        si1 = 0.25 * self.peak_broadening
        a2 = self.r2_int
        mu2 = self.r2_val
        si2 = 0.25 * self.peak_broadening
        return a1, mu1, si1, a2, mu2, si2

    def update_r1_and_r2_horizontal(self, popt, sigma):
        self.r1_val = popt[1]
        self.r1_unc = sigma[1]
        self.r2_val = popt[4]
        self.r2_unc = sigma[4]


class GausslorentzPeakhunt(TemplatePeakhunt):
    id = 'gausslorentz_fit'
    name = 'Gauss-Lorentz Fit'
    fit_range_multiplier = 3.0

    def curve(self, a1, mu1, si1, b1, ga1, a2, mu2, si2, b2, ga2):
        return lambda x: gauss(a2, mu2, si2)(x) + lorentz(b2, mu2, ga2)(x) + \
                         gauss(a1, mu1, si1)(x) + lorentz(b1, mu1, ga1)(x)

    @property
    def prediction(self):
        a1 = 0.75 * self.r1_int
        mu1 = self.r1_val
        si1 = 0.25 * self.peak_broadening
        b1 = 0.25 * self.r1_int
        ga1 = 0.50 * self.peak_broadening
        a2 = 0.75 * self.r2_int
        mu2 = self.r2_val
        si2 = 0.25 * self.peak_broadening
        b2 = 0.25 * self.r2_int
        ga2 = 0.25 * self.peak_broadening
        return a1, mu1, si1, b1, ga1, a2, mu2, si2, b2, ga2

    def update_r1_and_r2_horizontal(self, popt, sigma):
        self.r1_val = popt[1]
        self.r1_unc = sigma[1]
        self.r2_val = popt[6]
        self.r2_unc = sigma[6]


class PseudovoigtPeakhunt(TemplatePeakhunt):
    id = 'pseudovoigt_fit'
    name = 'Pseudo-Voigt Fit'
    fit_range_multiplier = 3.0

    def curve(self, a1, mu1, w1, et1, a2, mu2, w2, et2):
        si2 = w2 / (np.sqrt(8 * np.log(2)))
        si1 = w1 / (np.sqrt(8 * np.log(2)))
        ga2 = w2 / 2
        ga1 = w1 / 2
        return lambda x: et1 * gauss(a2, mu2, si2)(x) + \
                         (1 - et1) * lorentz(a2, mu2, ga2)(x) + \
                         et2 * gauss(a1, mu1, si1)(x) + \
                         (1 - et2) * lorentz(a1, mu1, ga1)(x)

    @property
    def prediction(self):
        a1 = self.r1_int
        mu1 = self.r1_val
        w1 = 0.6 * self.peak_broadening
        et1 = 0.5
        a2 = self.r2_int
        mu2 = self.r2_val
        w2 = 0.6 * self.peak_broadening
        et2 = 0.25
        return a1, mu1, w1, et1, a2, mu2, w2, et2

    def update_r1_and_r2_horizontal(self, popt, sigma):
        self.r1_val = popt[1]
        self.r1_unc = sigma[1]
        self.r2_val = popt[5]
        self.r2_unc = sigma[5]


# class CamelPeakhunt(TemplatePeakhunt):
#     def __init__(self):
#         super().__init__()
#         self.id = 'camel_fit'
#         self.name = 'Camel Fit'
#         self.fit_range_multiplier = 2.0
#
#     def curve(self, a1, mu1, si1, a2, mu2, si2, a0, mu0, si0):
#         return lambda x: gauss(a2, mu2, si2)(x) + gauss(a1, mu1, si1)(x) \
#                          + gauss(a0, mu0, si0)(x)
#
#     @property
#     def prediction(self):
#         si1, si2, si0 = 0.35, 0.35, 1.0
#         mu1, mu2, mu0 = self.r1_val, self.r2_val, (self.r1_val + self.r2_val)/2
#         a1, a2, a0 = self.r1_int, self.r2_int, (self.r1_int + self.r2_int)/10
#         return a1, mu1, si1, a2, mu2, si2, a0, mu0, si0
