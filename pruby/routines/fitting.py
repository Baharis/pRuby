import numpy as np
from scipy.optimize import curve_fit as scipy_fit
from scipy.signal import find_peaks_cwt
from uncertainties import ufloat
from .base import RoutineManager
from ..utility.maths import polynomial, gaussian, lorentzian
from pruby.spectrum import Spectrum, Curve
from pruby.utility.line_subset import LineSubset


class TemplateFittingRoutine:
    def __init__(self, spectrum):
        self.spectrum = spectrum
        self.curve = self.curve_linear()
        self.sigma = self.sigma_equal()
        self.focus = self.focus_on_whole()

    def curve_linear(self):
        def curve_func(x, _a0, _a1):
            return polynomial(a0, a1)(x)
        a1 = (self.spectrum.y[-1] - self.spectrum.y[0]) / \
             (self.spectrum.x[-1] - self.spectrum.x[0])
        a0 = self.spectrum.y[0] - a1 * self.spectrum.x[0]
        return Curve(func=curve_func, args=(a0, a1))

    def curve_camel(self):
        def curve_func(x, _a1, _mu1, _si1, _a2, _mu2, _si2, _a, _si):
            return gaussian(_a2, _mu2, _si2)(x) + gaussian(_a1, _mu1, _si1)(x) \
                   + gaussian(_a, (_mu2 + _mu1) / 2, _si)(x)
        mu1, a1, mu2, a2 = self.spectrum_peaks
        si1, si2, si, a = 0.35, 0.35, 1.0, a1 / 10
        return Curve(func=curve_func, args=(a1, mu1, si1, a2, mu2, si2, a, si))

    def curve_two_gaussians(self):
        def curve_func(x, _a1, _mu1, _si1, _a2, _mu2, _si2):
            return gaussian(_a1, _mu1, _si1)(x) + gaussian(_a2, _mu2, _si2)(x)
        mu1, a1, mu2, a2 = self.spectrum_peaks
        si1 = si2 = 0.3
        return Curve(func=curve_func, args=(a1, mu1, si1, a2, mu2, si2))

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
    def f(self):
        return np.array(list(map(self.curve, self.spectrum.x)))

    @property
    def diff(self):
        return self.spectrum.y - self.f

    @property
    def mse(self):
        return sum((self.diff / self.sigma) ** 2) / len(self.diff)

    @property
    def spectrum_peaks(self):
        x_span = max(self.spectrum.x) - min(self.spectrum.x)
        caret_width = int(0.5 / (x_span / len(self.spectrum.x))) + 1
        peak_indices = find_peaks_cwt(self.spectrum.y, [caret_width] * 5)
        peaks = np.array([(self.spectrum.x[i], self.spectrum.y[i])
                          for i in peak_indices])
        peaks = peaks[peaks[:, 1].argsort()[::-1]]
        r1_x, r1_y = peaks[0, 0], peaks[0, 1]
        if len(peaks) == 1 or not(peaks[0][0] - 2 < peaks[1][0] < peaks[0][0]):
            r2_x, r2_y = r1_x * (1 - 0.002), r1_y * 0.6
        else:
            r2_x, r2_y = peaks[1, 0], peaks[1, 1]
        return r1_x, r1_y, r2_x, r2_y

    def focus_on_whole(self):
        return LineSubset(min(self.spectrum.x), max(self.spectrum.x))

    def focus_on_edge(self, edge_fraction=0.1):
        x_min = min(self.spectrum.x)
        x_max = max(self.spectrum.x)
        sub1 = LineSubset(x_min, x_min + edge_fraction * (x_max - x_min))
        sub2 = LineSubset(x_max - edge_fraction * (x_max - x_min), x_max)
        return sub1 + sub2

    def focus_on_peaks(self, peak_width=0.5):
        r1_x, r1_y, r2_x, r2_y = self.spectrum_peaks
        sub1 = LineSubset(r1_x - peak_width / 2, r1_x + peak_width / 2)
        sub2 = LineSubset(r2_x - peak_width / 2, r2_x + peak_width / 2)
        return sub1 + sub2

    def sigma_equal(self):
        return np.ones_like(self.spectrum.x)

    def sigma_huber(self):
        lim = 0.05 * max(abs(self.diff))
        sigmas = [lim ** 2 if d < lim else lim * (2 * d - lim)
                  for d in self.diff]
        return np.array(sigmas)


