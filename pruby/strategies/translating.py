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


@TranslatingStrategies.register()
class JacobsenTranslatingStrategy(TranslatingStrategy):
    name = 'Jacobsen'
    year = 2008
    reference = r'https://doi.org/10.2138/am.2008.2988'

    def translate(self, calc):
        r1 = calc.r1 - calc.offset + calc.t_correction
        calc.p = mao_function(r1, a=1904, b=ufloat(10.32, 0.07))


@TranslatingStrategies.register()
class LiuTranslatingStrategy(TranslatingStrategy):
    """Based on doi:10.1088/1674-1056/22/5/056201"""
    name = 'Liu'  # (2013)
    year = 2013
    reference = r'https://doi.org/10.1088/1674-1056/22/5/056201'

    def translate(self, calc):
        r1 = calc.r1 - calc.offset + calc.t_correction
        calc.p = mao_function(r1, a=1904, b=9.827)


@TranslatingStrategies.register()
class MaoTranslatingStrategy(TranslatingStrategy):
    name = 'Mao'
    year = 1986
    reference = r'https://doi.org/10.1029/JB091iB05p04673'

    def translate(self, calc):
        r1 = calc.r1 - calc.offset + calc.t_correction
        calc.p = mao_function(r1, a=1904, b=7.665)


@TranslatingStrategies.register()
class PiermariniTranslatingStrategy(TranslatingStrategy):
    name = 'Piermarini'
    year = 1975
    reference = r'https://doi.org/10.1063/1.321957'

    def translate(self, calc):
        r1 = calc.r1 - calc.offset + calc.t_correction
        calc.p = ufloat(2.740, 0.016) * (r1 - R1_0)


@TranslatingStrategies.register(default=True)
class Ruby2020TranslatingStrategy(TranslatingStrategy):
    name = 'Ruby2020'
    year = 2020
    reference = r'https://doi.org/10.1080/08957959.2020.1791107'

    def translate(self, calc):
        r1 = calc.r1 - calc.offset + calc.t_correction
        r1_0_ruby2020 = ufloat(694.25, 0.01)
        r_rel = (r1 - r1_0_ruby2020) / r1_0_ruby2020
        calc.p = ufloat(1870, 10) * r_rel * (1 + ufloat(5.63, 0.03) * r_rel)


@TranslatingStrategies.register()
class WeiTranslatingStrategy(TranslatingStrategy):
    name = 'Wei'
    year = 2011
    reference = r'https://doi.org/10.1063/1.3624618'

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

# TODO: use years when generating strategy names
# TODO: add doi links or numbers as variables
