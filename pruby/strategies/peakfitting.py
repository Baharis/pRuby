import abc
import numpy as np
from scipy.optimize import curve_fit as scipy_fit
from scipy.signal import find_peaks_cwt
from uncertainties import ufloat
from .base import BaseStrategy, BaseStrategies
from ..utility import gaussian, pseudovoigt
from ..spectrum import Curve
from ..constants import R1_0, R2_0


class PeakfittingStrategy(BaseStrategy, abc.ABC):
    @abc.abstractmethod
    def peakfit(self, calc):
        raise NotImplementedError


class PeakfittingStrategies(BaseStrategies):
    pass


class BasePeakfittingStrategy(PeakfittingStrategy):
    @abc.abstractmethod
    def _prepare_peakfit(self, calc):
        pass

    @abc.abstractmethod
    def _assign_peaks(self, calc):
        pass

    def peakfit(self, calc):
        self._prepare_peakfit(calc)
        x = calc.peak_spectrum.focused.x
        y = calc.peak_spectrum.focused.y
        si = calc.peak_spectrum.focused.si
        calc.peak_spectrum.curve.args, pcov = \
            scipy_fit(calc.peak_spectrum.curve, xdata=x, ydata=y,
                      p0=calc.peak_spectrum.curve.args, sigma=si)
        calc.peak_spectrum.curve.uncs = np.sqrt(np.diag(pcov))
        self._assign_peaks(calc)

    @staticmethod
    def find_initial_peaks(spectrum):
        x_span = max(spectrum.x) - min(spectrum.x)
        caret_width = int(0.5 / (x_span / len(spectrum.x))) + 1
        peak_indices = find_peaks_cwt(spectrum.y, [caret_width] * 3)
        peaks = np.array([(spectrum.x[i], spectrum.y[i])
                          for i in peak_indices])
        peaks = peaks[peaks[:, 1].argsort()[::-1]]
        if len(peaks) == 0:
            r1x = R1_0.nominal_value
            r1y = max(spectrum.y)
            r2x = R2_0.nominal_value
            r2y = max(spectrum.y) / 2
        elif len(peaks) == 1:
            r1x = peaks[0][0]
            r1y = peaks[0][1]
            r2x = r1x * (1 - 0.002)
            r2y = r1y / 2
        else:
            if peaks[0][0] - 3.0 < peaks[1][0] < peaks[0][0] - 1.0:
                r1x = peaks[0][0]
                r1y = peaks[0][1]
                r2x = peaks[1][0]
                r2y = peaks[1][1]
            else:
                r1x = peaks[0][0]
                r1y = peaks[0][1]
                r2x = r1x * (1 - 0.002)
                r2y = r1y / 2
        return r1x, r1y, r2x, r2y

    @staticmethod
    def ufloat_from_curve_args(curve, index):
        return ufloat(curve.args[index], curve.uncs[index])


@PeakfittingStrategies.register(default=True)
class GaussianPeakfittingStrategy(BasePeakfittingStrategy):
    name = 'Gaussian'

    def _prepare_peakfit(self, calc):
        def two_gaussians(x, _a1, _mu1, _si1, _a2, _mu2, _si2):
            return gaussian(_a1, _mu1, _si1)(x) + gaussian(_a2, _mu2, _si2)(x)
        mu1, a1, mu2, a2 = self.find_initial_peaks(calc.peak_spectrum)
        si1 = si2 = 0.3
        calc.peak_spectrum.curve = Curve(func=two_gaussians,
                                         args=(a1, mu1, si1, a2, mu2, si2))
        peaks = self.find_initial_peaks(calc.peak_spectrum)
        calc.peak_spectrum.focus_on_points((peaks[0], peaks[2]), width=0.5)
        calc.peak_spectrum.sigma_type = 'equal'

    def _assign_peaks(self, calc):
        curve = calc.peak_spectrum.curve
        calc.r1 = self.ufloat_from_curve_args(curve, index=1)
        calc.r2 = self.ufloat_from_curve_args(curve, index=4)


@PeakfittingStrategies.register()
class PseudovoigtPeakfittingStrategy(BasePeakfittingStrategy):
    name = 'Pseudovoigt'

    def _prepare_peakfit(self, calc):
        def two_pseudovoigts(x, _a1, _mu1, _w1, _et1, _a2, _mu2, _w2, _et2):
            return pseudovoigt(_a1, _mu1, _w1, _et1)(x) + \
                   pseudovoigt(_a2, _mu2, _w2, _et2)(x)

        mu1, a1, mu2, a2 = self.find_initial_peaks(calc.peak_spectrum)
        w1 = w2 = 0.6
        et1 = et2 = 0.5
        calc.peak_spectrum.curve = Curve(
            func=two_pseudovoigts,
            args=(a1, mu1, w1, et1, a2, mu2, w2, et2))
        peaks = self.find_initial_peaks(calc.peak_spectrum)
        calc.peak_spectrum.focus_on_points((peaks[0], peaks[2]), width=1.0)
        calc.peak_spectrum.sigma_type = 'equal'

    def _assign_peaks(self, calc):
        curve = calc.peak_spectrum.curve
        calc.r1 = self.ufloat_from_curve_args(curve, index=1)
        calc.r2 = self.ufloat_from_curve_args(curve, index=5)


@PeakfittingStrategies.register()
class CamelPeakfittingStrategy(BasePeakfittingStrategy):
    name = 'Camel'

    def _prepare_peakfit(self, calc):
        def camel(x, _a1, _mu1, _si1, _a2, _mu2, _si2, _a, _si):
            return gaussian(_a2, _mu2, _si2)(x) + gaussian(_a1, _mu1, _si1)(x) \
                   + gaussian(_a, (_mu2 + _mu1) / 2, _si)(x)
        mu1, a1, mu2, a2 = self.find_initial_peaks(calc.peak_spectrum)
        si1, si2, si, a = 0.35, 0.35, 1.0, a1 / 10
        calc.peak_spectrum.curve = Curve(
            func=camel,
            args=(a1, mu1, si1, a2, mu2, si2, a, si))
        peaks = self.find_initial_peaks(calc.peak_spectrum)
        calc.peak_spectrum.focus_on_points((peaks[0], peaks[2]), width=1.0)
        calc.peak_spectrum.sigma_type = 'equal'

    def _assign_peaks(self, calc):
        curve = calc.peak_spectrum.curve
        calc.r1 = self.ufloat_from_curve_args(curve, index=1)
        calc.r2 = self.ufloat_from_curve_args(curve, index=4)
