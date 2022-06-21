import abc
import matplotlib as mpl
import matplotlib.pyplot as plt
from pruby.utility import cycle


class DrawingStrategy(abc.ABC):
    @property
    @abc.abstractmethod
    def name(self) -> str:
        pass

    @abc.abstractmethod
    def draw(self, calc):
        pass


class BaseDrawingStrategy(DrawingStrategy, abc.ABC):
    color_cycle = cycle(['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
                         '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'])

    def __init__(self):
        self.calc = None
        self.fig: plt.Figure
        self.ax: plt.Axes
        self.fig, self.ax = plt.subplots()
        self.color = '#000000'

    def draw_initialize(self, calc):
        self.calc = calc
        if not self.calc.fig.axes:
            self.draw_new_figure()
        elif not plt.fignum_exists(self.calc.fig.number):
            self.draw_new_figure()
        self.color = next(self.color_cycle)

    def draw_new_figure(self):
        mpl.use('TkAgg')
        self.fig, self.ax = plt.subplots()
        self.ax.minorticks_on()
        self.ax.grid(b=True, which='major', color='gray', alpha=0.2)
        self.ax.grid(b=True, axis='x', which='minor', color='gray', alpha=0.2)
        self.ax.grid(b=True, axis='y', which='major', color='gray', alpha=0.2)
        self.ax.tick_params(axis='x', which='minor', bottom=True)

    def draw_spectrum(self, x, y):
        lab = str(self.calc.p if not self.calc.dat_path else self.calc.dat_path)
        self.ax.plot(x, y, self.color, marker='.', ls='None', label=lab)

    def draw_curve(self, spectrum, bg=False):
        y = -spectrum.f if bg else spectrum.f
        ls = '--' if bg else '-'
        self.ax.plot(spectrum.x, y, self.color, ls=ls)
        self.ax.fill_between(x=spectrum.x, y1=y, color=self.color, alpha=0.2,
                             where=[_ in spectrum.focus for _ in spectrum.x])

    def draw_vline(self, x):
        self.ax.axvline(x, color=self.color)

    def draw_finalize(self):
        self.ax.set_xlim([min(self.calc.peak_spectrum.x),
                          max(self.calc.peak_spectrum.x)])
        self.ax.annotate('nm', xy=(1, 0), ha='left', va='top',
                         xytext=(10, - 3 - mpl.rcParams['xtick.major.pad']),
                         xycoords='axes fraction', textcoords='offset points')
        self.ax.legend()
        self.calc.fig = self.fig
        plt.show(block=True)  # this should change in gui and line


class ComplexDrawingStrategy(BaseDrawingStrategy):
    name = 'Traditional'

    def draw(self, calc):
        self.draw_initialize(calc)
        self.draw_spectrum(calc.peak_spectrum.x, calc.peak_spectrum.y)
        self.draw_curve(calc.peak_spectrum)
        self.draw_curve(calc.back_spectrum, bg=True)
        self.draw_vline(calc.r1.n)
        self.draw_vline(calc.r2.n)
        self.draw_finalize()


class SimpleDrawingStrategy(BaseDrawingStrategy):
    name = 'Simple'

    def draw(self, calc):
        self.draw_initialize(calc)
        self.draw_spectrum(calc.peak_spectrum.x, calc.peak_spectrum.y)
        self.draw_vline(calc.r1.n)
        self.draw_finalize()
