import numpy as np
from .base import RoutineManager
from pruby.spectrum import Spectrum

reading_routine_manager = RoutineManager()


class RawTxtReadingRoutine:
    def __init__(self):
        self.name = 'Raw text file'
        self.raw_spectrum = None
        reading_routine_manager.subscribe(self)

    def read(self, filepath):
        raw_data = np.loadtxt(filepath, dtype=(float, float))
        self.raw_spectrum = Spectrum(x=raw_data[:, 0], y=raw_data[:, 1])


class MetaTxtReadingRoutine:
    def __init__(self):
        self.name = 'Text file with metadata'
        self.raw_spectrum = None
        reading_routine_manager.subscribe(self)

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
        self.raw_spectrum = Spectrum(x=x_list, y=y_list)
