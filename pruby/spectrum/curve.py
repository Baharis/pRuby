from typing import Callable, Iterable
import numpy as np


class Curve:
    def __init__(self, func: Callable = lambda x: 0, args=tuple()):
        self.func: Callable = func
        self.args: Iterable = args
        self.uncs: tuple = tuple(np.zeros_like(args))

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
            except IndexError as e:
                raise IndexError('Too many arguments provided to the function')
        return call_x, args
