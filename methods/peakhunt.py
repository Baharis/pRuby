import numpy as np
from collections import OrderedDict
from scipy.signal import find_peaks_cwt
from scipy.optimize import curve_fit, minimize_scalar

# PEAKHUNT RANGE
peakhunt_range = 0.40


# HELPER FUNCTIONS
def default():
    return gauss_fit


def methods():
    dict_of_methods = OrderedDict()
    dict_of_methods['gauss_fit'] = {'function': gauss_fit,
                                    'name': 'Gauss Fit'}
    dict_of_methods['camel_fit'] = {'function': camel_fit,
                                    'name': 'Camel Fit'}
    dict_of_methods['dromaderies_fit'] = {'function': dromedaries_fit,
                                          'name': 'Dromaderies Fit'}
    dict_of_methods['pseudovoigt_fit'] = {'function': pseudovoigt_fit,
                                           'name': 'Pseudo-Voigt Fit'}
    return dict_of_methods


def make_dependent_on_x(func):
    return lambda x, *args: func(*args)(x)


def calculate_error(dots, func):
    error_sum = 0
    for dot in dots:
        error = np.power(dot[1] - func(dot[0]), 2)
        error_sum += error
    error_sum /= len(dots)
    print(error_sum)


# DOTS MENAGEMENT FUNCTIONS
def trim_to_range(dots, x_beg, x_end):
    indices_to_delete = \
        [index for index, x in enumerate(dots[:, 0]) if x < x_beg or x > x_end]
    return np.delete(dots, indices_to_delete, axis=0)


# BASIC FUNCTIONS
def linear(a, b):
    """	Input:  a, b - coeffitients for linear background function a * x + b
        Return:	linear function of an 'x' parameter      (float)
        Descr.: Produce linear function with fixed parameters"""
    return lambda x: a * x + b


def camel(a1, mu1, si1, a2, mu2, si2, a12, mu12, si12):
    """	Input:  a2, mu2, si2 - r2 gaussian coeffitients
                a1, mu1, si1 - r1 gaussian coeffitients
                a12, mu12, si12 - background gaussian coeffitients (float)s
        Return:	camel function of an 'x' parameter      (float)
        Descr.: Produce G+g+G(x)-type function with fixed parameters"""
    return lambda x: gauss(a2, mu2, si2)(x) + gauss(a1, mu1, si1)(x)\
                     + gauss(a12, mu12, si12)(x)


def dromedaries(mu1, a1, si1, b1, ga1, mu2, a2, si2, b2, ga2):
    """	Input:      For each of the maxima: suffix 1 for r1, 2 for r2
               mu - center of lorentz and gaussian functions
                a - height of the signal lorentz function
               si - standard deviation of the signal gaussian function
                b - height of the signal lorentz function
               ga - probable error of the signal lorentz function (floats)
        Return:	dromedaries function of an 'x' parameter      (float)
        Descr.: Produce Gg+Gg(x)-type function with fixed parameters"""
    return lambda x: gauss(a2, mu2, si2)(x) + lorentz(b2, mu2, ga2)(x) + \
                     gauss(a1, mu1, si1)(x) + lorentz(b1, mu1, ga1)(x)


def gauss(a, mu, si):
    """	Input:  a, mu, si - gaussian coeffitients               (float)
        Return:	gauss function of an 'x' parameter              (float)
        Descr.: Produce G(x)-type function with fixed parameters"""
    return lambda x: a * np.exp(-(x - mu) ** 2 / (2. * si ** 2))


def lorentz(a, mu, ga):
    """	Input: x - value and a=I, mu=x_0, ga - lorentz f. coeffitients  (float)
        Return:	value of function with desired parameters in x (float)
        Descr.: Calculate L-type function for given x and parameters"""
    return lambda x: (a * ga ** 2) / ((x - mu) ** 2 + ga ** 2)


