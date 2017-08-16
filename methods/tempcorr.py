# HELPER FUNCTIONS
def default():
    return ragan


def methods():
    return {'vos':   vos,
            'ragan': ragan,
            'none':  none}


# BASIC FUNCTIONS
def wavenumber_to_wavelength(wavenumber):
    """	Input:	wavenumber in cm^-1 (ufloat)
        Return:	wavelength in nm    (ufloat)
        Descr.: Calculate the value described above	"""
    return 10000000. / wavenumber


def wavelength_to_wavenumber(wavelength):
    """	Input:	wavenumber in nm    (ufloat)
        Return:	wavelength in cm^-1 (ufloat)
        Descr.: Calculate the value described above	"""
    return 10000000. / wavelength


def none(**_):
    """	Input:	anything
        Return:	0.0       (float)
        Descr.: Dummy method to handle no temperature correction"""
    return 0.0


def ragan_pressure(peak_number, temperature):
    """	Input:	peak_number: 'r1' or 'r2'  (string)
                temperature: in C degrees  (ufloat)
        Return:	ruby peak wavenumber shift (ufloat)
        Descr.: Calculate r1 or r2 in given temperature and atmo pressure,
                based on doi:10.1063/1.351951 in temperature under 26.85 oC"""
    t = temperature + 273.15
    if peak_number == 'r1':
        r_wavenumber = 14423. + 4.49 * 10 ** (-2) * t \
                                 - 4.81 * 10 ** (-4) * t ** 2 \
                                 + 3.71 * 10 ** (-7) * t ** 3
    elif peak_number == 'r2':
        r_wavenumber = 14452. + 3.00 * 10 ** (-2) * t \
                             - 3.88 * 10 ** (-4) * t ** 2 \
                             + 2.55 * 10 ** (-7) * t ** 3
    else:
        raise NameError('Peak number not defined. Use "r1" or "r2".')
    return wavenumber_to_wavelength(r_wavenumber)


# TEMPERATURE CORRECTORS
def ragan(peak_number, t_sam, t_ref, **_):
    """	Input:	peak_number: 'r1' or 'r2'        (string)
                t_sam & t_ref in C degrees       (ufloat)
        Return:	ruby peak wavenumber shift in nm (ufloat)
        Descr.: Calculate r1 or r2 shift in given temperature in nm (ufloat)"""
    return ragan_pressure(peak_number, t_sam) - \
           ragan_pressure(peak_number, t_ref)


def vos(peak_number, t_sam, **_):
    """	Input:	peak_number: 'r1' or 'r2'        (string)
                t_sam in C degrees               (ufloat)
        Return:	ruby peak wavenumber shift in nm (ufloat)
        Descr.: Calculate r1 or (r1+r2)/2, for r2, shift in given temperature,
                based on doi:10.1063/1.348903"""
    if peak_number == 'r1':
        shift_in_a = 6.591 * 10 ** (-2) * (t_sam - 26.85) + \
                     7.624 * 10 ** (-5) * (t_sam - 26.85) ** 2 - \
                     1.733 * 10 ** (-7) * (t_sam - 26.85) ** 3
    elif peak_number == 'r2':
        shift_in_a = 6.554 * 10 ** (-2) * (t_sam - 26.85) + \
                     8.670 * 10 ** (-5) * (t_sam - 26.85) ** 2 - \
                     1.099 * 10 ** (-7) * (t_sam - 26.85) ** 3
    else:
        raise NameError('Peak number not defined. Use "r1" or "r2".')
    return 0.1 * shift_in_a
