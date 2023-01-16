import os
import tkinter as tk
from natsort import natsorted
from pruby.constants import R1_0, T_0, P_0
from pruby.calculator import PressureCalculator
from pruby.gui.gridable import FilenameEntry, UfloatEntry, StatusBar
from pruby.gui.popups import open_file_dialogue, show_about
from pruby.strategies import \
    ReadingStrategies, \
    BackfittingStrategies, \
    PeakfittingStrategies, \
    CorrectingStrategies, \
    TranslatingStrategies, \
    DrawingStrategies


class Application(tk.Frame):
    def __init__(self, root, *args, **kwargs):
        tk.Frame.__init__(self, root, *args, **kwargs)
        self.root = root
        os.chdir(os.path.expanduser('~/'))

        # SETTING CONSTANTS
        self.r1_ref = R1_0
        self.t_ref = T_0
        self.p_ref = P_0
        self.autodraw = tk.BooleanVar(value=False)
        self.calc = PressureCalculator()
        self.ref = PressureCalculator()

        # method string variables
        self.reading_strategy = tk.StringVar(
            value=self.calc.engine.reader.name)
        self.backfitting_strategy = tk.StringVar(
            value=self.calc.engine.backfitter.name)
        self.peakfitting_strategy = tk.StringVar(
            value=self.calc.engine.peakfitter.name)
        self.correcting_strategy = tk.StringVar(
            value=self.calc.engine.corrector.name)
        self.translating_strategy = tk.StringVar(
            value=self.calc.engine.translator.name)
        self.drawing_strategy = tk.StringVar(
            value=self.calc.engine.drawer.name)

        # BUILDING TOP MENU
        self.menu = tk.Menu(self)
        self.root.config(menu=self.menu)

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
        self.menu.add_cascade(label="Methods", menu=self.menu_options)

        def make_options_submenu(strategy_list, str_var, label, command):
            self.menu_options.add_command(label=label, state='disabled')
            for strategy in strategy_list:
                self.menu_options.add_radiobutton(label=str(strategy()),
                value=strategy.name, variable=str_var, command=command)
            self.menu_options.add_separator()  # separators if necessary

        make_options_submenu(
            strategy_list=ReadingStrategies.registry.values(),
            str_var=self.reading_strategy,
            label='Reading',
            command=self.set_reading_method
        )
        make_options_submenu(
            strategy_list=BackfittingStrategies.registry.values(),
            str_var=self.backfitting_strategy,
            label='Background fitting',
            command=self.set_backfitting_method
        )
        make_options_submenu(
            strategy_list=PeakfittingStrategies.registry.values(),
            str_var=self.peakfitting_strategy,
            label='Spectrum fitting',
            command=self.set_peakfitting_method
        )
        make_options_submenu(
            strategy_list=CorrectingStrategies.registry.values(),
            str_var=self.correcting_strategy,
            label='Temperature correction',
            command=self.set_correcting_method
        )
        make_options_submenu(
            strategy_list=TranslatingStrategies.registry.values(),
            str_var=self.translating_strategy,
            label='Pressure determination',
            command=self.set_translating_method
        )
        make_options_submenu(
            strategy_list=DrawingStrategies.registry.values(),
            str_var=self.drawing_strategy,
            label='Drawing style',
            command=self.set_drawing_method
        )
        self.menu.add_command(label='?', command=show_about)

        # BUILDING ENTRY AREA
        self.file = FilenameEntry(self, self.file_to_previous,
                                  self.file_from_entry, self.file_to_next)
        self.file.grid(row=0, column=0, columnspan=4)
        self.r1 = UfloatEntry(self, label='R1', entry=self.r1_ref,
                              unit='nm', cmd=self.recalculate_p)
        self.r1.grid(row=1, column=0, columnspan=4)
        self.t = UfloatEntry(self, label='T', entry=self.t_ref, offset=273.15,
                             unit='\u00B0C', cmd=self.recalculate_p)
        self.t.grid(row=2, column=0, columnspan=4)
        self.p = UfloatEntry(self, label='p', entry=self.t_ref,
                             unit='GPa', cmd=self.recalculate_r)
        self.p.grid(row=3, column=0, columnspan=4)

        # BUILDING STATUS BAR
        self.status_bar = StatusBar(self)
        self.status_bar.grid(row=4, column=0, columnspan=4)

        # FINAL SETUP
        self.set_all_methods()
        self.save_reference()  # ran to update correlation b/ temp corr and r1!
        self.display('Ready...')

    def display(self, message):
        self.status_bar.display(message)

    def recalculate_p(self, *_):
        # calculate the pressure for current data
        self.calc.r1 = self.r1.get()
        self.calc.t = self.t.get()
        self.calc.calculate_p_from_r1()
        self.p.set(value=self.calc.p)
        if self.autodraw.get() is True:
            self.data_draw()
        self.display('Calculated p from R1 and T.')

    def recalculate_r(self, *_):
        self.calc.p = self.p.get()
        self.calc.t = self.t.get()
        self.calc.calculate_r1_from_p()
        self.r1.set(self.calc.r1)
        self.display('Calculated R1 from p and T.')

    def open_file_dialogue(self):
        path = open_file_dialogue()
        if not path:
            self.display('No file have been loaded.')
            return
        new_directory, new_filename = os.path.split(path)
        os.chdir(new_directory)
        self.change_file(new_filename)

    def change_file(self, filename):
        self.file.set(filename)
        if filename == '':
            return
        try:
            self.calc.read(filename)
        except RuntimeError:
            self.display('Fitting spectrum failed!')
            return
        except FileNotFoundError:
            self.display('File does not exist!')
            return
        except (TypeError, ValueError, UnicodeDecodeError):
            self.display('File cannot be intepreted!')
            return
        except PermissionError:
            self.display('No permissions to read this file!')
            return
        self.r1.set(value=self.calc.r1)
        self.recalculate_p()

    def file_to_next(self):
        return self.change_file(self.get_filename(self.file.get(), shift=+1))

    def file_to_previous(self):
        return self.change_file(self.get_filename(self.file.get(), shift=-1))

    def file_from_entry(self, *_):
        filename = self.file.get()
        if os.path.isfile(os.path.join(os.getcwd(), filename)):
            self.change_file(filename)
        elif os.path.isfile(filename):
            self.change_file(filename)

    def save_reference(self):
        self.calc.r1 = self.r1_ref = self.r1.get()
        self.calc.t = self.t_ref = self.t.get()
        self.calc.p = self.p_ref = self.p.get()
        self.calc.set_current_as_reference()
        self.recalculate_p()
        self.display('R1 & T saved as reference for p=0.')

    def load_reference(self):
        self.r1.set(self.r1_ref)
        self.t.set(self.t_ref)
        self.recalculate_p()
        self.display('R1 & T loaded from reference.')

    @staticmethod
    def get_filename(filename, shift=0):
        files = [f for f in os.listdir(os.getcwd()) if not os.path.isdir(f)]
        files = natsorted(files)
        try:
            index = files.index(filename)
        except ValueError:
            index, shift = 0, 0
        return files[(len(files) + index + shift) % len(files)]

    def set_all_methods(self):
        self.calc.engine.set_strategy(
            reading=self.reading_strategy.get(),
            backfitting=self.backfitting_strategy.get(),
            peakfitting=self.peakfitting_strategy.get(),
            correcting=self.correcting_strategy.get(),
            translating=self.translating_strategy.get(),
            drawing=self.drawing_strategy.get())
        self._reevaluate()

    def set_reading_method(self):
        self.calc.engine.set_strategy(reading=self.reading_strategy.get())
        self._reevaluate()

    def set_backfitting_method(self):
        self.calc.engine.set_strategy(backfitting=self.backfitting_strategy.get())
        self._reevaluate()

    def set_peakfitting_method(self):
        self.calc.engine.set_strategy(peakfitting=self.peakfitting_strategy.get())
        self._reevaluate()

    def set_correcting_method(self):
        self.calc.engine.set_strategy(correcting=self.correcting_strategy.get())
        self._reevaluate()

    def set_translating_method(self):
        self.calc.engine.set_strategy(translating=self.translating_strategy.get())
        self._reevaluate()

    def set_drawing_method(self):
        self.calc.engine.set_strategy(drawing=self.drawing_strategy.get())
        self._reevaluate()

    def _reevaluate(self):
        self.calc.calculate_offset_from_reference()
        try:
            self.calc.read()
            self.r1.set(value=self.calc.r1)
        except OSError:
            pass
        self.recalculate_p()

    def data_draw(self):
        try:
            self.calc.draw()
            self.display('Drawn currently loaded data.')
        except AttributeError:
            self.display('No loaded spectrum to draw!')
