import abc
import copy
from collections import OrderedDict
from .base import BaseStrategy, BaseStrategies
from scipy.optimize import curve_fit
from ..utility.functions import polynomial
from ..spectrum import Curve


class BackfittingStrategy(BaseStrategy, abc.ABC):
    @abc.abstractmethod
    def backfit(self, calc):
        raise NotImplementedError


class BackfittingStrategies(BaseStrategies):
    registry = OrderedDict()
    strategy_type = BackfittingStrategy


class BaseBackfittingStrategy(BackfittingStrategy, abc.ABC):
    # For details, see https://doi.org/10.1016/j.chemolab.2004.10.003

    @staticmethod
    def _approximate_linearly(spectrum):
        def linear_function(x, _a0, _a1):
            return polynomial(_a0, _a1)(x)
        a1 = (spectrum.y[-1] - spectrum.y[0]) / (spectrum.x[-1] - spectrum.x[0])
        a0 = spectrum.y[0] - a1 * spectrum.x[0]
        spectrum.curve = Curve(func=linear_function, args=(a0, a1))

    @abc.abstractmethod
    def _prepare_backfit(self, calc):
        pass

    def backfit(self, calc):
        self._prepare_backfit(calc)
        for cycle in range(50):
            previous_mse = calc.back_spectrum.mse
            x = calc.back_spectrum.focused.x
            y = calc.back_spectrum.focused.y
            si = calc.back_spectrum.focused.si
            calc.back_spectrum.curve.args, _ = \
                curve_fit(calc.back_spectrum.curve, xdata=x, ydata=y,
                          p0=calc.back_spectrum.curve.args, sigma=si)
            if previous_mse / calc.back_spectrum.mse - 1 < 1e-10:
                break
        calc.back_spectrum.y = calc.back_spectrum.f
        calc.peak_spectrum = copy.deepcopy(calc.raw_spectrum)
        calc.peak_spectrum.y = calc.raw_spectrum.y - calc.back_spectrum.y


@BackfittingStrategies.register(default=True)
class HuberBackfittingStrategy(BaseBackfittingStrategy):
    name = 'Linear Huber'

    def _prepare_backfit(self, calc):
        calc.back_spectrum = copy.deepcopy(calc.raw_spectrum)
        self._approximate_linearly(calc.back_spectrum)
        calc.back_spectrum.focus_on_whole()
        calc.back_spectrum.sigma_type = 'huber'


@BackfittingStrategies.register()
class SateliteBackfittingStrategy(BaseBackfittingStrategy):
    name = 'Linear Satelite'

    def _prepare_backfit(self, calc):
        calc.back_spectrum = copy.deepcopy(calc.raw_spectrum)
        self._approximate_linearly(calc.back_spectrum)
        calc.back_spectrum.focus_on_edge(width=1.0)
        calc.back_spectrum.sigma_type = 'equal'
