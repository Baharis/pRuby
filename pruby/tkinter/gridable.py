import tkinter as tk
import uncertainties as uc

PADX = 1
PADY = 0
WIDTH = 24


class FilenameEntry(tk.Frame):
    def __init__(self, parent, left_cmd, entry_cmd, right_cmd):
        tk.Frame.__init__(self, parent)
        self.value = tk.StringVar(value='')
        prev_button = tk.Button(self, text='\u25c0', command=left_cmd)
        prev_button.grid(row=0, column=0, padx=PADX, pady=PADY)
        self.entry = tk.Entry(self, width=int(0.7 * WIDTH), justify='right')
        self.set('')
        self.entry.grid(row=0, column=1, columnspan=2, padx=PADX, pady=PADY)
        self.entry.bind('<Return>', entry_cmd)
        next_button = tk.Button(self, text='\u25b6', command=right_cmd)
        next_button.grid(row=0, column=3, padx=PADX, pady=PADY)

    def get(self):
        return self.entry.get()

    def set(self, value):
        self.entry.delete(0, tk.END)
        self.entry.insert(0, value)


class UfloatEntry(tk.Frame):
    def __init__(self, parent, left_text, entry_text, right_text, cmd):
        self.parent = parent
        tk.Frame.__init__(self, parent)
        left_label = tk.Label(self, text=left_text)
        left_label.config(width=int(0.15*WIDTH), justify=tk.CENTER)
        left_label.grid(row=1, column=0, padx=PADX, pady=PADY)
        self.entry = tk.Entry(self, width=int(0.7*WIDTH), justify='right')
        self.set(entry_text)
        self.entry.grid(row=1, column=1, columnspan=2, padx=PADX, pady=PADY)
        self.entry.bind('<Return>', cmd)
        right_label = tk.Label(self, text=right_text)
        right_label.config(width=int(0.15*WIDTH), justify=tk.CENTER)
        right_label.grid(row=1, column=3, padx=PADX, pady=PADY)

    def get(self):
        try:
            uc.ufloat_fromstr(self.entry.get())
            return uc.ufloat_fromstr(self.entry.get())
        except ValueError as error:
            self.parent.display('Incorrect entry input format!')
            raise ValueError(error)

    def set(self, value):
        self.entry.delete(0, tk.END)
        self.entry.insert(0, '{0:.2uS}'.format(value))


class StatusBar(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.bar = tk.Label(self, bd=1, relief=tk.SUNKEN, width=WIDTH+2*PADX)
        self.bar.config(anchor='w')
        self.bar.pack()

    def display(self, message):
        self.bar.config(text=message)

    def grid(self, **kwargs):
        kwargs['padx'] = 0
        kwargs['pady'] = 1
        kwargs['sticky'] = 'NSWE'
        super().grid(**kwargs)
