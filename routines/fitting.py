import numpy as np
from scipy.optimize import curve_fit as scipy_fit
from scipy.signal import find_peaks_cwt
from uncertainties import ufloat
from .base import RoutineManager
from ..utility.maths import polynomial, gaussian, lorentzian
from ..pruby.spectrum import Curve, Spectrum, Point
from utility.maths import LinearSubspace


class BaseFitRoutine:
    def __init__(self):
        self.spectrum = Spectrum(x=[], y=[])
        self.curve = Curve(func=lambda x: 0, args=[])
        self.sigmas = self.sigmas_equal
        self.focus = self.focus_on_whole()

    @property
    def curve_linear(self):
        def curve_func(x, _a0, _a1):
            return polynomial(a0, a1)(x)
        a1 = (self.spectrum.y[-1] - self.spectrum.y[0]) / \
             (self.spectrum.x[-1] - self.spectrum.x[0])
        a0 = self.spectrum.y[0] - a1 * self.spectrum.x[0]
        return Curve(func=curve_func, args=(a0, a1))

    @property
    def curve_two_gaussians(self):
        def curve_func(x, _a1, _mu1, _si1, _a2, _mu2, _si2):
            return gaussian(_a1, _mu1, _si1)(x) + gaussian(_a2, _mu2, _si2)(x)
        mu1, a1, mu2, a2 = self.spectrum_peaks
        si1 = si2 = 0.3
        return Curve(func=curve_func, args=(a1, mu1, si1, a2, mu2, si2))

    @property
    def curve_two_pseudovoigts(self):
        def curve_func(x, _a1, _mu1, _w1, _et1, _a2, _mu2, _w2, _et2):
            si1, ga1 = _w1 / (np.sqrt(8 * np.log(2))), _w1 / 2
            si2, ga2 = _w2 / (np.sqrt(8 * np.log(2))), _w2 / 2
            return _et1 * gaussian(_a1, _mu1, si1)(x) + \
                   (1 - _et1) * lorentzian(_a1, _mu1, ga1)(x) + \
                   _et2 * gaussian(_a2, _mu2, si2)(x) + \
                   (1 - _et2) * lorentzian(_a2, _mu2, ga2)(x)
        mu1, a1, mu2, a2 = self.spectrum_peaks
        w1 = w2 = 0.6
        et1 = et2 = 0.5
        return Curve(func=curve_func, args=(a1, mu1, w1, et1, a2, mu2, w2, et2))

    @property
    def spectrum_peaks(self):
        x, y = self.spectrum.x, self.spectrum.y
        caret_width = int(0.5 / ((max(x) - min(x)) / len(self.spectrum)))
        peak_indices = find_peaks_cwt(y, [caret_width] * 5)
        peaks = np.array([(x[i], y[i]) for i in peak_indices])
        peaks = peaks[peaks[:, 1].argsort()[::-1]]
        r1_x, r1_y = peaks[0, 0], peaks[0, 1]
        if len(peaks) == 1 or not(peaks[0][0] - 2 < peaks[1][0] < peaks[0][0]):
            r2_x, r2_y = r1_x * (1 - 0.002), r1_y * 0.6
        else:
            r2_x, r2_y = peaks[1, 0], peaks[1, 1]
        return r1_x, r1_y, r2_x, r2_y

    def focus_on_whole(self):
        x_min = min(self.spectrum.x)
        x_max = max(self.spectrum.x)
        return LinearSubspace(x_min, x_max)

    def focus_on_edge(self, edge_fraction=0.1):
        x_min = min(self.spectrum.x)
        x_max = max(self.spectrum.x)
        sub1 = LinearSubspace(x_min, x_min + edge_fraction * (x_max - x_min))
        sub2 = LinearSubspace(x_max - edge_fraction * (x_max - x_min), x_max)
        return sub1 + sub2

    def focus_on_peaks(self, peak_width=0.5):
        r1_x, r1_y, r2_x, r2_y = self.spectrum_peaks
        sub1 = LinearSubspace(r1_x - peak_width / 2, r1_x + peak_width / 2)
        sub2 = LinearSubspace(r2_x - peak_width / 2, r2_x + peak_width / 2)
        return sub1 + sub2

    @property
    def sigmas_equal(self):
        return np.ones_like(self.spectrum.x)

    @property
    def sigmas_huber(self):
        diff = self.delta
        lim = 0.05 * max(abs(diff))
        sigmas = [lim ** 2 if d < lim else lim * (2 * d - lim) for d in diff]
        return np.array(sigmas)

    @property
    def delta(self):
        return self.spectrum.y - np.array(map(self.curve, self.spectrum.x))

    @property
    def mse(self):
        return sum((self.delta / self.sigmas) ** 2) / len(self.spectrum.x)

    def point_from_curve_arguments(self, x_arg, y_arg):
        return Point(x=ufloat(self.curve.args[x_arg], self.curve.uncs[x_arg]),
                     y=ufloat(self.curve.args[y_arg], self.curve.uncs[y_arg]))

    def fit(self):
        precision = 1e-10
        cycle, max_cycles = 0, 50
        while True:
            prev_mse = self.mse
            cycle += 1
            xdata = self.spectrum.x[[x in self.focus for x in self.spectrum.x]]
            ydata = self.spectrum.y[[x in self.focus for x in self.spectrum.x]]
            sigma = self.sigmas[[x in self.focus for x in self.spectrum.x]]
            popt, pcov = scipy_fit(self.curve, xdata=xdata, ydata=ydata,
                                   p0=self.curve.args, sigma=sigma)
            if prev_mse / self.mse - 1 > precision or cycle == max_cycles:
                break
        self.curve.args = popt
        self.curve.uncs = pcov


