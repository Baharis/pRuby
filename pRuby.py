import os
import tkinter as tk
import tkinter.filedialog as tkfd
import tkinter.messagebox as tkmb
import matplotlib as mpl
import matplotlib.pyplot as pp
import numpy as np
import uncertainties as uc

from methods import peakhunt
from methods import shifttop
from methods import tempcorr
from utility.cycle_generator import cycle_generator
import utility.tk_objects as tkob


class Application(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        os.chdir(os.path.expanduser('~'))

        # SETTING CONSTANTS
        self.r1_ref = uc.ufloat(694.2, 0.1)
        self.t_ref = uc.ufloat(24.85, 0.1)
        self.p1_ref = uc.ufloat(0.0, 0.28)
        self.r1_sam = self.r1_ref
        self.t_sam = self.t_ref
        self.p1_sam = self.p1_ref
        self.dots = None
        self.data_autodraw = tk.BooleanVar(value=False)
        self.filenext = ''
        self.fileprevious = ''
        self.fit_color_cycle = cycle_generator(('r', 'g', 'b', 'c', 'm', 'y'))
        self.fit_successful = True
        self.peakhunt_results = {}
        self.peakhunt_method = peakhunt.default()
        self.shifttop_method = shifttop.default()
        self.tempcorr_method = tempcorr.default()
        self.method_peakhunt_stringvar = \
            tk.StringVar(value=peakhunt.default().__name__)
        self.method_shifttop_stringvar = \
            tk.StringVar(value=shifttop.default().__name__)
        self.method_tempcorr_stringvar = \
            tk.StringVar(value=tempcorr.default().__name__)
        self.peakhunt_methods = peakhunt.methods()
        self.shifttop_methods = shifttop.methods()
        self.tempcorr_methods = tempcorr.methods()

        # BUILDING MENU
        self.menu = tk.Menu(self)
        root.config(menu=self.menu)
        self.menu_data = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Data", menu=self.menu_data)
        self.menu_data.add_command(label='Import',
                                   command=self.data_import)
        self.menu_data.add_command(label='Draw',
                                   command=self.data_draw)
        self.menu_data.add_command(label='To reference',
                                   command=self.data_to_reference)
        self.menu_data.add_command(label='From reference',
                                   command=self.data_from_reference)
        self.menu_data.add_checkbutton(label='Auto draw',
                                       onvalue=True, offvalue=False,
                                       variable=self.data_autodraw)
        self.menu_methods = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Methods", menu=self.menu_methods)
        for key, m in self.peakhunt_methods.items():
            self.menu_methods.add_radiobutton(
                label=m['name'], variable=self.method_peakhunt_stringvar,
                value=m['function'].__name__, command=self.methods_set)
        self.menu_methods.add_separator()
        for key, m in self.tempcorr_methods.items():
            self.menu_methods.add_radiobutton(
                label=m['name'], variable=self.method_tempcorr_stringvar,
                value=m['function'].__name__, command=self.methods_set)
        self.menu_methods.add_separator()
        for key, m in self.shifttop_methods.items():
            self.menu_methods.add_radiobutton(
                label=m['name'], variable=self.method_shifttop_stringvar,
                value=m['function'].__name__, command=self.methods_set)
        self.menu.add_command(label='?', command=self.about)

        # ENTRY AREA - file
        self.filename_stringvar = tk.StringVar(value='')
        self.file_previous_button = tk.Button(self, text='\u25c0',
            command=self.file_toprevious)
        self.file_previous_button.grid(row=0, column=0)
        self.file_entry = tk.Entry(self, textvariable=self.filename_stringvar,
                                   width=12, justify='left')
        self.file_entry.grid(row=0, column=1, columnspan=2, padx=1, pady=1)
        self.file_entry.bind('<Return>', self.file_fromentry)
        self.file_next_button = tk.Button(self, text='\u25b6',
            command=self.file_tonext)
        self.file_next_button.grid(row=0, column=3)

        # ENTRY AREA - r1
        self.r1_ufloatvar = tkob.UfloatVar(value=self.r1_ref)
        tk.Label(self, text='R1').grid(row=1, column=0)
        self.r1_entry = tkob.Entry(self, textvariable=self.r1_ufloatvar,
                                   command=self.calculate_p1)
        self.r1_entry.grid(row=1, column=1, columnspan=2)
        tkob.Label(self, text='nm').grid(row=1, column=3)

        # ENTRY AREA - t
        self.t_ufloatvar = tkob.UfloatVar(value=self.t_ref)
        tk.Label(self, text='t').grid(row=2, column=0)
        self.t_entry = tkob.Entry(self, textvariable=self.t_ufloatvar,
                                command=self.calculate_p1)
        self.t_entry.grid(row=2, column=1, columnspan=2)
        tk.Label(self, text='\u00B0C').grid(row=2, column=3)

        # ENTRY AREA - p1
        self.p1_ufloatvar = tkob.UfloatVar(value=self.p1_ref)
        tk.Label(self, text='p1').grid(row=3, column=0)
        self.p1_entry = tkob.Entry(self, textvariable=self.p1_ufloatvar,
                                 command=self.calculate_p1)
        self.p1_entry.grid(row=3, column=1, columnspan=2)
        tk.Label(self, text='GPa').grid(row=3, column=3)

    def calculate_p1(self, *_):
        self.r1_sam = uc.ufloat_fromstr(self.r1_entry.get())
        self.t_sam = uc.ufloat_fromstr(self.t_entry.get())
        peakhunt_arguments = {'tempcorr_method': self.tempcorr_method,
                              'shifttop_method': self.shifttop_method,
                              'r1_sam': self.r1_sam, 't_sam': self.t_sam,
                              'r1_ref': self.r1_ref, 't_ref': self.t_ref}
        self.p1_sam = self.shifttop_method(**peakhunt_arguments)
        self.p1_ufloatvar.set(value=self.p1_sam)

    @staticmethod
    def about():
        message = 'pRuby - pressure estimation based on ruby fluorescence ' \
                  'spectrum by Daniel Tcho\u0144\n\n'\
                  'For details and help, visit pRuby page' \
                  '(https://github.com/Baharis/pRuby).'
        tkmb.showinfo(title='About pRuby', message=message)

    @staticmethod
    def cut_dots_to_690_700(dots):
        dots = dots[dots[:, 0].argsort()]
        new_dots = []
        for x, y in zip(dots[:, 0], dots[:, 1]):
            if 690 <= x <= 700:
                new_dots.append([x, y])
        return np.array(new_dots, dtype=(float, float))

    @staticmethod
    def _parse_txt(path):
        return np.loadtxt(path, dtype=(float, float))

    @staticmethod
    def _parse_other(path):
        file = open(path, "r")
        dots = []
        for line in file.readlines():
            try:
                x = float(line.strip().split()[0])
                y = float(line.strip().split()[1])
            except ValueError:
                pass
            else:
                dots.append([x, y])
        return np.array(dots, dtype=(float, float))

    def data_draw(self):
        # RETURN IF NO FILE HAS BEEN IMPORTED YET
        if self.dots is None:
            tkmb.showinfo(message='Import data to draw!')
            return

        # SET BASIC GEOMETRY AND STYLE
        dots_x = self.dots[:, 0]
        dots_y = self.dots[:, 1]
        x_min = 690.0
        x_max = 700.0
        x_span = x_max - x_min
        y_span = np.max(dots_y) - np.min(dots_y)
        y_min = min(np.min(dots_y) - 0.01 * y_span, 0)
        y_max = np.max(dots_y) + 0.20 * y_span
        active_color = next(self.fit_color_cycle)
        pp.minorticks_on()
        pp.grid(b=True, which='major', color='gray', alpha=0.2)
        pp.grid(b=True, axis='x', which='minor', color='gray', alpha=0.1)
        pp.grid(b=True, axis='y', which='major', color='gray', alpha=0.1)
        pp.tick_params(axis='x', which='minor', bottom='on')

        # DRAW ELEMENTS OF LAST PEAKHUNT AND FIT:
        # DOTS
        label = self.filename_stringvar.get() + ', ' + \
                self.method_peakhunt_stringvar.get()
        pp.plot(dots_x, dots_y, marker='.', color=active_color,
                linestyle='None', label=label)

        if self.fit_successful:
            # PEAK POSITIONS
            pp.plot(self.peakhunt_results['r1_val'],
                    self.peakhunt_results['r1_int'],
                    color=active_color, marker='v', markersize='8')
            pp.plot(self.peakhunt_results['r2_val'],
                    self.peakhunt_results['r2_int'],
                    color=active_color, marker='v', markersize='8')

            # CURVES AND FILLS
            for fit_function, fit_range in \
                    zip(self.peakhunt_results['fit_function'],
                        self.peakhunt_results['fit_range']):
                curve_x = np.linspace(start=fit_range[0], stop=fit_range[1],
                                      num=int(100 * (fit_range[1] - fit_range[0])))
                pp.plot(curve_x, fit_function(curve_x), linestyle='-',
                        color=active_color)
                pp.fill_between(x=curve_x, y1=y_min, y2=fit_function(curve_x),
                                color=active_color, alpha=0.1)

        # X-AXIS AND LEGEND
        ax = pp.gca()
        ax.set_xlim([x_min, x_max])
        ax.annotate('nm', xy=(1, 0), ha='left', va='top',
                    xytext=(10, - 3 - mpl.rcParams['xtick.major.pad']),
                    xycoords='axes fraction', textcoords='offset points')
        pp.legend()
        pp.show()

    def data_fit(self):
        try:
            self.peakhunt_results = self.peakhunt_method(self.dots)
        except RuntimeError:
            tkmb.showerror(message='Data could not be fitted! '
                                   'Consider changing the peakhunt method.')
            self.fit_successful = False
        else:
            self.fit_successful = True
            self.r1_sam = uc.ufloat(self.peakhunt_results['r1_val'],
                                    self.peakhunt_results['r1_unc'])
            self.r1_ufloatvar.set(value=self.r1_sam)
            print(self.peakhunt_results)

    def data_import(self):
        path = tkfd.askopenfilename(
            title='Open ruby file...',
            filetypes=(("Text files", "*.txt"), ("All files", "*.*")),
            initialdir=os.getcwd())
        self.file_change(path)

    def file_change(self, path):
        if len(path) > 0:
            try:
                dots = self._parse_txt(path)
            except ValueError:
                try:
                    dots = self._parse_other(path)
                except ValueError:
                    tkmb.showerror(message='Cannot interpret file content')
                    return
            except PermissionError:
                tkmb.showerror(message='No permissions to read this file')
                return
            except TypeError:
                tkmb.showerror(message='Cannot interpret file content')
                return
        else:
            return
        directory, filename = os.path.split(path)
        self.filename_stringvar.set(filename)
        try:
            os.chdir(directory)
        except FileNotFoundError:
            pass
        self.file_list()
        self.dots = self.cut_dots_to_690_700(dots=dots)
        self.data_fit()
        self.calculate_p1()
        if self.data_autodraw.get() is True:
            self.data_draw()

    def data_to_reference(self):
        self.r1_ref = uc.ufloat_fromstr(self.r1_ufloatvar.get())
        self.t_ref = uc.ufloat_fromstr(self.t_ufloatvar.get())
        self.p1_ref = uc.ufloat_fromstr(self.p1_ufloatvar.get())

    def data_from_reference(self):
        self.r1_sam = self.r1_ref
        self.r1_ufloatvar.set(self.r1_sam)
        self.t_sam = self.t_ref
        self.t_ufloatvar.set(self.t_sam)
        self.p1_sam = self.p1_ref
        self.p1_ufloatvar.set(self.p1_sam)
        self.calculate_p1()

    def file_fromentry(self, *_):
        filename = self.file_entry.get()
        if os.path.isfile(os.path.join(os.getcwd(), filename)):
            self.file_change(filename)
        elif os.path.isfile(filename):
            self.file_change(filename)

    def file_list(self):
        filelist = []
        for filename in os.listdir(os.getcwd()):
            if not os.path.isdir(filename):
                filelist.append(filename)
        filelist.sort()
        fileindex = filelist.index(self.filename_stringvar.get())
        try:
            self.filenext = filelist[(fileindex + 1) % len(filelist)]
        except IndexError:
            self.filenext = ''
        try:
            self.fileprevious = filelist[fileindex - 1]
        except IndexError:
            self.fileprevious = ''

    def file_tonext(self):
        self.file_change(self.filenext)

    def file_toprevious(self):
        self.file_change(self.fileprevious)

    def methods_set(self):
        self.peakhunt_method = \
         self.peakhunt_methods[self.method_peakhunt_stringvar.get()]['function']
        self.shifttop_method = \
         self.shifttop_methods[self.method_shifttop_stringvar.get()]['function']
        self.tempcorr_method =\
         self.tempcorr_methods[self.method_tempcorr_stringvar.get()]['function']
        if self.dots is not None:
            self.data_fit()
        if self.data_autodraw.get() is True:
            self.data_draw()
        self.calculate_p1()


# MAIN PROGRAM
if __name__ == '__main__':
    root = tk.Tk()
    app_wd = os.getcwd()
    Application(root).pack(side='top', fill='both', expand=True)
    root.title('pRuby')
    root.attributes("-topmost", True)
    icon = tk.PhotoImage(file=app_wd + '/resources/icon.gif')
    root.tk.call('wm', 'iconphoto', root._w, icon)
    root.resizable(False, False)
    root.mainloop()