def pseudovoigt(mu1, a1, w1, et1, mu2, a2, w2, et2):
    """	Input:      For each of the maxima: suffix 1 for r1, 2 for r2
               mu - center of both pseudo-voigt functions
                a - height of the total signal of both functions
                w - pseudo-voigt half-with of the both functions
               et - percentege of gaussian component in both pseudo-voigts
        Return:	pseudo-voigt function of an 'x' parameter      (float)
        Descr.: Produce GL+GL(x)-type function with fixed parameters"""
    si2 = w2/(np.sqrt(8*np.log(2)))
    si1 = w1/(np.sqrt(8*np.log(2)))
    ga2 = w2 / 2
    ga1 = w1 / 2
    return lambda x: et1 * gauss(a2, mu2, si2)(x) + \
                     (1 - et1) * lorentz(a2, mu2, ga2)(x) + \
                     et2 * gauss(a1, mu1, si1)(x) + \
                     (1 - et2) * lorentz(a1, mu1, ga1)(x)


def peak_search(dots):
    """	Input:	dots - ruby spectrum data (n x 2 ndarray)
        Return:	list of data biggest peaks (n x 2 ndarray)
        Descr.: Find and sort biggest peaks in dots data"""
    peak_indexes = find_peaks_cwt(vector=dots[:, 1], widths=[10])
    peaks = np.array([dots[index, :] for index in peak_indexes])
    peaks = peaks[peaks[:, 1].argsort()[::-1]]
    return peaks


# BACKGROUND ESTIMATION
def estimate_background(dots):
    # PREPARE 20 EDGE DOTS TO ESTIMATE BACKGROUND
    left_edge_dots = np.array(dots[:10, :], dtype=(float, float))
    right_edge_dots = np.array(dots[-10:, :], dtype=(float, float))
    edge_dots = np.concatenate((left_edge_dots, right_edge_dots))

    # ESTIMATE INITIAL BACKGROUND PARAMETERS
    a = (dots[-1, 1] - dots[0, 1]) / (dots[-1, 0] - dots[0, 0])
    b = dots[0, 1] - a * dots[0, 0]
    guess = (a, b)

    # FIT LINEAR BACKGROUND TO THE EDGE DOTS
    popt, pcov = curve_fit(make_dependent_on_x(linear), xdata=edge_dots[:, 0],
                           ydata=edge_dots[:, 1], p0=guess)

    # PREPARE DOTS CORRECTED FOR BACKGROUND
    background = linear(popt[0], popt[1])
    corrected_dots = []
    for x, y in zip(dots[:, 0], dots[:, 1]):
        corrected_dots.append([x, y - background(x)])
    corrected_dots = np.array(corrected_dots, dtype=(float, float))

    # RETURN DATA
    return {'corrected_dots': corrected_dots,
            'background': background}


# FIT FUNCTIONS
def camel_fit(dots):
    """	Input:	dots - ruby spectrum data (n x 2 ndarray)
        Return:	dict with r1, r2 and fit description
        Descr.: Fit G+g+G-type "camel" function to dots"""

    # LOAD PEAKS AND ESTIMATE BACKGROUND
    estimated_background = estimate_background(dots)
    background = estimated_background['background']
    dots = estimated_background['corrected_dots']
    peaks = peak_search(dots)[:2, :]

    # ESTIMATE INITIAL GAUSSIAN PARAMETERS
    si1, si2, si12 = 0.35, 0.35, 1.0
    mu1 = peaks[0, 0]
    a1 = peaks[0, 1]
    mu2 = peaks[1, 0]
    a2 = peaks[1, 1]
    a12 = 0.1 * (a1 + a2)
    mu12 = 0.5 * (mu1 + mu2)
    guess = (a1, mu1, si1, a2, mu2, si2, a12, mu12, si12)

    # TRIM DATA AND FIT CAMEL CURVE
    x_beg = peaks[1, 0] - 2 * peakhunt_range
    x_end = peaks[0, 0] + 2 * peakhunt_range
    dots = trim_to_range(dots, x_beg, x_end)
    dots_sigma = peaks[0, 1] * np.power(dots[:, 1], -1)
    popt, pcov = curve_fit(make_dependent_on_x(camel), xdata=dots[:, 0],
                           ydata=dots[:, 1], p0=guess, sigma=dots_sigma)
    sigma = np.sqrt(np.diag(pcov))

    # FIND ACTUAL MAXIMA AND RETURN DATA
    dx = peakhunt_range
    r1_val = minimize_scalar(lambda x: -camel(*popt)(x), method='Bounded',
                             bounds=(popt[1]-dx, popt[1]+dx)).x
    r2_val = minimize_scalar(lambda x: -camel(*popt)(x), method='Bounded',
                             bounds=(popt[4]-dx, popt[4]+dx)).x

    calculate_error(dots, lambda x: camel(*popt)(x) + background(x))

    return {'r1_val': r1_val,
            'r1_unc': sigma[1],
            'r1_int': camel(*popt)(r1_val) + background(r1_val),
            'r2_val': r2_val,
            'r2_unc': sigma[4],
            'r2_int': camel(*popt)(r2_val) + background(r2_val),
            'fit_function': [lambda x: camel(*popt)(x) + background(x)],
            'fit_range': [(x_beg, x_end)]}


