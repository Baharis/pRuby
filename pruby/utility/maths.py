import numpy as np


def polynomial(*coefficients):
    return lambda x: sum([c * x ** i for i, c in enumerate(coefficients)])


def gaussian(a, mu, si):
    return lambda x: a * np.exp(-(x - mu) ** 2 / (2. * si ** 2))


def lorentzian(a, mu, ga):
    return lambda x: (a * ga ** 2) / ((x - mu) ** 2 + ga ** 2)







