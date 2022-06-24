import numpy as np


def polynomial(*coefficients):
    return lambda x: sum([c * x ** i for i, c in enumerate(coefficients)])


def gaussian(a, mu, si):
    return lambda x: a * np.exp(-(x - mu) ** 2 / (2. * si ** 2))


def lorentzian(a, mu, ga):
    return lambda x: (a * ga ** 2) / ((x - mu) ** 2 + ga ** 2)


def pseudovoigt(a, mu, w, et):
    si = w / (np.sqrt(8 * np.log(2)))
    ga = w / 2
    return lambda x: et * gaussian(a, mu, si)(x) + \
                     (1 - et) * lorentzian(a, mu, ga)(x)