def pseudovoigt_fit(dots):
    """	Input:	dots - ruby spectrum data (n x 2 ndarray)
        Return:	dict with r1, r2 and fit description
        Descr.: Fit GL+GL-type "dromedaries" function to dots"""

    # LOAD PEAKS AND ESTIMATE BACKGROUND
    estimated_background = estimate_background(dots)
    background = estimated_background['background']
    dots = estimated_background['corrected_dots']
    peaks = peak_search(dots)[:2, :]

    # ESTIMATE INITIAL GAUSSIAN & LORENTZIAN PARAMETERS
    mu1, mu2 = peaks[0, 0], peaks[1, 0]
    a1, a2 = peaks[0, 1], peaks[1, 1]
    w1, w2 = 0.75, 0.75
    et1, et2 = 0.5, 0.25
    guess = (mu1, a1, w1, et1, mu2, a2, w2, et2)

    # TRIM DATA AND FIT THE DROMEDARIES CURVE
    x_beg = peaks[1, 0] - 3 * peakhunt_range
    x_end = peaks[0, 0] + 3 * peakhunt_range
    dots = trim_to_range(dots, x_beg, x_end)
    popt, pcov = curve_fit(make_dependent_on_x(pseudovoigt), xdata=dots[:, 0],
                           ydata=dots[:, 1], p0=guess)
    sigma = np.sqrt(np.diag(pcov))

    calculate_error(dots, lambda x: pseudovoigt(*popt)(x) + background(x))

    # RETURN DATA
    return {'r1_val': popt[0],
            'r1_unc': sigma[0],
            'r1_int': pseudovoigt(*popt)(popt[0]) + background(popt[0]),
            'r2_val': popt[4],
            'r2_unc': sigma[4],
            'r2_int': pseudovoigt(*popt)(popt[4]) + background(popt[4]),
            'fit_function':
                [lambda x: pseudovoigt(*popt)(x) + background(x)],
            'fit_range': [(x_beg, x_end)]}


