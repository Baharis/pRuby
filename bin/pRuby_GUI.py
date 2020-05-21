import os
import tkinter as tk
import uncertainties as uc
from natsort import natsorted

import pruby.tkinter.variables
from pruby.constants import R1_0, T_0, P_0
from pruby.calculator import PressureCalculator
from pruby.tkinter import StringVar, UfloatVar, BooleanVar, StatusBar,\
    Entry, Label, Button, open_file_dialogue, show_about, show_error


class Application(tk.Frame):

    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        os.chdir(os.path.expanduser('~/'))

        # SETTING CONSTANTS
        self.r1_ref = R1_0
        self.t_ref = T_0
        self.p_ref = P_0  # was ufloat(0.0, 0.28)
        self.autodraw = BooleanVar(value=False)
        self.calc = PressureCalculator()

        # method string variables
        self.reading_strategy = StringVar(self.calc.strategy.reader.name)
        self.backfitting_strategy = StringVar(self.calc.strategy.backfitter.name)
        self.peakfitting_strategy = StringVar(self.calc.strategy.peakfitter.name)
        self.correcting_strategy = StringVar(self.calc.strategy.corrector.name)
        self.translating_strategy = StringVar(self.calc.strategy.translator.name)
        self.drawing_strategy = StringVar(self.calc.strategy.drawer.name)

        # BUILDING TOP MENU
        self.menu = tk.Menu(self)
        root.config(menu=self.menu)

        self.menu_data = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Data", menu=self.menu_data)
        self.menu_data.add_command(label='Load',
                                   command=self.open_file_dialogue)
        self.menu_data.add_command(label='Draw',
                                   command=self.data_draw)
        self.menu_data.add_command(label='To reference',
                                   command=self.save_reference)
        self.menu_data.add_command(label='From reference',
                                   command=self.load_reference)
        self.menu_data.add_checkbutton(label='Auto draw', onvalue=True,
                                       offvalue=False, variable=self.autodraw)

        self.menu_options = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Options", menu=self.menu_options)

        def make_options_submenu(strategy_list, str_var, label):
            self.menu_options.add_command(label=label, state='disabled')
            for strategy in strategy_list:
                self.menu_options.add_radiobutton(label=strategy.name,
                value=strategy.name, variable=str_var, command=self.set_methods)
            self.menu_options.add_separator()  # separators if necessary

        make_options_submenu(self.calc.strategy.readers,
                             self.reading_strategy, 'Reading')
        make_options_submenu(self.calc.strategy.backfitters,
                             self.backfitting_strategy, 'Background fitting')
        make_options_submenu(self.calc.strategy.peakfitters,
                             self.peakfitting_strategy, 'Spectrum fitting')
        make_options_submenu(self.calc.strategy.correctors,
                             self.correcting_strategy, 'Temperature correction')
        make_options_submenu(self.calc.strategy.translators,
                            self.translating_strategy, 'Pressure determination')
        make_options_submenu(self.calc.strategy.drawers,
                             self.drawing_strategy, 'Drawing style')
        self.menu.add_command(label='?', command=show_about)

        # ENTRY AREA - file
        self.filename = StringVar('')
        self.file_entry = Entry(self, self.filename, self.file_from_entry)
        self.file_entry.grid(row=0, column=1, columnspan=2, padx=1, pady=1)
        self.file_prev_button = Button(self, '\u25c0', self.file_to_previous)
        self.file_prev_button.grid(row=0, column=0)
        self.file_next_button = Button(self, '\u25b6', self.file_to_next)
        self.file_next_button.grid(row=0, column=3)

        # ENTRY AREA - r1
        self.r1 = pruby.tkinter.variables.UfloatVar(value=self.r1_ref)
        Label(self, text='R1').grid(row=1, column=0)
        self.r1_entry = Entry(self, var=self.r1, cmd=self.recalculate_p)
        self.r1_entry.grid(row=1, column=1, columnspan=2)
        Label(self, text='nm').grid(row=1, column=3)

        # ENTRY AREA - t
        self.t = pruby.tkinter.variables.UfloatVar(value=self.t_ref)
        Label(self, text='t').grid(row=2, column=0)
        self.t_entry = Entry(self, var=self.t, cmd=self.recalculate_p)
        self.t_entry.grid(row=2, column=1, columnspan=2)
        Label(self, text='K').grid(row=2, column=3)  # celsius'\u00B0C'

        # ENTRY AREA - p
        self.p = pruby.tkinter.variables.UfloatVar(value=self.p_ref)
        Label(self, text='p').grid(row=3, column=0)
        self.p_entry = Entry(self, var=self.p, cmd=self.recalculate_r)
        self.p_entry.grid(row=3, column=1, columnspan=2)
        Label(self, text='GPa').grid(row=3, column=3)

        # status bar
        self.status_bar = StatusBar(self)
        self.status_bar.grid(row=4, column=0, columnspan=4)

        # final touches to make sure everything works
        self.recalculate_p()
        self.set_methods()

    def recalculate_p(self, *_):
        # calculate the shift for current calculator
        self.calc.shift = 0.0
        self.calc.t = self.t_ref
        self.calc.p = 0.0
        self.calc.calculate_r1_from_p()
        self.calc.shift = self.r1_ref - self.calc.r1
        # calculate the pressure for current data
        self.calc.r1 = uc.ufloat_fromstr(self.r1.get())
        self.calc.t = uc.ufloat_fromstr(self.t.get())
        self.calc.calculate_p_from_r1()
        self.p.set(value=self.calc.p)
        if self.autodraw.get() is True:
            self.data_draw()

    def recalculate_r(self, *_):
        self.calc.p = uc.ufloat_fromstr(self.p.get())
        self.calc.t = uc.ufloat_fromstr(self.t.get())
        self.calc.calculate_r1_from_p()
        self.r1.set(self.calc.r1)

    def open_file_dialogue(self):
        path = open_file_dialogue()
        directory, filename = os.path.split(path)
        if directory:
            os.chdir(directory)
            self.change_file(filename)

    def change_file(self, filename):
        self.filename.set(filename)
        if filename is '':
            return
        try:
            self.calc.filename = filename
            self.calc.read_and_fit()
        except RuntimeError:
            show_error('Fitting failed! Consider changing fiting strategy.')
            return
        except FileNotFoundError:
            show_error('The file does not exist')
            return
        except (TypeError, ValueError, UnicodeDecodeError):
            show_error('Cannot interpret file content')
            return
        except PermissionError:
            show_error('No permissions to read this file')
            return
        self.r1.set(value=self.calc.r1)
        self.recalculate_p()

    def file_to_next(self):
        return self.change_file(self.get_filename(self.filename.get(), shift=+1))

    def file_to_previous(self):
        return self.change_file(self.get_filename(self.filename.get(), shift=-1))

    def file_from_entry(self, *_):
        filename = self.filename.get()
        if os.path.isfile(os.path.join(os.getcwd(), filename)):
            self.change_file(filename)
        elif os.path.isfile(filename):
            self.change_file(filename)

    def save_reference(self):
        self.r1_ref = uc.ufloat_fromstr(self.r1.get())
        self.t_ref = uc.ufloat_fromstr(self.t.get())
        self.p_ref = uc.ufloat_fromstr(self.p.get())
        self.recalculate_p()

    def load_reference(self):
        self.r1.set(self.r1_ref)
        self.t.set(self.t_ref)
        self.recalculate_p()

    @staticmethod
    def get_filename(filename, shift=0):
        files = [f for f in os.listdir(os.getcwd()) if not os.path.isdir(f)]
        files = natsorted(files)
        try:
            index = files.index(filename)
        except ValueError:
            index, shift = 0, 0
        return files[(len(files) + index + shift) % len(files)]

    def set_methods(self):
        self.calc.strategy.set(
            reading=self.reading_strategy.get(),
            backfitting=self.backfitting_strategy.get(),
            peakfitting=self.peakfitting_strategy.get(),
            correcting=self.correcting_strategy.get(),
            translating=self.translating_strategy.get(),
            drawing=self.drawing_strategy.get())
        self.recalculate_p()

    def data_draw(self):
        try:
            self.calc.draw()
        except AttributeError:
            show_error('Peak spectrum is empty! Load data to draw.')


# MAIN PROGRAM
if __name__ == '__main__':
    root = tk.Tk()
    app_wd = os.getcwd()
    app = Application(root).pack(side='top', fill='both', expand=True)
    root.title('pRuby')
    root.attributes("-topmost", True)
    icon = tk.PhotoImage(file=app_wd + '/resources/icon.gif')
    root.tk.call('wm', 'iconphoto', root._w, icon)
    # TODO for some bizzare reason the icon died while moving drawing to routine
    # TODO also looks like text fields are suddenly empty and can't be filled ?!
    # TODO tommorow. tired.
    root.resizable(False, False)
    root.mainloop()
