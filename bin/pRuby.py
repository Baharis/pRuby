from uncertainties import ufloat
from ..routines.reading import reading_routine_manager
from ..routines.fitting import backfitting_routine_manager
from ..routines.fitting import peakfitting_routine_manager
from ..routines.correcting import correcting_routine_manager
from ..routines.translating import translating_routine_manager


class PressureCalculator:
    def __init__(self, reading=None, backfitting=None, peakfitting=None,
                 correcting=None, translating=None,
                 shift=ufloat(0.0, 0.0), temperature=ufloat(298.15, 0.0)):
        self.reading_routine = reading
        self.backfitting_routine = backfitting
        self.peakfitting_routine = peakfitting
        self.correcting_routine = correcting
        self.translating_routine = translating
        self.shift = shift
        self.temperature = temperature

    @property
    def reading_routine(self):
        if self._reading_routine is None:
            return reading_routine_manager.default
        else:
            return self._reading_routine

    @reading_routine.setter
    def reading_routine(self, value):
        self._reading_routine = reading_routine_manager[value]

    @property
    def backfitting_routine(self):
        if self._backfitting_routine is None:
            return backfitting_routine_manager.default
        else:
            return self._backfitting_routine

    @backfitting_routine.setter
    def backfitting_routine(self, value):
        self._backfitting_routine = backfitting_routine_manager[value]

    @property
    def peakfitting_routine(self):
        if self._peakfitting_routine is None:
            return peakfitting_routine_manager.default
        else:
            return self._peakfitting_routine

    @peakfitting_routine.setter
    def peakfitting_routine(self, value):
        self._peakfitting_routine = peakfitting_routine_manager[value]

    @property
    def correcting_routine(self):
        if self._correcting_routine is None:
            return correcting_routine_manager.default
        else:
            return self._correcting_routine

    @correcting_routine.setter
    def correcting_routine(self, value):
        self._correcting_routine = correcting_routine_manager[value]

    @property
    def translating_routine(self):
        if self._translating_routine is None:
            return translating_routine_manager.default
        else:
            return self._translating_routine

    @translating_routine.setter
    def translating_routine(self, value):
        self._translating_routine = translating_routine_manager[value]

    def __call__(self, filepath):
        temp = self.temperature
        raw_spec = self.reading_routine.read(filepath)
        peak_spec, back_spec, back_curve = self.backfitting_routine(raw_spec)
        peak_r1, peak_r2, peak_curve = self.peakfitting_routine(peak_spec)
        real_r1 = peak_r1 + self.shift
        real_r2 = peak_r2 + self.shift
        temp_corr = self.correcting_routine(temp)
        pressure = self.translating_routine(real_r1, real_r2, temp_corr, temp)
        axis = self.drawing_routine(peak_spec, back_spec, peak_curve,
                                    back_curve, peak_r1, peak_r2, pressure)
        return pressure, axis
