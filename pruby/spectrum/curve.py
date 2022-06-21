import numpy as np


class Curve:
    def __init__(self, func=lambda x: 0, args=tuple()):
        self.func = func
        self.args = args
        self.uncs = tuple(np.zeros_like(args))

    def __call__(self, *args):
        x, args = self._interpret_call(args)
        try:
            return np.array([self.func(x_val, *args) for x_val in x])
        except TypeError:
            return self.func(x, *args)

    def _interpret_call(self, args):
        call_x, call_args = args[0], args[1:]
        args = list(self.args)
        for i, a in enumerate(call_args):
            try:
                args[i] = a
            except IndexError:
                raise ValueError('Too many argument provided to the function')
        return call_x, args
