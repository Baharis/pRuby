import numpy as np
from scipy.signal import find_peaks_cwt
from scipy.optimize import curve_fit, minimize_scalar

# PEAKHUNT RANGE
peakhunt_range = 0.2


# HELPER FUNCTIONS
def default():
    return labspec_fit


def methods():
    return {'gauss_fit':       {'function': gauss_fit,
                                'name':     'Gauss Fit',
                                'desc':     'G&G'},
            'labspec_fit':     {'function': labspec_fit,
                                'name':     'Labspec Fit',
                                'desc':     'GL&GL'},
            'bactrian_fit':    {'function': bactrian_fit,
                                'name':     'Bactrian Fit',
                                'desc':     'G+G'},
            'camel_fit':       {'function': camel_fit,
                                'name':     'Camel Fit',
                                'desc':     'G+g+G'},
            'dromedaries_fit': {'function': dromedaries_fit,
                                'name':     'Dromedaries Fit',
                                'desc':     'GLg+GLg'}
            }


# DOTS MENAGEMENT FUNCTIONS
def trim_to_range(dots, x_beg, x_end):
    indices_to_delete = \
        [index for index, x in enumerate(dots[:, 0]) if x < x_beg or x > x_end]
    return np.delete(dots, indices_to_delete, axis=0)


# BASIC FUNCTIONS
def linear(x, a, b):
    """	Input:  x - given point for which background is calculated (floats)
                a, b - coeffitients for linear background function a * x + b
        Return:	value of function with desired parameters in x (float)
        Descr.: Calculate linear function for given x and parameters"""
    return a * x + b


def linear_fixed(a, b):
    """	Input:  a, b - coeffitients for linear background function a * x + b
        Return:	linear function of an 'x' parameter      (float)
        Descr.: Produce linear function with fixed parameters"""
    def linear_baby(x):
        return linear(x, a, b)
    return linear_baby


def bactrian(x, a1, mu1, si1, a2, mu2, si2):
    """	Input:  x - given point for which camel is calculated
                a2, mu2, si2 - r2 gaussian coeffitients
                a1, mu1, si1 - r1 gaussian coeffitients (float)s
        Return:	value of function with desired parameters in x (float)
        Descr.: Calculate G+G-type function for given x and parameters"""
    return gauss(x, a2, mu2, si2) + gauss(x, a1, mu1, si1)


def bactrian_fixed(a1, mu1, si1, a2, mu2, si2):
    """	Input:  a2, mu2, si2 - r2 gaussian coeffitients
                a1, mu1, si1 - r1 gaussian coeffitients (float)s
        Return:	bactrian function of an 'x' parameter      (float)
        Descr.: Produce G+G(x)-type function with fixed parameters"""
    def bactrian_baby(x):
        return bactrian(x, a1, mu1, si1, a2, mu2, si2)
    return bactrian_baby


def camel(x, a1, mu1, si1, a2, mu2, si2, a12, mu12, si12):
    """	Input:  x - given point for which camel is calculated
                a2, mu2, si2 - r2 gaussian coeffitients
                a1, mu1, si1 - r1 gaussian coeffitients
                a12, mu12, si12 - background gaussian coeffitients (float)s
        Return:	value of function with desired parameters in x (float)
        Descr.: Calculate G+g+G-type function for given x and parameters"""
    return gauss(x, a2, mu2, si2) + gauss(x, a1, mu1, si1)\
           + gauss(x, a12, mu12, si12)


def camel_fixed(a1, mu1, si1, a2, mu2, si2, a12, mu12, si12):
    """	Input:  a2, mu2, si2 - r2 gaussian coeffitients
                a1, mu1, si1 - r1 gaussian coeffitients
                a12, mu12, si12 - background gaussian coeffitients (float)s
        Return:	camel function of an 'x' parameter      (float)
        Descr.: Produce G+g+G(x)-type function with fixed parameters"""
    def camel_baby(x):
        return camel(x, a1, mu1, si1, a2, mu2, si2, a12, mu12, si12)
    return camel_baby


