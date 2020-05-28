from uncertainties import ufloat
from .strategy import Strategy
from .spectrum import Spectrum
from .utility import cycle, LineSubset
from .constants import P_0, R1_0, R2_0, T_0


class PressureCalculator:
    def __init__(self):
        # initializing strategies
        self.strategy = Strategy(self)
        # initializing variables
        self.filename = ''
        self.limits = LineSubset(690.0, 705.0)
        self.raw_spectrum = Spectrum()
        self.back_spectrum = Spectrum()
        self.peak_spectrum = Spectrum()
        self.r1 = R1_0
        self.r2 = R2_0
        self.r1_ref = R1_0
        self.t = T_0
        self.t_ref = T_0
        self.t_correction = 0.0
        self.offset = 0.0
        self.p = P_0
        self.calculate_p_from_r1()
        self.fig, self.ax = None, None
        self.color_cycle = cycle('rgbcmy')
        self.color = 'k'

    def set_current_as_reference(self):
        self.r1_ref = self.r1
        self.t_ref = self.t
        self.calculate_p_from_r1()
        self.calculate_offset_from_reference()
        self.calculate_p_from_r1()

    def calculate_offset_from_reference(self):
        backupped_values = self.r1, self.t, self.p
        self.offset = ufloat(0.00, 0.01)
        self.t, self.p = self.t_ref, P_0
        self.calculate_r1_from_p()
        self.offset = self.r1_ref - self.r1
        self.r1, self.t, self.p = backupped_values

    def read_and_fit(self):
        self.strategy.read()
        self.strategy.backfit()
        self.strategy.peakfit()

    def calculate_p_from_r1(self):
        self.strategy.correct()
        self.strategy.translate()

    def calculate_r1_from_p(self):
        target_p, self.p = self.p, self.p - 100
        precision, r_step_size = 10 ** -4, 1.0
        self.r1 = ufloat(self.r1.n, precision)
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
