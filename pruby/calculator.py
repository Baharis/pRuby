from uncertainties import ufloat
from pruby.routines.manager import routine_manager
from pruby.spectrum import Spectrum, Curve
from .constants import P_0, R1_0, R2_0, T_0, UZERO
from .utility import LineSubset
import abc


# TODO work further here (dynamic inheritance) after upgrading routine_manager
# class PressureCalculatorFactory:
#     def make_calculator(self, reading='', backfitting='', peakfitting='',
#                         correcting='', translating='', drawing=''):
#         r = routine_manager.select('reading', reading)
#         b = routine_manager.select('backfitting', backfitting)
#         p = routine_manager.select('peakfitting', peakfitting)
#         c = routine_manager.select('correcting', correcting)
#         t = routine_manager.select('translating', translating)
#         d = routine_manager.select('drawing', drawing)
#
#         class PressureCalculator(abc.ABC, r, b, p, c, t, d):
#             def __init__(self):
#                 # fitting
#                 self.peak_spect = Spectrum()
#                 self.back_spect = Spectrum()
#                 self.peak_curve = Curve()
#                 self.back_curve = Curve()
#                 self.peak_focus = LineSubset()
#                 self.back_focus = LineSubset()
#                 self.r1_x = R1_0
#                 self.r1_y = UZERO
#                 self.r2_x = R2_0
#                 self.r2_y = UZERO
#                 # correctting
#                 self.shift = 0.0
#                 self.t = T_0
#                 # translating
#                 self.p = P_0
#                 # settings
#                 self.reading_routine = reading_routine_manager.default
#                 self.backfitting_routine = backfitting_routine_manager.default
#                 self.peakfitting_routine = peakfitting_routine_manager.default
#                 self.correcting_routine = correcting_routine_manager.default
#                 self.translating_routine = translating_routine_manager.default
#                 self.drawing_routine = drawing_routine_manager.default
#
#             def set_routine(self, reading='', backfitting='', peakfitting='',
#                             correcting='', translating='', drawing=''):
#                 if reading:
#                     self.reading_routine = reading_routine_manager.select(
#                         reading)
#                 if backfitting:
#                     self.backfitting_routine = backfitting_routine_manager.select(
#                         backfitting)
#                 if peakfitting:
#                     self.peakfitting_routine = peakfitting_routine_manager.select(
#                         peakfitting)
#                 if correcting:
#                     self.correcting_routine = correcting_routine_manager.select(
#                         correcting)
#                 if translating:
#                     self.translating_routine = translating_routine_manager.select(
#                         translating)
#                 if drawing:
#                     self.drawing_routine = drawing_routine_manager.select(
#                         drawing)
#
#             def read_and_fit(self, filepath):
#                 raw_spect = self.reading_routine.read(filepath)
#                 self.peak_spect, self.back_spect, self.back_curve, self.back_focus = \
#                     self.backfitting_routine(raw_spect).fit()
#                 r1, r2, self.peak_curve, self.peak_focus = \
#                     self.peakfitting_routine(self.peak_spect).fit()
#                 self.r1_x, self.r1_y = r1
#                 self.r2_x, self.r2_y = r2
#
#             def calculate_pressure(self):
#                 r1_shifted = self.r1_x - self.shift
#                 r2_shifted = self.r2_x - self.shift
#                 temp_correction = self.correcting_routine().correct(self.t)
#                 self.p = self.translating_routine().translate(r1_shifted,
#                                                               r2_shifted,
#                                                               temp_correction,
#                                                               self.t)
#
#             def calculate_r1(self):
#                 target_p, self.p = self.p, self.p - 100
#                 precision, r_step_size = 10 ** -4, 1.0
#                 self.r1_x = ufloat(self.r1_x.n, precision)
#                 while True:
#                     previous_p = self.p
#                     self.calculate_pressure()
#                     if abs(target_p - self.p) < precision:
#                         break
#                     if abs(self.p - previous_p) > abs(previous_p - target_p):
#                         r_step_size = r_step_size * 0.5
#                     if self.p < target_p:
#                         self.r1_x += r_step_size
#                     else:
#                         self.r1_x -= r_step_size
#
#             def draw(self):
#                 self.drawing_routine.draw(r1_x=self.r1_x, r1_y=self.r1_y,
#                                           r2_x=self.r2_x, r2_y=self.r2_y,
#                                           label=str(self.p),
#                                           peak_spect=self.peak_spect,
#                                           back_spect=self.back_spect,
#                                           peak_curve=self.peak_curve,
#                                           back_curve=self.back_curve,
#                                           peak_focus=self.peak_focus,
#                                           back_focus=self.back_focus)
#
#         return PressureCalculator()





