import os
import tkinter as tk
import tkinter.filedialog as tkfd
import tkinter.messagebox as tkmb
import matplotlib as mpl
import matplotlib.pyplot as pp
import numpy as np
import uncertainties as uc
from natsort import natsorted

from pruby.strategy.base import routine_manager
from pruby.constants import R1_0, R2_0, T_0, P_0
from pruby.calculator import PressureCalculator
import pruby.utility.tk_objects as tkob


class Application(tk.Frame):

    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        os.chdir(os.path.expanduser('~/'))

        # SETTING CONSTANTS
        self.r1_ref = R1_0
        self.t_ref = T_0
        self.p1_ref = P_0  # was ufloat(0.0, 0.28)
        self.autodraw = tk.BooleanVar(value=False)
        self.calculator = PressureCalculator()

        # method string variables
        self.reading_routine = tk.StringVar(
            value=routine_manager.default['reading'].name)
        self.backfitting_routine = tk.StringVar(
            value=routine_manager.default['backfitting'].name)
        self.peakfitting_routine = tk.StringVar(
            value=routine_manager.default['peakfitting'].name)
        self.correcting_routine = tk.StringVar(
            value=routine_manager.default['correcting'].name)
        self.translating_routine = tk.StringVar(
            value=routine_manager.default['translating'].name)
        self.drawing_routine = tk.StringVar(
            value=routine_manager.default['drawing'].name)

        # BUILDING TOP MENU
        self.menu = tk.Menu(self)
        root.config(menu=self.menu)

        self.menu_data = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Data", menu=self.menu_data)
        self.menu_data.add_command(label='Load', command=self.open_file_dialogue)
        self.menu_data.add_command(label='Draw', command=self.data_draw)
        self.menu_data.add_command(label='To reference', command=self.save_reference)
        self.menu_data.add_command(label='From reference', command=self.load_reference)
        self.menu_data.add_checkbutton(label='Auto draw', onvalue=True,
                                       offvalue=False, variable=self.autodraw)

        self.menu_methods = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Methods", menu=self.menu_methods)

        def make_methods_submenu(role, label):
            self.menu_methods.add_command(label=label, state='disabled')
            for m in routine_manager.names[role]:
                self.menu_methods.add_radiobutton(label=m, value=m,
                    variable=getattr(self, role+'_routine'),
                    command=self.set_methods)
            # self.menu_methods.add_separator() add separators if necessary
        make_methods_submenu('reading', 'Reading')
        make_methods_submenu('backfitting', 'Background fitting')
        make_methods_submenu('peakfitting', 'Spectrum fitting')
        make_methods_submenu('correcting', 'Temperature correction')
        make_methods_submenu('translating', 'Pressure determination')
        make_methods_submenu('drawing', 'Drawing style')
        self.menu.add_command(label='?', command=self.show_about)

        # ENTRY AREA - file
        self.file_name = tk.StringVar(value='')
        self.file_entry = tk.Entry(self, width=12, textvariable=self.file_name)
        self.file_entry.grid(row=0, column=1, columnspan=2, padx=1, pady=1)
        self.file_entry.bind('<Return>', self.file_fromentry)
        self.file_previous = ''
        self.file_previous_button = tk.Button(self, text='\u25c0', command=self.change_file_to_previous)
        self.file_previous_button.grid(row=0, column=0)
        self.file_next = ''
        self.file_next_button = tk.Button(self, text='\u25b6', command=self.change_file_to_next)
        self.file_next_button.grid(row=0, column=3)

        # ENTRY AREA - r1
        self.r1 = tkob.UfloatVar(value=self.r1_ref)
        tk.Label(self, text='R1').grid(row=1, column=0)
        self.r1_entry = tkob.Entry(self, textvariable=self.r1, command=self.recalculate_p)
        self.r1_entry.grid(row=1, column=1, columnspan=2)
        tkob.Label(self, text='nm').grid(row=1, column=3)

        # ENTRY AREA - t
        self.t = tkob.UfloatVar(value=self.t_ref)
        tk.Label(self, text='t').grid(row=2, column=0)
        self.t_entry = tkob.Entry(self, textvariable=self.t, command=self.recalculate_p)
        self.t_entry.grid(row=2, column=1, columnspan=2)
        tk.Label(self, text='\u00B0C').grid(row=2, column=3)

        # ENTRY AREA - p1
        self.p1 = tkob.UfloatVar(value=self.p1_ref)
        tk.Label(self, text='p1').grid(row=3, column=0)
        self.p1_entry = tkob.Entry(self, textvariable=self.p1, command=self.recalculate_r)
        self.p1_entry.grid(row=3, column=1, columnspan=2)
        tk.Label(self, text='GPa').grid(row=3, column=3)

        # final touches to make sure everything works
        self.recalculate_p()
        self.set_methods()

    @staticmethod
    def show_about():
        message = 'pRuby - pressure estimation based on ruby fluorescence ' \
                  'spectrum by Daniel Tcho\u0144\n\n'\
                  'For details and help, visit pRuby page' \
                  '(https://github.com/Baharis/pRuby).'
        tkmb.showinfo(title='About pRuby', message=message)

    def recalculate_p(self, *_):
        # calculate the shift for current calculator
        self.calculator.shift = 0.0
        self.calculator.t = self.t_ref
        self.calculator.p = 0.0
        self.calculator.calculate_r1()
        self.calculator.shift = self.r1_ref - self.calculator.r1_x
        # calculate the pressure for current data
        self.calculator.r1_x = uc.ufloat_fromstr(self.r1.get())
        self.calculator.t = uc.ufloat_fromstr(self.t.get())
        self.calculator.calculate_pressure()
        self.p1.set(value=self.calculator.p)
        if self.autodraw.get() is True:
            self.data_draw()

    def recalculate_r(self, *_):
        self.calculator.p = uc.ufloat_fromstr(self.p1.get())
        self.calculator.t = uc.ufloat_fromstr(self.t.get())
        self.calculator.calculate_r1()
        self.r1.set(self.calculator.r1_x)

    def open_file_dialogue(self):
        path = tkfd.askopenfilename(
            title='Open ruby spectrum file...',
            filetypes=(("Text files", "*.txt"), ("All files", "*.*")),
            initialdir=os.getcwd())
        directory, filename = os.path.split(path)
        os.chdir(directory)
        self.change_file(filename)

    def change_file(self, filename):
        self.file_name.set(filename)
        if filename is '':
            return
        self.update_file_list()
        try:
            self.calculator.read_and_fit(filename)
        except RuntimeError:
            tkmb.showerror(message='Fitting failed!'
                                   'Consider changing fiting strategy.')
            return
        except FileNotFoundError:
            tkmb.showerror(message='The file does not exist')
            return
        except (TypeError, ValueError, UnicodeDecodeError):
            tkmb.showerror(message='Cannot interpret file content')
            return
        except PermissionError:
            tkmb.showerror(message='No permissions to read this file')
            return
        self.r1.set(value=self.calculator.r1_x)
        self.recalculate_p()

    def change_file_to_next(self):
        return self.change_file(self.file_next)

    def change_file_to_previous(self):
        return self.change_file(self.file_previous)

    def save_reference(self):
        self.r1_ref = uc.ufloat_fromstr(self.r1.get())
        self.t_ref = uc.ufloat_fromstr(self.t.get())
        self.p1_ref = uc.ufloat_fromstr(self.p1.get())
        self.recalculate_p()

    def load_reference(self):
        self.r1.set(self.r1_ref)
        self.t.set(self.t_ref)
        self.recalculate_p()

    def file_fromentry(self, *_):
        filename = self.file_entry.get()
        if os.path.isfile(os.path.join(os.getcwd(), filename)):
            self.change_file(filename)
        elif os.path.isfile(filename):
            self.change_file(filename)

    def update_file_list(self):
        files = natsorted([f for f in os.listdir(os.getcwd())
                           if not os.path.isdir(f)])
        index = files.index(self.file_entry.get())
        self.file_next = files[(index + 1) % len(files)]
        self.file_previous = files[(len(files) + index - 1) % len(files)]

    def set_methods(self):
        self.calculator.set_routine(
            reading=self.reading_routine.get(),
            backfitting=self.backfitting_routine.get(),
            peakfitting=self.peakfitting_routine.get(),
            correcting=self.correcting_routine.get(),
            translating=self.translating_routine.get(),
            drawing=self.drawing_routine.get())
        self.recalculate_p()

    def data_draw(self):
        self.calculator.draw()


# MAIN PROGRAM
if __name__ == '__main__':
    root = tk.Tk()
    app_wd = os.getcwd()
    Application(root).pack(side='top', fill='both', expand=True)
    root.title('pRuby')
    root.attributes("-topmost", True)
    icon = tk.PhotoImage(file=app_wd + '/resources/icon.gif')
    root.tk.call('wm', 'iconphoto', root._w, icon)
    # TODO for some bizzare reason the icon died while moving drawing to routine
    # TODO also looks like text fields are suddenly empty and can't be filled ?!
    # TODO tommorow. tired.
    root.resizable(False, False)
    root.mainloop()
