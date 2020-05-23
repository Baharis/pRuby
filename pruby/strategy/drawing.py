from abc import abstractmethod
import matplotlib as mpl
import matplotlib.pyplot as plt


class TemplateDrawingStrategy:
    @abstractmethod
    def draw(self, calc):
        pass

    def draw_initialize(self, calc):
        if calc.fig is None:
            self.draw_new_figure(calc)
        else:
            if not plt.fignum_exists(calc.fig.number):
                self.draw_new_figure(calc)
        calc.color = next(calc.color_cycle)

    @staticmethod
    def draw_new_figure(calc):
        mpl.use('TkAgg')
        calc.fig, calc.ax = plt.subplots()
        plt.minorticks_on()
        plt.grid(b=True, which='major', color='gray', alpha=0.2)
        plt.grid(b=True, axis='x', which='minor', color='gray', alpha=0.2)
        plt.grid(b=True, axis='y', which='major', color='gray', alpha=0.2)
        plt.tick_params(axis='x', which='minor', bottom=True)


    @staticmethod
    def draw_spectrum(calc, x, y):
        lab = str(calc.p if not calc.filename else calc.filename)
        calc.ax.plot(x, y, calc.color, marker='.', ls='None', label=lab)

    @staticmethod
    def draw_curve(calc, spectrum, bg=False):
        y = -spectrum.f if bg else spectrum.f
        ls = '--' if bg else '-'
        calc.ax.plot(spectrum.x, y, calc.color, ls=ls)
        calc.ax.fill_between(x=spectrum.x, y1=y, color=calc.color, alpha=0.2,
                             where=[_ in spectrum.focus for _ in spectrum.x])

    @staticmethod
    def draw_vline(calc, x):
        calc.ax.axvline(x, color=calc.color)

    @staticmethod
    def draw_finalize(calc):
        calc.ax.set_xlim([min(calc.peak_spectrum.x), max(calc.peak_spectrum.x)])
        calc.ax.annotate('nm', xy=(1, 0), ha='left', va='top',
                         xytext=(10, - 3 - mpl.rcParams['xtick.major.pad']),
                         xycoords='axes fraction', textcoords='offset points')
        plt.legend()
        plt.show(block=False)


class ComplexDrawingStrategy(TemplateDrawingStrategy):
    name = 'Traditional'

    def draw(self, calc):
        self.draw_initialize(calc)
        self.draw_spectrum(calc, calc.peak_spectrum.x, calc.peak_spectrum.y)
        self.draw_curve(calc, calc.peak_spectrum)
        self.draw_curve(calc, calc.back_spectrum, bg=True)
        self.draw_vline(calc, calc.r1.n)
        self.draw_vline(calc, calc.r2.n)
        self.draw_finalize(calc)


class SimpleDrawingStrategy(TemplateDrawingStrategy):
    name = 'Simple'

    def draw(self, calc):
        self.draw_initialize(calc)
        self.draw_spectrum(calc, calc.peak_spectrum.x, calc.peak_spectrum.y)
        self.draw_vline(calc, calc.r1.n)
        self.draw_finalize(calc)


# So seemingly the application breaks if matplotlib objects are created before
# the tk object. Most likely a default root of mpl is made before explicit root
# of tk and variables are bound there. Details: bugs.python.org/issue38292.
