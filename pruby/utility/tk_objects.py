import tkinter as tk

TK_PADDING = 1
TK_WIDTH = 12


class Entry(tk.Entry):
    def __init__(self, master, **kwargs):
        kwargs['width'] = 12
        command = kwargs['command']
        del(kwargs['command'])
        if type(kwargs['textvariable']) is UfloatVar:
            kwargs['justify'] = 'right'
        else:
            kwargs['justify'] = 'left'
        super().__init__(master, **kwargs)
        try:
            self.bind('<Return>', command)
        except KeyError:
            pass

    def grid(self, **kwargs):
        kwargs['padx'] = TK_PADDING
        kwargs['pady'] = TK_PADDING
        super().grid(**kwargs)


class Label(tk.Label):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

    def grid(self, **kwargs):
        kwargs['padx'] = TK_PADDING
        kwargs['pady'] = TK_PADDING
        super().grid(**kwargs)


class UfloatVar(tk.StringVar):
    def __init__(self, **kwargs):
        try:
            kwargs['value'] = '{0:.2uS}'.format(kwargs['value'])
        except ValueError:
            return
        super().__init__(**kwargs)

    def set(self, value):
        try:
            value = '{0:.2uS}'.format(value)
        except ValueError:
            return
        super().set(value)

