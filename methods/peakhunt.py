import numpy as np
from scipy.signal import find_peaks_cwt
from scipy.optimize import curve_fit, minimize_scalar


peakhunt_fit_width = 0.2


# HELPER FUNCTIONS
def default():
    return labspec_fit


def methods():
    return {'camel_fit':   {'function': camel_fit,   'name': 'Camel Fit'},
            'gauss_fit':   {'function': gauss_fit,   'name': 'Gauss Fit'},
            'labspec_fit': {'function': labspec_fit, 'name': 'Labspec Fit'}}


# BASIC FUNCTIONS
def camel(x, a1, mu1, si1, a2, mu2, si2, a12, mu12, si12):
    """	Input:  x - given point for which camel is calculated
                a0, b0 - linear equation coefitients
                a2, mu2, si2 - r2 gaussian coeffitients
                a1, mu1, si1 - r1 gaussian coeffitients (float)s
        Return:	value of gaussian with desired parameters in x (float)
        Descr.: Calculate the value described above	"""
    return gauss(x, a2, mu2, si2) + gauss(x, a1, mu1, si1)\
           + gauss(x, a12, mu12, si12)


def camel_fixed(a1, mu1, si1, a2, mu2, si2, a12, mu12, si12):
    """	Input:  a0, b0 - linear equation coefitients
                a2, mu2, si2 - r2 gaussian coeffitients
                a1, mu1, si1 - r1 gaussian coeffitients (float)s
        Return:	camel function of an 'x' parameter      (float)
        Descr.: Produce camel(x) function with fixed gaussians' parameters"""
    def camel_baby(x):
        return camel(x, a1, mu1, si1, a2, mu2, si2, a12, mu12, si12)
    return camel_baby


def llama(x, a1, mu1, si1, a2, mu2, si2):
    """	Input:  x - given point for which camel is calculated
                a0, b0 - linear equation coefitients
                a2, mu2, si2 - r2 gaussian coeffitients
                a1, mu1, si1 - r1 gaussian coeffitients (float)s
        Return:	value of gaussian with desired parameters in x (float)
        Descr.: Calculate the value described above	"""
    return gauss(x, a2, mu2, si2) + gauss(x, a1, mu1, si1)


def llama_fixed(a1, mu1, si1, a2, mu2, si2):
    """	Input:  a0, b0 - linear equation coefitients
                a2, mu2, si2 - r2 gaussian coeffitients
                a1, mu1, si1 - r1 gaussian coeffitients (float)s
        Return:	camel function of an 'x' parameter      (float)
        Descr.: Produce camel(x) function with fixed gaussians' parameters"""
    def llama_baby(x):
        return llama(x, a1, mu1, si1, a2, mu2, si2)
    return llama_baby


def gauss(x, a, mu, si):
    """	Input: x - value and a, mu, si - gaussian coeffitients  (float)
        Return:	value of gaussian with desired parameters and x (float)
        Descr.: Calculate the value described above	"""
    return a * np.exp(-(x - mu) ** 2 / (2. * si ** 2))


def gauss_fixed(a, mu, si):
    """	Input:  a, mu, si - gaussian coeffitients               (float)
        Return:	gauss function of an 'x' parameter              (float)
        Descr.: Produce gauss(x) function with fixed parameters"""
    def gauss_baby(x):
        return gauss(x, a, mu, si)
    return gauss_baby


def labspec(x, a, mu, si, ga, ks):
    """	Input: x - value
               a - total height of cauchy and gaussian functions
               mu - center of cauchy and gaussian functions
               si - standard deviation of the gaussian function
               ga - probable error of the lorentz function
               ks - lorentz to gaussian ratio, 1 gives pure lorentz (floats)
        Return:	value of labspec function with desired parameters and x (float)
        Descr.: Calculate the value described above	"""
    return (1-ks) * gauss(x, a, mu, si) + ks * lorentz(x, a, mu, ga)


def labspec_fixed(a, mu, si, ga, ks):
    """	Input: a - total height of cauchy and gaussian functions
               mu - center of cauchy and gaussian functions
               si - standard deviation of the gaussian function
               ga - probable error of the lorentz function
               ks - lorentz to gaussian ratio, 1 gives pure lorentz (floats)
        Return:	gauss function of an 'x' parameter              (float)
        Descr.: Produce labspec(x) function with fixed parameters"""
    def labspec_baby(x):
        return labspec(x, a, mu, si, ga, ks)
    return labspec_baby


def lorentz(x, a, mu, ga):
    """	Input: x - value and a=I, mu=x_0, ga - lorentz f. coeffitients  (float)
        Return:	value of lorentz function with desired parameters and x (float)
        Descr.: Calculate the value described above	"""
    return (a * ga ** 2) / ((x - mu) ** 2 + ga ** 2)


