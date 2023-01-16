import abc
import numpy as np
from collections import OrderedDict
from uncertainties import ufloat_fromstr
from pruby.strategies.base import BaseStrategy, BaseStrategies
from pruby.spectrum import Spectrum


class ReadingStrategy(BaseStrategy, abc.ABC):
    @staticmethod
    @abc.abstractmethod
    def read(calc):
        raise NotImplementedError


class ReadingStrategies(BaseStrategies):
    registry = OrderedDict()
    strategy_type = ReadingStrategy


@ReadingStrategies.register()
class RawTxtReadingStrategy(ReadingStrategy):
    name = 'Raw spectrum txt'

    @staticmethod
    def read(calc):
        data = np.loadtxt(calc.dat_path, dtype=(float, float))
        x_list, y_list = data[:, 0], data[:, 1]
        calc.raw_spectrum = Spectrum(x_list, y_list).within(calc.limits)


@ReadingStrategies.register(default=True)
class MetaTxtReadingStrategy(ReadingStrategy):
    name = 'Metadata spectrum txt'

    @staticmethod
    def read(calc):
        with open(calc.dat_path, 'r') as file:
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


@ReadingStrategies.register()
class SingleLineReadingStrategy(ReadingStrategy):
    name = 'Single value txt'

    @staticmethod
    def read(calc):
        with open(calc.dat_path, 'r') as file:
            first_line = file.readline().split()
            r1 = ufloat_fromstr(first_line[0])
            try:
                intensity = ufloat_fromstr(first_line[1])
            except (IndexError, ValueError):
                intensity = 1
        calc.raw_spectrum = calc.peak_spectrum = Spectrum([r1], [intensity])
        calc.r1 = r1
