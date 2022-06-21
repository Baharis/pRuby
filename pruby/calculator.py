import matplotlib.pyplot as plt
import uncertainties as uc
from pruby.strategy import Strategy
from pruby.spectrum import Spectrum
from pruby.utility import LineSubset
from pruby.constants import P_0, R1_0, R2_0, T_0, UZERO


class PressureCalculator:
    def __init__(self):
        self.strategy: Strategy = Strategy(self)
        self.dat_path: str = ''
        self.ref_path: str = ''
        self.limits: LineSubset = LineSubset(690.0, 705.0)
        self.raw_spectrum: Spectrum = Spectrum()
        self.back_spectrum: Spectrum = Spectrum()
        self.peak_spectrum: Spectrum = Spectrum()
        self.r1: uc.UFloat = R1_0
        self.r2: uc.UFloat = R2_0
        self.r1_ref: uc.UFloat = R1_0
        self.t: uc.UFloat = T_0
        self.t_ref: uc.UFloat = T_0
        self.p: uc.UFloat = P_0
        self.t_correction: uc.UFloat = UZERO
        self.offset: uc.UFloat = UZERO
        self.fig: plt.Figure = plt.Figure()
        self.calculate_p_from_r1()

    @staticmethod
    def convert_to_ufloat(value):
        if isinstance(value, (uc.core.Variable, uc.core.AffineScalarFunc)):
            return value
        elif isinstance(value, float):
            return uc.ufloat(value)
        else:
            m = 'Assigned value {} should be float or ufloat'.format(str(value))
            raise TypeError(m)

    @property
    def r1(self):
        return self._r1

    @r1.setter
    def r1(self, value):
        self._r1 = self.convert_to_ufloat(value)

    @property
    def r2(self):
        return self._r2

    @r2.setter
    def r2(self, value):
        self._r2 = self.convert_to_ufloat(value)

    @property
    def r1_ref(self):
        return self._r1_ref

    @r1_ref.setter
    def r1_ref(self, value):
        self._r1_ref = self.convert_to_ufloat(value)

    @property
    def t(self):
        return self._t

    @t.setter
    def t(self, value):
        self._t = self.convert_to_ufloat(value)

    @property
    def t_ref(self):
        return self._t_ref

    @t_ref.setter
    def t_ref(self, value):
        self._t_ref = self.convert_to_ufloat(value)

    @property
    def t_correction(self):
        return self._t_correction

    @t_correction.setter
    def t_correction(self, value):
        self._t_correction = self.convert_to_ufloat(value)

    @property
    def offset(self):
        return self._offset

    @offset.setter
    def offset(self, value):
        self._offset = self.convert_to_ufloat(value)

    @property
    def p(self):
        return self._p

    @p.setter
    def p(self, value):
        self._p = self.convert_to_ufloat(value)

    def set_current_as_reference(self):
        self.r1_ref = self.r1
        self.t_ref = self.t
        self.ref_path = self.dat_path
        self.calculate_p_from_r1()
        self.calculate_offset_from_reference()
        self.calculate_p_from_r1()

    def calculate_offset_from_reference(self):
        backupped_values = self.r1, self.t, self.p
        self.offset = uc.ufloat(0.00, 0.01)
        self.t, self.p = self.t_ref, P_0
        self.calculate_r1_from_p()
        self.offset = self.r1_ref - self.r1
        self.r1, self.t, self.p = backupped_values

    def read(self, path: str = ''):
        self.dat_path = path if path else self.dat_path
        self.strategy.read()
        self.strategy.backfit()
        self.strategy.peakfit()

    def calculate_p_from_r1(self):
        self.strategy.correct()
        self.strategy.translate()

    def calculate_r1_from_p(self):
        target_p, self.p = self.p, self.p - 100
        precision, r_step_size = 10 ** -4, 1.0
        self.r1 = uc.ufloat(self.r1.n, precision)
        while True:
            previous_p = self.p
            self.calculate_p_from_r1()
            if abs(target_p - self.p) < precision:
                break
            if abs(self.p - previous_p) > abs(previous_p - target_p):
                r_step_size = r_step_size * 0.5
            if self.p < target_p:
                self.r1 += r_step_size
            else:
                self.r1 -= r_step_size

    def draw(self):
        if self.peak_spectrum:
            self.strategy.draw()
        else:
            raise AttributeError('The peak spectrum is empty')


if __name__ == '__main__':
    c = PressureCalculator()
    c.read('/home/dtchon/git/pRuby/r27.txt')
    c.calculate_p_from_r1()
    print(c.p)
    c.set_current_as_reference()
    c.draw()
    c.read('/home/dtchon/git/pRuby/r27.txt')
    c.calculate_p_from_r1()
    print(c.p)
    c.strategy.set(drawing='Simple')
    c.draw()
