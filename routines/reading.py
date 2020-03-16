import numpy as np
from .base import RoutineManager
from pruby.spectrum import Spectrum

file_reading_routine_manager = RoutineManager()


class RawTxtReadingRoutine:
    name = 'Raw text file'

    def __init__(self):
        self.spectrum = Spectrum()

    def read(self, filepath):
        raw_data = np.loadtxt(filepath, dtype=(float, float))
        self.spectrum = Spectrum(x=raw_data[:, 0], y=raw_data[:, 1])


class MetaTxtReadingRoutine:
    name = 'Text file with metadata'

    def __init__(self):
        self.spectrum = Spectrum()

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
        self.spectrum = Spectrum(x=x_list, y=y_list)


file_reading_routine_manager.subscribe(RawTxtReadingRoutine())
file_reading_routine_manager.subscribe(MetaTxtReadingRoutine())
