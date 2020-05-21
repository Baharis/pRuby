import tkinter as tk


class BooleanVar(tk.BooleanVar):
    def __init__(self, value):
        super().__init__(value=value)


class StringVar(tk.StringVar):
    def __init__(self, value):
        super().__init__(value=value)


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