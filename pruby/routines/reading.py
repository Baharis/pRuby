import numpy as np
from .base import RoutineManager
from pruby.spectrum import Spectrum
from pruby.utility.line_subset import LineSubset


reading_routine_manager = RoutineManager()


class TemplateReadingRoutine:
    limits = LineSubset(690.0, 705.0)


class RawTxtReadingRoutine(TemplateReadingRoutine):
    name = 'Raw txt'

    def read(self, filepath):
        raw_data = np.loadtxt(filepath, dtype=(float, float))
        raw_spectrum = Spectrum(x=raw_data[:, 0], y=raw_data[:, 1])
        return raw_spectrum.within(self.limits)


class MetaTxtReadingRoutine(TemplateReadingRoutine):
    name = 'Metadata txt'

    def read(self, filepath):
        with open(filepath, "r") as file:
            x_list, y_list = [], []
            for line in file.readlines():
                try:
                    split_line = line.strip().split()
                    new_x = float(split_line[0])
                    new_y = float(split_line[1])
                except ValueError:
                    pass
                else:
                    x_list.append(new_x)
                    y_list.append(new_y)
        raw_spectrum = Spectrum(x=x_list, y=y_list)
        return raw_spectrum.within(self.limits)


reading_routine_manager.subscribe(RawTxtReadingRoutine())
reading_routine_manager.subscribe(MetaTxtReadingRoutine())
