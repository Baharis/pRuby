import tkinter as tk

from pruby.tkinter.variables import UfloatVar

TK_PADDING = 1
TK_WIDTH = 12


class Entry(tk.Entry):
    def __init__(self, master, var, cmd):
        kwargs = {'width': 16, 'textvariable': var}
        if type(var) is UfloatVar:
            kwargs['justify'] = 'right'
        else:
            kwargs['justify'] = 'left'
        super().__init__(master, **kwargs)
        try:
            self.bind('<Return>', cmd)
        except KeyError:
            pass

    def grid(self, **kwargs):
        kwargs['padx'] = TK_PADDING
        kwargs['pady'] = TK_PADDING
        super().grid(**kwargs)


class Label(tk.Label):
    def __init__(self, master, text):
        super().__init__(master, text=text)

    def grid(self, **kwargs):
        kwargs['padx'] = TK_PADDING
        kwargs['pady'] = TK_PADDING
        super().grid(**kwargs)


class Button(tk.Button):
    def __init__(self, master, text, cmd):
        super().__init__(master, text=text, command=cmd)


class StatusBar(tk.Label):
    def __init__(self, master, **kwargs):
        kwargs['bd'] = 1
        kwargs['relief'] = tk.SUNKEN
        kwargs['width'] = 20
        super().__init__(master, **kwargs)
        self.config(text='Ready...', anchor='w')

    def display(self, message):
        self.config(text=message)

    def grid(self, **kwargs):
        kwargs['padx'] = 0
        kwargs['pady'] = 1
        kwargs['sticky'] = 'NSWE'
        super().grid(**kwargs)
