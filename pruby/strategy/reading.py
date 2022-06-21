from abc import abstractmethod
import numpy as np
from ..spectrum import Spectrum


class ReadingStrategy:
    @staticmethod
    @abstractmethod
    def read(calc):
        pass


class RawTxtReadingStrategy(ReadingStrategy):
    name = 'Raw txt'

    @staticmethod
    def read(calc):
        data = np.loadtxt(calc.dat_path, dtype=(float, float))
        x_list, y_list = data[:, 0], data[:, 1]
        calc.raw_spectrum = Spectrum(x_list, y_list).within(calc.limits)


class MetaTxtReadingStrategy(ReadingStrategy):
    name = 'Metadata txt'

    @staticmethod
    def read(calc):
        with open(calc.dat_path, "r") as file:
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
        calc.raw_spectrum = Spectrum(x_list, y_list).within(calc.limits)
