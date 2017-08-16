import uncertainties as uc


# HELPER FUNCTIONS
def default():
    return liu


def methods():
    return {'liu':        liu,
            'mao':        mao,
            'piermarini': piermarini,
            'wei':        wei}


def mao_like(r1, a, b):
    """	Input:	a [GPa] and b [1] "mao-like" form parameters (floats)
        Return:	"mao-like" function with a and b parameters fixed
        Descr.: produce function similar to doi:10.1063/1.325277"""
    la_0 = 694.24                               # nm
    return (a / b) * (((r1 / la_0) ** b) - 1)   # GPa


# PRESSURE CALCULATORS
def liu(r1_sam, t_sam, t_ref, tempcorr_method, **_):
    """	Input:	'r1_sam' peak pos. in nm & 't_sam' ruby temp. in K (ufloats)
        Return:	calculated pressure in GPa                         (ufloat)
        Descr.: Calculate pressure based on doi:10.1088/1674-1056/22/5/056201"""
    pa = 1.01325e-4                    # atmospheric pressure in GPa
    r1 = r1_sam + tempcorr_method(**{'peak_number': 'r1',
                             't_sam': t_sam, 't_ref': t_ref})
    return mao_like(r1, a=1904, b=9.827)


def mao(r1_sam, t_sam, t_ref, tempcorr_method, **_):
    """	Input:	'r1_sam' peak pos. in nm & 't_sam' ruby temp. in K (ufloats)
        Return:	calculated pressure in GPa                         (ufloat)
        Descr.: Calculate pressure based on doi:10.1063/1.321957"""
    pa = 1.01325e-4                    # atmospheric pressure in GPa
    r1 = r1_sam + tempcorr_method(**{'peak_number': 'r1',
                             't_sam': t_sam, 't_ref': t_ref})
    return mao_like(r1, a=1904, b=7.665)


def piermarini(r1_sam, t_sam, r1_ref, t_ref, tempcorr_method, **_):
    """	Input:	'r1_sam' & 'r1_ref' peak positions (ufloat)
                't_sam' & 't_ref' ruby temperatures (ufloat)
        Return:	calculated pressure               (ufloat)
        Descr.: Calculate pressure based on doi:10.1063/1.321957"""
    pa = 1.01325e-4                    # atmospheric pressure in GPa
    s1 = r1_sam - r1_ref               # shift in nm
    s1 += tempcorr_method(**{'peak_number': 'r1',
                             't_sam': t_sam, 't_ref': t_ref})
    s1 *= 10                           # shift in A
    a = uc.ufloat(2.740, 0.016)        # kbar/A
    return pa + 0.1 * (a * s1)


def wei(r1_sam, t_sam, **_):
    """	Input:	'r1_sam' peak pos. in nm & 't_sam' ruby temp. in K (ufloats)
        Return:	calculated pressure in GPa                         (ufloat)
        Descr.: Calculate pressure based on doi:10.1063/1.3624618"""
    a_300 = uc.ufloat(1915.0, 0.9)            # GPa
    a_1 = uc.ufloat(0.622, 0.007)             # GPa/K
    b_300 = uc.ufloat(9.28, 0.02)             # 1
    b_1 = uc.ufloat(-0.024, 0.003)            # 1/K
    b_2 = uc.ufloat(-8.2e-7, 0.02e-7)         # 1/K^2
    la_300 = 694.2                            # nm
    la_1 = uc.ufloat(0.0063, 0.0002)          # nm/K
    t_ref = 24.85                             # K
    dt = t_sam - t_ref                        # K
    dt2 = dt * dt                             # K^2
    a = a_300 + a_1 * dt                      # GPa
    b = b_300 + b_1 * dt + b_2 * dt2          # 1
    la_t = la_300 + la_1 * dt                 # nm
    return (a/b) * (pow(r1_sam / la_t, b) - 1.0)  # GPa
