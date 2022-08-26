import abc
from collections import OrderedDict
from pruby.strategies.base import BaseStrategy, BaseStrategies
from uncertainties import ufloat
from pruby.constants import R1_0


def mao_function(r1, a, b):
    """Based on doi:10.1063/1.325277"""
    return (a / b) * (((r1 / R1_0) ** b) - 1)


class TranslatingStrategy(BaseStrategy, abc.ABC):
    @abc.abstractmethod
    def translate(self, calc):
        raise NotImplementedError


class TranslatingStrategies(BaseStrategies):
    registry = OrderedDict()
    strategy_type = TranslatingStrategy


@TranslatingStrategies.register(default=True)
class JacobsenTranslatingStrategy(TranslatingStrategy):
    name = 'Jacobsen'  # (2008)

    def translate(self, calc):
        r1 = calc.r1 - calc.offset + calc.t_correction
        calc.p = mao_function(r1, a=1904, b=ufloat(10.32, 0.07))


@TranslatingStrategies.register(default=True)
class LiuTranslatingStrategy(TranslatingStrategy):
    name = 'Liu'  # (2013)

    def translate(self, calc):
        r1 = calc.r1 - calc.offset + calc.t_correction
        calc.p = mao_function(r1, a=1904, b=9.827)


@TranslatingStrategies.register()
class MaoTranslatingStrategy(TranslatingStrategy):
    name = 'Mao'  # (1986)

    def translate(self, calc):
        r1 = calc.r1 - calc.offset + calc.t_correction
        calc.p = mao_function(r1, a=1904, b=7.665)


@TranslatingStrategies.register()
class PiermariniTranslatingStrategy(TranslatingStrategy):
    """Based on doi:10.1063/1.321957"""
    name = 'Piermarini'  # (1975)

    def translate(self, calc):
        r1 = calc.r1 - calc.offset + calc.t_correction
        calc.p = ufloat(2.740, 0.016) * (r1 - R1_0)


@TranslatingStrategies.register()
class WeiTranslatingStrategy(TranslatingStrategy):
    """Based on doi:10.1063/1.3624618"""
    name = 'Wei'  # (2011)

    def translate(self, calc):
        r1 = calc.r1 - calc.offset
        a300 = ufloat(1915.0, 0.9)
        a1 = ufloat(0.622, 0.007)
        b300 = ufloat(9.28, 0.02)
        b1 = ufloat(-0.024, 0.003)
        b2 = ufloat(-8.2e-7, 0.02e-7)
        la300 = ufloat(694.2, 0.0)
        la1 = ufloat(0.0063, 0.0002)
        dt = calc.t - 298.0
        a = a300 + a1 * dt
        b = b300 + b1 * dt + b2 * dt ** 2
        la_t = la300 + la1 * dt
        calc.p = (a / b) * (pow(r1 / la_t, b) - 1.0)
