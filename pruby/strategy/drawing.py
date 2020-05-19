from abc import abstractmethod
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from .base import Strategy


class TemplateDrawingStrategy:
    @abstractmethod
    def draw(self, calc):
        pass

    @staticmethod
    def draw_initialize(calc):
        mpl.use('TkAgg')
        fig, ax = plt.subplots()
        plt.minorticks_on()
        plt.grid(b=True, which='major', color='gray', alpha=0.2)
        plt.grid(b=True, axis='x', which='minor', color='gray', alpha=0.2)
        plt.grid(b=True, axis='y', which='major', color='gray', alpha=0.2)
        plt.tick_params(axis='x', which='minor', bottom=True)
        calc.fig, calc.ax = fig, ax
        calc.color = next(calc.color_cycle)

    @staticmethod
    def draw_spectrum(calc, x, y):
        lab = str(calc.p if not calc.filename else calc.filename)
        calc.ax.plot(x, y, calc.color, marker='.', ls='None', label=lab)

    @staticmethod
    def draw_curve(calc, x, f, focus, bg=False):
        y = -np.array(list(map(f, x))) if bg else np.array(list(map(f, x)))
        ls = '--' if bg else '-'
        calc.ax.plot(x, y, calc.color, ls=ls)
        calc.ax.fill_between(x=x, y1=y, color=calc.color, alpha=0.2,
                             where=[_ in focus for _ in x])

    @staticmethod
    def draw_vline(calc, x):
        calc.ax.axvline(x, color=calc.color)

    @staticmethod
    def draw_finalize():
        plt.legend()
        plt.show(block=False)


class ComplexDrawingStrategy(TemplateDrawingStrategy):
    name = 'Traditional'

    def draw(self, calc):
        self.draw_initialize(calc)
        self.draw_spectrum(calc, calc.peak_spectrum.x, calc.peak_spectrum.y)
        self.draw_curve(calc, calc.peak_spectrum.x, calc.peak_spectrum.f,
                        calc.peak_spectrum.focus)
        self.draw_curve(calc, calc.back_spectrum.x, calc.back_spectrum.f,
                        calc.back_spectrum.focus, bg=True)
        self.draw_vline(calc, calc.r1.n)
        self.draw_vline(calc, calc.r2.n)
        calc.ax.set_xlim([min(calc.peak_spect.x), max(calc.peak_spect.x)])
        calc.ax.annotate('nm', xy=(1, 0), ha='left', va='top',
                         xytext=(10, - 3 - mpl.rcParams['xtick.major.pad']),
                         xycoords='axes fraction', textcoords='offset points')
        self.draw_finalize()


class SimpleDrawingStrategy(TemplateDrawingStrategy):
    name = 'Simple'

    def draw(self, calc):
        self.draw_initialize(calc)
        self.draw_spectrum(calc, calc.peak_spectrum.x, calc.peak_spectrum.y)
        self.draw_vline(calc, calc.r1.n)
        calc.ax.set_xlim([min(calc.peak_spect.x), max(calc.peak_spect.x)])
        calc.ax.annotate('nm', xy=(1, 0), ha='left', va='top',
                         xytext=(10, - 3 - mpl.rcParams['xtick.major.pad']),
                         xycoords='axes fraction', textcoords='offset points')
        self.draw_finalize()


class DrawingStrategy(Strategy):
    pass


DrawingStrategy.subscribe(ComplexDrawingStrategy)
DrawingStrategy.subscribe(SimpleDrawingStrategy)


# So seemingly the application breaks if matplotlib objects are created before
# the tk object. Most likely a default root of mpl is made before explicit root
# of tk and variables are bound there. Details: bugs.python.org/issue38292.