def peak_search(dots):
    """	Input:	dots - ruby spectrum data (n x 2 ndarray)
        Return:	list of data biggest peaks (n x 2 ndarray)
        Descr.: Find and sort biggest peaks in dots data"""
    peak_indexes = find_peaks_cwt(vector=dots[:, 1], widths=[10])
    peaks = np.array([dots[index, :] for index in peak_indexes])
    peaks = peaks[peaks[:, 1].argsort()[::-1]]
    return peaks


# FIT FUNCTIONS
def camel_fit(dots):
    """	Input:	dots - ruby spectrum data (n x 2 ndarray)
        Return:	{'r1' position (ufloat) and 'fit'ted function (function)}
        Descr.: Fit camel function to dots"""

    # ESTIMATE INITIAL a0 AND b0
    peaks = peak_search(dots)[:2, :]
    x_beg, x_end = dots[0, 0], dots[-1, 0]
    y_beg, y_end = dots[0, 1], dots[-1, 1]
    a0 = (y_end - y_beg) / (x_end - x_beg)
    b0 = ((y_beg + y_end) - a0 * (x_beg + x_end)) / 2.0

    # ESTIMATE INITIAL GAUSSIAN PARAMETERS
    si1, si2, si12 = 0.35, 0.35, 1.0
    mu1 = peaks[0, 0]
    a1 = peaks[0, 1] - a0 * mu1 - b0
    mu2 = peaks[1, 0]
    a2 = peaks[1, 1] - a0 * mu2 - b0
    a12 = 0.1 * (a1 + a2)
    mu12 = 0.5 * (mu1 + mu2)
    guess = (a1, mu1, si1, a2, mu2, si2, a12, mu12, si12)

    # CUT DATA TO FITTED SURROUNDING
    x_beg = peaks[1, 0] - 1.5 * peakhunt_fit_width
    x_end = peaks[0, 0] + 1.5 * peakhunt_fit_width
    indices_to_delete = \
        [index for index, x in enumerate(dots[:, 0]) if x < x_beg or x > x_end]
    dots = np.delete(dots, indices_to_delete, axis=0)

    # FIT THE CAMEL CURVE
    popt, pcov = curve_fit(camel, xdata=dots[:, 0], ydata=dots[:, 1], p0=guess,
                           sigma=mu1 * np.power(dots[:, 1], -1))
    sigma = np.sqrt(np.diag(pcov))

    # FIND ACTUAL MAXIMA AND RETURN DATA
    dx = peakhunt_fit_width
    r1_val = minimize_scalar(lambda x: -camel_fixed(*popt)(x), method='Bounded',
                              bounds=(popt[1]-dx, popt[1]+dx)).x
    r2_val = minimize_scalar(lambda x: -camel_fixed(*popt)(x), method='Bounded',
                              bounds=(popt[4]-dx, popt[4]+dx)).x

    return {'r1_val': r1_val,
            'r1_unc': sigma[1],
            'r1_int': camel(r1_val, *popt),
            'r2_val': r2_val,
            'r2_unc': sigma[4],
            'r2_int': camel(r2_val, *popt),
            'fit_function': [camel_fixed(*popt)],
            'fit_range': [(x_beg, x_end)]}


def llama_fit(dots):
    """	Input:	dots - ruby spectrum data (n x 2 ndarray)
        Return:	{'r1' position (ufloat) and 'fit'ted function (function)}
        Descr.: Fit camel function to dots"""

    # ESTIMATE INITIAL a0 AND b0
    peaks = peak_search(dots)[:2, :]
    x_beg, x_end = dots[0, 0], dots[-1, 0]
    y_beg, y_end = dots[0, 1], dots[-1, 1]
    a0 = (y_end - y_beg) / (x_end - x_beg)
    b0 = ((y_beg + y_end) - a0 * (x_beg + x_end)) / 2.0

    # ESTIMATE INITIAL GAUSSIAN PARAMETERS
    si1, si2 = 0.35, 0.35
    mu1 = peaks[0, 0]
    a1 = peaks[0, 1] - a0 * mu1 - b0
    mu2 = peaks[1, 0]
    a2 = peaks[1, 1] - a0 * mu2 - b0
    guess = (a1, mu1, si1, a2, mu2, si2)

    # CUT DATA TO FITTED SURROUNDING
    x_beg = peaks[1, 0] - 1.5 * peakhunt_fit_width
    x_end = peaks[0, 0] + 1.5 * peakhunt_fit_width
    indices_to_delete = \
        [index for index, x in enumerate(dots[:, 0]) if x < x_beg or x > x_end]
    dots = np.delete(dots, indices_to_delete, axis=0)

    # FIT THE CAMEL CURVE
    popt, pcov = curve_fit(llama, xdata=dots[:, 0], ydata=dots[:, 1], p0=guess,
                           sigma=mu1 * np.power(dots[:, 1], -1))
    sigma = np.sqrt(np.diag(pcov))

    # FIND ACTUAL MAXIMA AND RETURN DATA
    dx = peakhunt_fit_width
    r1_val = popt[1]
    r2_val = popt[4]

    return {'r1_val': r1_val,
            'r1_unc': sigma[1],
            'r1_int': llama(r1_val, *popt),
            'r2_val': r2_val,
            'r2_unc': sigma[4],
            'r2_int': llama(r2_val, *popt),
            'fit_function': [llama_fixed(*popt)],
            'fit_range': [(x_beg, x_end)]}