class TemplateBackFittingRoutine(TemplateFittingRoutine):
    def fit(self):
        prec, cycle, max_cycles = 1e-10, 0, 50
        while True:
            prev_mse = self.mse
            cycle += 1
            x = self.spectrum.within(self.focus).x
            y = self.spectrum.within(self.focus).y
            si = self.sigma[np.array([_ in self.focus for _ in self.spectrum.x])]
            self.curve.args, _ = scipy_fit(self.curve, xdata=x, ydata=y,
                                           p0=self.curve.args, sigma=si)
            if prev_mse / self.mse - 1 > prec or cycle == max_cycles:
                break

        signal_spectrum = Spectrum(x=self.spectrum.x, y=self.spectrum.y-self.f)
        back_spectrum = Spectrum(x=self.spectrum.x, y=self.f)
        back_curve = self.curve
        back_focus = self.focus
        return signal_spectrum, back_spectrum, back_curve, back_focus


class HuberBackFittingRoutine(TemplateBackFittingRoutine):
    name = 'Linear Huber'

    def __init__(self, spectrum):
        super().__init__(spectrum)
        self.curve = self.curve_linear()
        self.focus = self.focus_on_whole()
        self.sigma = self.sigma_huber()


class SateliteBackFittingRoutine(TemplateBackFittingRoutine):
    name = 'Linear Satelite'

    def __init__(self, spectrum):
        super().__init__(spectrum)
        self.curve = self.curve_linear()
        self.focus = self.focus_on_edge(edge_fraction=0.1)
        self.sigma = self.sigma_equal()


class TemplatePeakFittingRoutine(TemplateFittingRoutine):
    r1, r2 = False, False

    def fit(self):
        x = self.spectrum.within(self.focus).x
        y = self.spectrum.within(self.focus).y
        si = self.sigma[np.array([_ in self.focus for _ in self.spectrum.x])]
        popt, pcov = scipy_fit(self.curve, xdata=x, ydata=y,
                               p0=self.curve.args, sigma=1/(1+y-min(y)))
        popt, pcov = scipy_fit(self.curve, xdata=x, ydata=y, p0=popt, sigma=si)
        self.curve.args = popt
        self.curve.uncs = np.sqrt(np.diag(pcov))
        return self.r1, self.r2, self.curve, self.focus

    def tuple_from_curve_arguments(self, x_arg, y_arg):
        return (ufloat(self.curve.args[x_arg], self.curve.uncs[x_arg]),
                ufloat(self.curve.args[y_arg], self.curve.uncs[y_arg]))


class GaussianPeakFittingRoutine(TemplatePeakFittingRoutine):
    name = 'Gaussian'

    def __init__(self, spectrum):
        super().__init__(spectrum)
        self.curve = self.curve_two_gaussians()
        self.focus = self.focus_on_peaks(peak_width=0.5)
        self.sigma = self.sigma_equal()

    @property
    def r1(self):
        return self.tuple_from_curve_arguments(x_arg=1, y_arg=0)

    @property
    def r2(self):
        return self.tuple_from_curve_arguments(x_arg=4, y_arg=3)


class PseudovoigtPeakFittingRoutine(TemplatePeakFittingRoutine):
    name = 'Pseudovoigt'

    def __init__(self, spectrum):
        super().__init__(spectrum)
        self.curve = self.curve_two_pseudovoigts()
        self.focus = self.focus_on_peaks(peak_width=1.0)
        self.sigma = self.sigma_equal()

    @property
    def r1(self):
        return self.tuple_from_curve_arguments(x_arg=1, y_arg=0)

    @property
    def r2(self):
        return self.tuple_from_curve_arguments(x_arg=5, y_arg=4)


class CamelPeakFittingRoutine(TemplatePeakFittingRoutine):
    name = 'Camel'

    def __init__(self, spectrum):
        super().__init__(spectrum)
        self.curve = self.curve_camel()
        self.focus = self.focus_on_peaks(peak_width=1.0)
        self.sigma = self.sigma_equal()

    @property
    def r1(self):
        return self.tuple_from_curve_arguments(x_arg=1, y_arg=0)

    @property
    def r2(self):
        return self.tuple_from_curve_arguments(x_arg=4, y_arg=3)


backfitting_routine_manager = RoutineManager()
backfitting_routine_manager.subscribe(HuberBackFittingRoutine)
backfitting_routine_manager.subscribe(SateliteBackFittingRoutine)

peakfitting_routine_manager = RoutineManager()
peakfitting_routine_manager.subscribe(GaussianPeakFittingRoutine)
peakfitting_routine_manager.subscribe(PseudovoigtPeakFittingRoutine)
peakfitting_routine_manager.subscribe(CamelPeakFittingRoutine)
