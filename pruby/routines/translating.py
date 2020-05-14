from uncertainties import ufloat
from .base import RoutineManager
from ..constants import R1_0, R2_0, T_0


def mao_function(r1, a, b):
    """Based on doi:10.1063/1.325277"""
    return (a / b) * (((r1 / R1_0) ** b) - 1)


class TemplateTranslationRoutine:
    def __init__(self):
        self.r1_corrected, self.r1_uncorrected = R1_0, R1_0
        self.r2_corrected, self.r2_uncorrected = R2_0, R2_0
        self.temperature = T_0

    @property
    def pressure(self):
        return 0.0

    def translate(self, r1, r2, correction, temperature):
        self.r1_uncorrected, self.r1_corrected = r1, r1 + correction
        self.r2_uncorrected, self.r2_corrected = r2, r2 + correction
        self.temperature = temperature
        return self.pressure


class LiuTranslationRoutine(TemplateTranslationRoutine):
    name = 'Liu'  # (2013)

    @property
    def pressure(self):
        return mao_function(self.r1_corrected, a=1904, b=9.827)


class MaoTranslationRoutine(TemplateTranslationRoutine):
    name = 'Mao'  # (1986)

    @property
    def pressure(self):
        return mao_function(self.r1_corrected, a=1904, b=7.665)


class PiermariniTranslationRoutine(TemplateTranslationRoutine):
    """Based on doi:10.1063/1.321957"""
    name = 'Piermarini'  # (1975)

    @property
    def pressure(self):
        return ufloat(2.740, 0.016) * (self.r1_corrected - R1_0)


class WeiTranslationRoutine(TemplateTranslationRoutine):
    """Based on doi:10.1063/1.3624618"""
    name = 'Wei'  # (2011)

    @property
    def pressure(self):
        a300 = ufloat(1915.0, 0.9)
        a1 = ufloat(0.622, 0.007)
        b300 = ufloat(9.28, 0.02)
        b1 = ufloat(-0.024, 0.003)
        b2 = ufloat(-8.2e-7, 0.02e-7)
        la300 = ufloat(694.2, 0.0)
        la1 = ufloat(0.0063, 0.0002)
        dt = self.temperature - 298.0
        a = a300 + a1 * dt
        b = b300 + b1 * dt + b2 * dt ** 2
        la_t = la300 + la1 * dt
        return (a / b) * (pow(self.r1_uncorrected / la_t, b) - 1.0)


translating_routine_manager = RoutineManager()
translating_routine_manager.subscribe(LiuTranslationRoutine)
translating_routine_manager.subscribe(WeiTranslationRoutine)
translating_routine_manager.subscribe(MaoTranslationRoutine)
translating_routine_manager.subscribe(PiermariniTranslationRoutine)