def dromedaries(x, mu1, a1, si1, b1, ta1, mu2, a2, si2, b2, ta2):
    """	Input:  x - given point for which dromedaries is calculated
                    For each of the maxima: suffix 1 for r1, 2 for r2
               mu - center of cauchy and both gaussian functions
                a - height of the signal gaussian function
               si - standard deviation of the signal gaussian function
                b - height of the noise gaussian function
               ta - standard deviation of the noise gaussian function
                c - height of the signal lorentz function
               ga - probable error of the signal lorentz function (floats)
        Return:	value of function with desired parameters in x (float)
        Descr.: Calculate GLg+GLg-type function for given x and parameters"""
    # R2 signal gauss + R2 noise gauss +
    # R1 signal gauss + R1 noise gauss
    return gauss(x, a2, mu2, si2) + gauss(x, b2, mu2, ta2) + \
        gauss(x, a1, mu1, si1) + gauss(x, b1, mu1, ta1)


def dromedaries_fixed(mu1, a1, si1, b1, ta1, mu2, a2, si2, b2, ta2):
    """	Input:      For each of the maxima: suffix 1 for r1, 2 for r2
               mu - center of cauchy and both gaussian functions
                a - height of the signal gaussian function
               si - standard deviation of the signal gaussian function
                b - height of the noise gaussian function
               ta - standard deviation of the noise gaussian function (floats)
        Return:	dromedaries function of an 'x' parameter      (float)
        Descr.: Produce Gg+Gg(x)-type function with fixed parameters"""
    def dromedaries_baby(x):
        return dromedaries(x, mu1, a1, si1, b1, ta1, mu2, a2, si2, b2, ta2)
    return dromedaries_baby


def gauss(x, a, mu, si):
    """	Input: x - value and a, mu, si - gaussian coeffitients  (float)
        Return:	value of function with desired parameters in x (float)
        Descr.: Calculate G-type function for given x and parameters"""
    return a * np.exp(-(x - mu) ** 2 / (2. * si ** 2))


def gauss_fixed(a, mu, si):
    """	Input:  a, mu, si - gaussian coeffitients               (float)
        Return:	gauss function of an 'x' parameter              (float)
        Descr.: Produce G(x)-type function with fixed parameters"""
    def gauss_baby(x):
        return gauss(x, a, mu, si)
    return gauss_baby


def labspec(x, mu, a, si, b, ga):
    """	Input: x - value
               mu - center of lorentz and gaussian functions
               a - height of gaussian function
               si - standard deviation of the gaussian function
               b - height of lorentz function
               ga - probable error of the lorentz function (floats)
        Return:	value of function with desired parameters in x (float)
        Descr.: Calculate GL-type function for given x and parameters"""
    return gauss(x, a, mu, si) + lorentz(x, b, mu, ga)


def labspec_fixed(mu, a, si, b, ga):
    """	Input: mu - center of lorentz and gaussian functions
               a - height of gaussian function
               si - standard deviation of the gaussian function
               b - height of lorentz function
               ga - probable error of the lorentz function (floats)
        Return:	labspec function of an 'x' parameter              (float)
        Descr.: Produce GL(x)-type function with fixed parameters"""
    def labspec_baby(x):
        return labspec(x, mu, a, si, b, ga)
    return labspec_baby


def lorentz(x, a, mu, ga):
    """	Input: x - value and a=I, mu=x_0, ga - lorentz f. coeffitients  (float)
        Return:	value of function with desired parameters in x (float)
        Descr.: Calculate L-type function for given x and parameters"""
    return (a * ga ** 2) / ((x - mu) ** 2 + ga ** 2)


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
    popt, pcov = curve_fit(linear, xdata=edge_dots[:, 0], ydata=edge_dots[:, 1],
                               p0=guess)
    sigma = np.sqrt(np.diag(pcov))

    # PREPARE DOTS CORRECTED FOR BACKGROUND
    background = linear_fixed(popt[0], popt[1])
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
    popt, pcov = curve_fit(camel, xdata=dots[:, 0], ydata=dots[:, 1], p0=guess,
                           sigma=dots_sigma)
    sigma = np.sqrt(np.diag(pcov))

    # FIND ACTUAL MAXIMA AND RETURN DATA
    dx = peakhunt_range
    r1_val = minimize_scalar(lambda x: -camel_fixed(*popt)(x), method='Bounded',
                              bounds=(popt[1]-dx, popt[1]+dx)).x
    r2_val = minimize_scalar(lambda x: -camel_fixed(*popt)(x), method='Bounded',
                              bounds=(popt[4]-dx, popt[4]+dx)).x

    return {'r1_val': r1_val,
            'r1_unc': sigma[1],
            'r1_int': camel(r1_val, *popt) + background(r1_val),
            'r2_val': r2_val,
            'r2_unc': sigma[4],
            'r2_int': camel(r2_val, *popt) + background(r2_val),
            'fit_function': [lambda x: camel_fixed(*popt)(x) + background(x)],
            'fit_range': [(x_beg, x_end), (x_beg, x_end)]}