# TODO remove after switching to new code
class PressureCalculator(abc.ABC):
    def __init__(self):
        # fitting
        self.peak_spect = Spectrum()
        self.back_spect = Spectrum()
        self.peak_curve = Curve()
        self.back_curve = Curve()
        self.peak_focus = LineSubset()
        self.back_focus = LineSubset()
        self.r1_x = R1_0
        self.r1_y = UZERO
        self.r2_x = R2_0
        self.r2_y = UZERO
        # correctting
        self.shift = 0.0
        self.t = T_0
        # translating
        self.p = P_0
        # settings
        self.reading_routine = routine_manager.default['reading']
        self.backfitting_routine = routine_manager.default['backfitting']
        self.peakfitting_routine = routine_manager.default['peakfitting']
        self.correcting_routine = routine_manager.default['correcting']
        self.translating_routine = routine_manager.default['translating']
        self.drawing_routine = routine_manager.default['drawing']

    def set_routine(self, reading='', backfitting='', peakfitting='',
                    correcting='', translating='', drawing=''):
        if reading:
            self.reading_routine = routine_manager.select('reading', reading)
        if backfitting:
            self.backfitting_routine = routine_manager.select('backfitting', backfitting)
        if peakfitting:
            self.peakfitting_routine = routine_manager.select('peakfitting', peakfitting)
        if correcting:
            self.correcting_routine = routine_manager.select('correcting', correcting)
        if translating:
            self.translating_routine = routine_manager.select('translating', translating)
        if drawing:
            self.drawing_routine = routine_manager.select('drawing', drawing)

    def read_and_fit(self, filepath):
        raw_spect = self.reading_routine.read(filepath)
        self.peak_spect, self.back_spect, self.back_curve, self.back_focus = \
            self.backfitting_routine(raw_spect).fit()
        r1, r2, self.peak_curve, self.peak_focus = \
            self.peakfitting_routine(self.peak_spect).fit()
        self.r1_x, self.r1_y = r1
        self.r2_x, self.r2_y = r2

    def calculate_pressure(self):
        r1_shifted = self.r1_x - self.shift
        r2_shifted = self.r2_x - self.shift
        temp_correction = self.correcting_routine().correct(self.t)
        self.p = self.translating_routine().translate(r1_shifted, r2_shifted,
                                                      temp_correction, self.t)

    def calculate_r1(self):
        target_p, self.p = self.p, self.p-100
        precision, r_step_size = 10**-4, 1.0
        self.r1_x = ufloat(self.r1_x.n, precision)
        while True:
            previous_p = self.p
            self.calculate_pressure()
            if abs(target_p-self.p) < precision:
                break
            if abs(self.p - previous_p) > abs(previous_p - target_p):
                r_step_size = r_step_size * 0.5
            if self.p < target_p:
                self.r1_x += r_step_size
            else:
                self.r1_x -= r_step_size

    def draw(self):
        self.drawing_routine.draw(r1_x=self.r1_x, r1_y=self.r1_y,
            r2_x=self.r2_x, r2_y=self.r2_y, label=str(self.p),
            peak_spect=self.peak_spect, back_spect=self.back_spect,
            peak_curve=self.peak_curve, back_curve=self.back_curve,
            peak_focus=self.peak_focus, back_focus=self.back_focus)