def dromedaries_fit(dots):
    """	Input:	dots - ruby spectrum data (n x 2 ndarray)
        Return:	dict with r1, r2 and fit description
        Descr.: Fit Lg+Lg-type "dromedaries" function to dots"""

    # LOAD PEAKS AND ESTIMATE BACKGROUND
    estimated_background = estimate_background(dots)
    background = estimated_background['background']
    dots = estimated_background['corrected_dots']
    peaks = peak_search(dots)[:2, :]

    # ESTIMATE INITIAL GAUSSIAN & LORENTZIAN PARAMETERS
    mu1, mu2 = peaks[0, 0], peaks[1, 0]
    a1, a2 = 0.75 * peaks[0, 1], 0.75 * peaks[1, 1]
    si1, si2 = 0.35, 0.35
    b1, b2 = 0.20 * peaks[0, 1], 0.20 * peaks[1, 1]
    ga1, ga2 = 0.7, 0.7
    guess = (mu1, a1, si1, b1, ga1, mu2, a2, si2, b2, ga2)

    # TRIM DATA AND FIT THE DROMEDARIES CURVE
    x_beg = peaks[1, 0] - 3 * peakhunt_range
    x_end = peaks[0, 0] + 3 * peakhunt_range
    dots = trim_to_range(dots, x_beg, x_end)
    dots_sigma = peaks[0, 1] * np.power(dots[:, 1], -1)
    popt, pcov = curve_fit(make_dependent_on_x(dromedaries), xdata=dots[:, 0],
                           ydata=dots[:, 1], p0=guess)
    sigma = np.sqrt(np.diag(pcov))

    calculate_error(dots, lambda x: dromedaries(*popt)(x) + background(x))

    # RETURN DATA
    return {'r1_val': popt[0],
            'r1_unc': sigma[0],
            'r1_int': dromedaries(*popt)(popt[0]) + background(popt[0]),
            'r2_val': popt[5],
            'r2_unc': sigma[5],
            'r2_int': dromedaries(*popt)(popt[5]) + background(popt[5]),
            'fit_function':
                [lambda x: dromedaries(*popt)(x) + background(x)],
            'fit_range': [(x_beg, x_end)]}


def gauss_fit(dots):
    """	Input:	dots - ruby spectrum data (n x 2 ndarray)
        Return:	dict with r1, r2 and fit description
        Descr.: Fit G&G-type "two gauss" function to dots"""

    # LOAD PEAKS AND ESTIMATE BACKGROUND
    estimated_background = estimate_background(dots)
    background = estimated_background['background']
    dots = estimated_background['corrected_dots']
    peaks = peak_search(dots)[:2, :]

    # ESTIMATE INITIAL GAUSSIAN PARAMETERS
    si1, si2 = 0.35, 0.35
    mu1, mu2 = peaks[0, 0], peaks[1, 0]
    a1, a2 = peaks[0, 1], peaks[1, 1]
    guess1, guess2 = (a1, mu1, si1), (a2, mu2, si2)

    # CUT DATA TO FITTED SURROUNDING
    x_beg1 = peaks[0, 0] - peakhunt_range
    x_end1 = peaks[0, 0] + peakhunt_range
    x_beg2 = peaks[1, 0] - peakhunt_range
    x_end2 = peaks[1, 0] + peakhunt_range
    dots1 = trim_to_range(dots, x_beg1, x_end1)
    dots2 = trim_to_range(dots, x_beg2, x_end2)

    # FIT THE GAUSS CURVES AND RETURN DATA
    popt1, pcov1 = curve_fit(make_dependent_on_x(gauss), xdata=dots1[:, 0],
                             ydata=dots1[:, 1], p0=guess1)
    sigma1 = np.sqrt(np.diag(pcov1))
    popt2, pcov2 = curve_fit(make_dependent_on_x(gauss), xdata=dots2[:, 0],
                             ydata=dots2[:, 1], p0=guess2)
    sigma2 = np.sqrt(np.diag(pcov2))

    calculate_error(dots1, lambda x: gauss(*popt1)(x) + background(x))
    calculate_error(dots2, lambda x: gauss(*popt2)(x) + background(x))

    return {'r1_val': popt1[1],
            'r1_unc': sigma1[1],
            'r1_int': popt1[0] + background(popt1[1]),
            'r2_val': popt2[1],
            'r2_unc': sigma2[1],
            'r2_int': popt2[0] + background(popt2[1]),
            'fit_function':
                [lambda x: gauss(*popt1)(x) + background(x),
                 lambda x: gauss(*popt2)(x) + background(x)],
            'fit_range': [(x_beg1, x_end1), (x_beg2, x_end2)]}


if __name__ == '__main__':
    pass