def bactrian_fit(dots):
    """	Input:	dots - ruby spectrum data (n x 2 ndarray)
        Return:	dict with r1, r2 and fit description
        Descr.: Fit G+G-type "bactrian" function to dots"""

    # LOAD PEAKS AND ESTIMATE BACKGROUND
    estimated_background = estimate_background(dots)
    background = estimated_background['background']
    dots = estimated_background['corrected_dots']
    peaks = peak_search(dots)[:2, :]

    # ESTIMATE INITIAL GAUSSIAN PARAMETERS
    si1, si2 = 0.35, 0.35
    mu1 = peaks[0, 0]
    a1 = peaks[0, 1]
    mu2 = peaks[1, 0]
    a2 = peaks[1, 1]
    guess = (a1, mu1, si1, a2, mu2, si2)

    # TRIM DATA AND FIT THE BACTRIAN CURVE
    x_beg = peaks[1, 0] - 2 * peakhunt_range
    x_end = peaks[0, 0] + 2 * peakhunt_range
    dots = trim_to_range(dots, x_beg, x_end)
    dots_sigma = peaks[0, 1] * np.power(dots[:, 1], -1)
    popt, pcov = curve_fit(bactrian, xdata=dots[:, 0], ydata=dots[:, 1],
                           p0=guess, sigma=dots_sigma)
    sigma = np.sqrt(np.diag(pcov))

    # FIND ACTUAL MAXIMA AND RETURN DATA
    return {'r1_val': popt[1],
            'r1_unc': sigma[1],
            'r1_int': bactrian(popt[1], *popt) + background(popt[1]),
            'r2_val': popt[4],
            'r2_unc': sigma[4],
            'r2_int': bactrian(popt[4], *popt) + background(popt[4]),
            'fit_function': [lambda x: bactrian_fixed(*popt)(x) + background(x)],
            'fit_range': [(x_beg, x_end)]}