def gauss_fit(dots):
    # ESTIMATE INITIAL GAUSSIAN PARAMETERS
    peaks = peak_search(dots)[:2, :]
    si1, si2 = 0.35, 0.35
    mu1, mu2 = peaks[0, 0], peaks[1, 0]
    a1, a2 = peaks[0, 1], peaks[1, 1]
    guess1, guess2 = (a1, mu1, si1), (a2, mu2, si2)

    # CUT DATA TO FITTED SURROUNDING
    x_beg1 = peaks[0, 0] - peakhunt_fit_width
    x_end1 = peaks[0, 0] + peakhunt_fit_width
    x_beg2 = peaks[1, 0] - peakhunt_fit_width
    x_end2 = peaks[1, 0] + peakhunt_fit_width
    dots1_indices = [i for i, x in enumerate(dots[:, 0]) if x_beg1 < x < x_end1]
    dots1 = dots[dots1_indices, :]
    dots2_indices = [i for i, x in enumerate(dots[:, 0]) if x_beg2 < x < x_end2]
    dots2 = dots[dots2_indices, :]

    # FIT THE GAUSS CURVES AND RETURN DATA
    popt1, pcov1 = \
        curve_fit(gauss, xdata=dots1[:, 0], ydata=dots1[:, 1], p0=guess1)
    sigma1 = np.sqrt(np.diag(pcov1))
    popt2, pcov2 = \
        curve_fit(gauss, xdata=dots2[:, 0], ydata=dots2[:, 1], p0=guess2)
    sigma2 = np.sqrt(np.diag(pcov2))
    return {'r1_val': popt1[1],
            'r1_unc': sigma1[1],
            'r1_int': popt1[0],
            'r2_val': popt2[1],
            'r2_unc': sigma2[1],
            'r2_int': popt2[0],
            'fit_function': [gauss_fixed(*popt1), gauss_fixed(*popt2)],
            'fit_range': [(x_beg1, x_end1), (x_beg2, x_end2)]}


def labspec_fit(dots):
    # ESTIMATE INITIAL LABSPEC PARAMETERS
    peaks = peak_search(dots)[:2, :]
    a1, a2 = peaks[0, 1], peaks[1, 1]
    mu1, mu2 = peaks[0, 0], peaks[1, 0]
    si1, si2 = 0.35, 0.35
    ga1, ga2 = 0.20, 0.20
    ks1, ks2 = 0.50, 0.50
    guess1, guess2 = (a1, mu1, si1, ga1, ks1), (a2, mu2, si2, ga2, ks2)

    # CUT DATA TO FITTED SURROUNDING
    x_beg1 = peaks[0, 0] - 2 * peakhunt_fit_width
    x_end1 = peaks[0, 0] + 2 * peakhunt_fit_width
    x_beg2 = peaks[1, 0] - 1.5 * peakhunt_fit_width
    x_end2 = peaks[1, 0] + 1.5 * peakhunt_fit_width
    dots1_indices = [i for i, x in enumerate(dots[:, 0]) if x_beg1 < x < x_end1]
    dots1 = dots[dots1_indices, :]
    dots2_indices = [i for i, x in enumerate(dots[:, 0]) if x_beg2 < x < x_end2]
    dots2 = dots[dots2_indices, :]

    # FIT THE LABSPEC CURVES AND RETURN DATA
    popt1, pcov1 = \
        curve_fit(labspec, xdata=dots1[:, 0], ydata=dots1[:, 1], p0=guess1)
    sigma1 = np.sqrt(np.diag(pcov1))
    popt2, pcov2 = \
        curve_fit(labspec, xdata=dots2[:, 0], ydata=dots2[:, 1], p0=guess2)
    sigma2 = np.sqrt(np.diag(pcov2))
    return {'r1_val': popt1[1],
            'r1_unc': sigma1[1],
            'r1_int': popt1[0],
            'r2_val': popt2[1],
            'r2_unc': sigma2[1],
            'r2_int': popt2[0],
            'fit_function': [labspec_fixed(*popt1), labspec_fixed(*popt2)],
            'fit_range': [(x_beg1, x_end1), (x_beg2, x_end2)]}


if __name__ == '__main__':
    pass


