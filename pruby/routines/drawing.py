import numpy as np
from pruby.spectrum import Spectrum, Curve
from pruby.utility import LineSubset, cycle
import matplotlib as mpl
import matplotlib.pyplot as plt


class TemplateDrawingRoutine:
    def __init__(self):
        self.fig, self.ax = None, None
        self.color_cycle = cycle('r', 'g', 'b', 'c', 'm', 'y')
        self.color = 'k'

    def draw_initialize(self):
        if self.fig is None:
            mpl.use('TkAgg')
            fig, ax = plt.subplots()
            plt.minorticks_on()
            plt.grid(b=True, which='major', color='gray', alpha=0.2)
            plt.grid(b=True, axis='x', which='minor', color='gray', alpha=0.2)
            plt.grid(b=True, axis='y', which='major', color='gray', alpha=0.2)
            plt.tick_params(axis='x', which='minor', bottom=True)
            self.fig, self.ax = fig, ax
        self.color = next(self.color_cycle)

    def draw_spectrum(self, x, y, lab):
        self.ax.plot(x, y, self.color, marker='.', ls='None', label=lab)

    def draw_curve(self, x, f, focus, bg=False):
        y = -np.array(list(map(f, x))) if bg else np.array(list(map(f, x)))
        ls = '--' if bg else '-'
        self.ax.plot(x, y, self.color, ls=ls)
        self.ax.fill_between(x=x, y1=y, color=self.color, alpha=0.2,
                             where=[_ in focus for _ in x])

    def draw_peak(self, x, y):
        # self.ax.plot(x, y, color=self.color, marker='v', ms='8') #triangle
        self.ax.axvline(x, color=self.color)

    def draw_finalize(self):
        plt.legend()
        plt.show(block=False)


class TraditionalDrawingRoutine(TemplateDrawingRoutine):
    name = 'Traditional'

    def draw(self, r1_x, r1_y, r2_x, r2_y, label,
             peak_spect=Spectrum(), back_spect=Spectrum(),
             peak_curve=Curve(), back_curve=Curve(),
             peak_focus=LineSubset(), back_focus=LineSubset()):
        self.draw_initialize()
        self.draw_spectrum(peak_spect.x, peak_spect.y, label)
        self.draw_curve(peak_spect.x, peak_curve, peak_focus)
        self.draw_curve(back_spect.x, back_curve, back_focus, bg=True)
        self.draw_peak(r1_x.n, r1_y.n)
        self.draw_peak(r2_x.n, r2_y.n)
        self.ax.set_xlim([min(peak_spect.x), max(peak_spect.x)])
        self.ax.annotate('nm', xy=(1, 0), ha='left', va='top',
                         xytext=(10, - 3 - mpl.rcParams['xtick.major.pad']),
                         xycoords='axes fraction', textcoords='offset points')
        self.draw_finalize()


class SimpleDrawingRoutine(TemplateDrawingRoutine):
    name = 'Simple'

    def draw(self, r1_x, r1_y, r2_x, r2_y, label,
             peak_spect=Spectrum(), back_spect=Spectrum(),
             peak_curve=Curve(), back_curve=Curve(),
             peak_focus=LineSubset(), back_focus=LineSubset()):
        self.draw_initialize()
        self.draw_spectrum(peak_spect.x, peak_spect.y, label)
        self.draw_peak(r1_x.n, r1_y.n)
        self.ax.set_xlim([min(peak_spect.x), max(peak_spect.x)])
        self.ax.annotate('nm', xy=(1, 0), ha='left', va='top',
                         xytext=(10, - 3 - mpl.rcParams['xtick.major.pad']),
                         xycoords='axes fraction', textcoords='offset points')
        self.draw_finalize()

# So seemingly the application breaks if matplotlib objects are created before
# the tk object. Most likely a default root of mpl is made before explicit root
# of tk and variables are bound there. Details: bugs.python.org/issue38292.
