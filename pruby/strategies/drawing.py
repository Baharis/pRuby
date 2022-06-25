import abc
from collections import OrderedDict
import matplotlib as mpl
import matplotlib.pyplot as plt
from pruby.strategies import BaseStrategy, BaseStrategies
from pruby.utility import cycle

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pruby import PressureCalculator


class DrawingStrategy(BaseStrategy, abc.ABC):
    calc: 'PressureCalculator'

    @abc.abstractmethod
    def draw(self, calc):
        raise NotImplementedError


class DrawingStrategies(BaseStrategies):
    registry = OrderedDict()
    strategy_type = DrawingStrategy


class BaseDrawingStrategy(DrawingStrategy, abc.ABC):
    def __init__(self):
        if self.interactive:
            mpl.use('TkAgg')
        else:
            mpl.use('Agg')
        plt.close()
        self.calc: 'PressureCalculator'
        self.fig: plt.Figure = plt.figure(figsize=(8, 6), dpi=100)
        self.ax: plt.Axes = self.fig.add_subplot()
        self.color = '#000000'
        self.color_cycle = cycle(
            ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
             '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'])

    @property
    def interactive(self):
        return not bool(self.calc.output_path)

    def draw_initialize(self, calc):
        self.calc = calc
        if not self.calc.fig.axes:
            self.draw_new_figure()
        elif not plt.fignum_exists(self.calc.fig.number):
            self.draw_new_figure()
        self.color = next(self.color_cycle)

    def draw_new_figure(self):
        self.fig = plt.figure(figsize=(8, 6), dpi=100)
        self.ax = self.fig.add_subplot()

    def draw_grid_and_tics(self):
        self.ax.minorticks_on()
        self.ax.grid(b=True, which='major', color='gray', alpha=0.2)
        self.ax.grid(b=True, axis='x', which='minor', color='gray', alpha=0.2)
        self.ax.grid(b=True, axis='y', which='major', color='gray', alpha=0.2)
        self.ax.tick_params(axis='x', which='minor', bottom=True)

    def draw_spectrum(self, x, y):
        if self.interactive:
            label = self.calc.dat_path
        else:
            label = f'p = {self.calc.p} GPa'
        self.ax.plot(x, y, self.color, marker='.', ls='None', label=label)

    def draw_curve(self, spectrum, bg=False):
        y = -spectrum.f if bg else spectrum.f
        ls = '--' if bg else '-'
        self.ax.plot(spectrum.x, y, self.color, ls=ls)
        self.ax.fill_between(x=spectrum.x, y1=y, color=self.color, alpha=0.2,
                             where=[_ in spectrum.focus for _ in spectrum.x])

    def draw_vline(self, x):
        self.ax.axvline(x, color=self.color)

    def draw_finalize(self):
        self.ax.set_xlim(min(self.calc.peak_spectrum.x),
                         max(self.calc.peak_spectrum.x))
        self.ax.annotate('nm', xy=(1, 0), ha='left', va='top',
                         xytext=(10, - 3 - mpl.rcParams['xtick.major.pad']),
                         xycoords='axes fraction', textcoords='offset points')
        self.ax.legend()
        self.calc.fig = self.fig
        if self.interactive:
            self.fig.show()
        else:
            self.fig.savefig(self.calc.output_path)


@DrawingStrategies.register()
class SimpleDrawingStrategy(BaseDrawingStrategy):
    name = 'Simple'

    def draw(self, calc):
        self.draw_initialize(calc)
        self.draw_grid_and_tics()
        self.draw_spectrum(calc.peak_spectrum.x, calc.peak_spectrum.y)
        self.draw_vline(calc.r1.n)
        self.draw_finalize()


@DrawingStrategies.register(default=True)
class ComplexDrawingStrategy(BaseDrawingStrategy):
    name = 'Complex'

    def draw(self, calc):
        self.draw_initialize(calc)
        self.draw_grid_and_tics()
        self.draw_spectrum(calc.peak_spectrum.x, calc.peak_spectrum.y)
        self.draw_curve(calc.peak_spectrum)
        self.draw_curve(calc.back_spectrum, bg=True)
        self.draw_vline(calc.r1.n)
        self.draw_vline(calc.r2.n)
        self.draw_finalize()



