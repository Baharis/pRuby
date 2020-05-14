from uncertainties import ufloat
from ..utility.maths import polynomial
from ..constants import T_0


def to_wavelength(wavenumber):
    """Recalculate wavenumber in cm^-1 to wavelength in nm."""
    return 1e7 / wavenumber


def ragan_r1_position(t):
    return to_wavelength(polynomial(14423, 4.49e-2, -4.81e-4, 3.71e-7)(t))


def ragan_r2_position(t):
    return to_wavelength(polynomial(14452, 3.00e-2, -3.88e-4, 2.55e-7)(t))


def vos_r1_shift(t):
    return 0.1 * polynomial(0.0, 6.591e-2, 7.624e-5, -1.733e-7)(t - 300.0)


def vos_r2_shift(t):
    return 0.1 * polynomial(0.0, 6.554e-2, 8.670e-5, -1.099e-7)(t - 300.0)


class TemplateCorrectionRoutine:
    def __init__(self):
        self.t = T_0

    @property
    def correction(self):
        return 0.0

    def correct(self, temperature):
        self.t = temperature
        return self.correction


class VosR1CorrectionRoutine(TemplateCorrectionRoutine):
    """Based on doi:10.1063/1.348903"""
    name = 'Vos R1'  # (1991)

    @property
    def correction(self):
        return -vos_r1_shift(self.t)


class VosR2CorrectionRoutine(TemplateCorrectionRoutine):
    """Based on doi:10.1063/1.348903"""
    name = 'Vos R2'  # (1991)

    @property
    def correction(self):
        return -vos_r2_shift(self.t)


class VosR12CorrectionRoutine(TemplateCorrectionRoutine):
    """Based on doi:10.1063/1.348903"""
    name = 'Vos average'  # (1991)

    @property
    def correction(self):
        return - 0.5 * vos_r2_shift(self.t) - 0.5 * vos_r1_shift(self.t)


class RaganR1CorrectionRoutine(TemplateCorrectionRoutine):
    """Based on doi:10.1063/1.351951"""
    name = 'Ragan R1'  # (1992)

    @property
    def correction(self):
        return ragan_r1_position(T_0) - ragan_r1_position(self.t)


class RaganR2CorrectionRoutine(TemplateCorrectionRoutine):
    """Based on doi:10.1063/1.351951"""
    name = 'Ragan R2'  # (1992)

    @property
    def correction(self):
        return ragan_r2_position(T_0) - ragan_r2_position(self.t)


class RaganR12CorrectionRoutine(TemplateCorrectionRoutine):
    """Based on doi:10.1063/1.351951"""
    name = 'Ragan average'  # (1992)

    @property
    def correction(self):
        return (ragan_r1_position(T_0) - ragan_r1_position(self.t) +
                ragan_r2_position(T_0) - ragan_r2_position(self.t)) / 2


class NoneCorrectionRoutine(TemplateCorrectionRoutine):
    name = 'None'

    @property
    def correction(self):
        return ufloat(0.0, 0.0)