def dromedaries_fit(dots):
    """	Input:	dots - ruby spectrum data (n x 2 ndarray)
        Return:	dict with r1, r2 and fit description
        Descr.: Fit GLg+GLg-type "dromedaries" function to dots"""

    # LOAD PEAKS AND ESTIMATE BACKGROUND
    estimated_background = estimate_background(dots)
    background = estimated_background['background']
    dots = estimated_background['corrected_dots']
    peaks = peak_search(dots)[:2, :]

    # ESTIMATE INITIAL GAUSSIAN & LORENTZIAN PARAMETERS
    mu1, mu2 = peaks[0, 0], peaks[1, 0]
    a1, a2 = 0.75*peaks[0, 1], 0.75*peaks[1, 1]
    si1, si2 = 0.35, 0.35
    b1, b2 = 0.25*peaks[0, 1], 0.25*peaks[1, 1]
    ta1, ta2 = 1.00, 1.00
    guess = (mu1, a1, si1, b1, ta1, mu2, a2, si2, b2, ta2)

    # TRIM DATA AND FIT THE DROMEDARIES CURVE
    x_beg = peaks[1, 0] - 2 * peakhunt_range
    x_end = peaks[0, 0] + 2 * peakhunt_range
    dots = trim_to_range(dots, x_beg, x_end)
    dots_sigma = peaks[0, 1] * np.power(dots[:, 1], -1)
    popt, pcov = curve_fit(dromedaries, xdata=dots[:, 0], ydata=dots[:, 1],
                           p0=guess, sigma=dots_sigma)
    # popt, pcov = guess, guess
    sigma = np.sqrt(np.diag(pcov))

    # RETURN DATA
    return {'r1_val': popt[0],
            'r1_unc': sigma[0],
            'r1_int': dromedaries(popt[0], *popt) + background(popt[0]),
            'r2_val': popt[5],
            'r2_unc': sigma[5],
            'r2_int': dromedaries(popt[5], *popt) + background(popt[5]),
            'fit_function':
                [lambda x: dromedaries_fixed(*popt)(x) + background(x)],
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
    dots1_sigma = peaks[0, 1] * np.power(dots1[:, 1], -1)
    popt1, pcov1 = curve_fit(gauss, xdata=dots1[:, 0], ydata=dots1[:, 1],
                             p0=guess1, sigma=dots1_sigma)
    sigma1 = np.sqrt(np.diag(pcov1))
    dots2_sigma = peaks[1, 1] * np.power(dots2[:, 1], -1)
    popt2, pcov2 = curve_fit(gauss, xdata=dots2[:, 0], ydata=dots2[:, 1],
                             p0=guess2, sigma=dots2_sigma)
    sigma2 = np.sqrt(np.diag(pcov2))
    return {'r1_val': popt1[1],
            'r1_unc': sigma1[1],
            'r1_int': popt1[0] + background(popt1[1]),
            'r2_val': popt2[1],
            'r2_unc': sigma2[1],
            'r2_int': popt2[0] + background(popt2[1]),
            'fit_function':
                [lambda x: gauss_fixed(*popt1)(x) + background(x),
                 lambda x: gauss_fixed(*popt2)(x) + background(x)],
            'fit_range': [(x_beg1, x_end1), (x_beg2, x_end2)]}


def labspec_fit(dots):
    """	Input:	dots - ruby spectrum data (n x 2 ndarray)
        Return:	dict with r1, r2 and fit description
        Descr.: Fit GL-type "two labspec" function to dots"""

    # LOAD PEAKS AND ESTIMATE BACKGROUND
    estimated_background = estimate_background(dots)
    background = estimated_background['background']
    dots = estimated_background['corrected_dots']
    peaks = peak_search(dots)[:2, :]

    # ESTIMATE INITIAL LABSPEC PARAMETERS
    mu1, mu2 = peaks[0, 0], peaks[1, 0]
    a1, a2 = 0.5*peaks[0, 1], 0.5*peaks[1, 1]
    si1, si2 = 0.35, 0.35
    b1, b2 = 0.5*peaks[0, 1], 0.5*peaks[1, 1]
    ga1, ga2 = 0.20, 0.20
    guess1, guess2 = (mu1, a1, si1, b1, ga1), (mu2, a2, si2, b2, ga2)

    # CUT DATA TO FITTED SURROUNDING
    x_beg1 = peaks[0, 0] - 2 * peakhunt_range
    x_end1 = peaks[0, 0] + 2 * peakhunt_range
    x_beg2 = peaks[1, 0] - 2 * peakhunt_range
    x_end2 = peaks[1, 0] + 2 * peakhunt_range
    dots1 = trim_to_range(dots, x_beg1, x_end1)
    dots2 = trim_to_range(dots, x_beg2, x_end2)

    # FIT THE LABSPEC CURVES AND RETURN DATA
    dots1_sigma = peaks[0, 1] * np.power(dots1[:, 1], -1)
    popt1, pcov1 = curve_fit(labspec, xdata=dots1[:, 0], ydata=dots1[:, 1],
                             p0=guess1, sigma=dots1_sigma)
    sigma1 = np.sqrt(np.diag(pcov1))
    dots2_sigma = peaks[1, 1] * np.power(dots2[:, 1], -1)
    popt2, pcov2 = curve_fit(labspec, xdata=dots2[:, 0], ydata=dots2[:, 1],
                             p0=guess2, sigma=dots2_sigma)
    sigma2 = np.sqrt(np.diag(pcov2))
    return {'r1_val': popt1[0],
            'r1_unc': sigma1[0],
            'r1_int': popt1[1] + popt1[3] + background(popt1[0]),
            'r2_val': popt2[0],
            'r2_unc': sigma2[0],
            'r2_int': popt2[1] + popt2[3] + background(popt2[0]),
            'fit_function':
                [lambda x: labspec_fixed(*popt1)(x) + background(x),
                 lambda x: labspec_fixed(*popt2)(x) + background(x)],
            'fit_range': [(x_beg1, x_end1), (x_beg2, x_end2)]}


if __name__ == '__main__':
    pass