class HuberBackgroundFitRoutine(BaseFitRoutine):
    name = 'Linear Huber'

    def __init__(self):
        super().__init__()
        self.curve = self.curve_linear
        self.focus = self.focus_on_whole()
        self.sigmas = self.sigmas_huber


class SateliteBackgroundFitRoutine(BaseFitRoutine):
    name = 'Linear Satelite'

    def __init__(self):
        super().__init__()
        self.curve = self.curve_linear
        self.focus = self.focus_on_edge(edge_fraction=0.1)
        self.sigmas = self.sigmas_equal


class GaussianSignalFitRoutine(BaseFitRoutine):
    name = 'Gaussian'

    def __init__(self):
        super().__init__()
        self.curve = self.curve_two_gaussians
        self.focus = self.focus_on_peaks(peak_width=0.5)
        self.sigmas = self.sigmas_equal

    @property
    def r1(self):
        return self.point_from_curve_arguments(x_arg=1, y_arg=0)

    @property
    def r2(self):
        return self.point_from_curve_arguments(x_arg=4, y_arg=3)


class PseudovoigtSignalFitRoutine(BaseFitRoutine):
    name = 'Pseudovoigt'

    def __init__(self):
        super().__init__()
        self.curve = self.curve_two_pseudovoigts
        self.focus = self.focus_on_peaks(peak_width=0.5)
        self.sigmas = self.sigmas_equal

    @property
    def r1(self):
        return self.point_from_curve_arguments(x_arg=1, y_arg=0)

    @property
    def r2(self):
        return self.point_from_curve_arguments(x_arg=5, y_arg=4)


background_fit_routine_manager = RoutineManager()
background_fit_routine_manager.subscribe(HuberBackgroundFitRoutine)
background_fit_routine_manager.subscribe(SateliteBackgroundFitRoutine)

signal_fit_routine_manager = RoutineManager()
signal_fit_routine_manager.subscribe(GaussianSignalFitRoutine)
signal_fit_routine_manager.subscribe(PseudovoigtSignalFitRoutine)
