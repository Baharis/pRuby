import abc
from ..utility.functions import polynomial
from ..constants import T_0, UZERO


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


class CorrectingStrategy(abc.ABC):
    @property
    @abc.abstractmethod
    def name(self) -> str:
        pass

    @abc.abstractmethod
    def correct(self, calc):
        pass


class VosR1CorrectingStrategy(CorrectingStrategy):
    """Based on doi:10.1063/1.348903"""
    name = 'Vos R1'  # (1991)

    def correct(self, calc):
        calc.t_correction = -vos_r1_shift(calc.t)


class VosR2CorrectingStrategy(CorrectingStrategy):
    """Based on doi:10.1063/1.348903"""
    name = 'Vos R2'  # (1991)

    def correct(self, calc):
        calc.t_correction = -vos_r2_shift(calc.t)


class VosR12CorrectingStrategy(CorrectingStrategy):
    """Based on doi:10.1063/1.348903"""
    name = 'Vos average'  # (1991)

    def correct(self, calc):
        calc.t_correction = \
            - 0.5 * vos_r2_shift(calc.t) - 0.5 * vos_r1_shift(calc.t)


class RaganR1CorrectingStrategy(CorrectingStrategy):
    """Based on doi:10.1063/1.351951"""
    name = 'Ragan R1'  # (1992)

    def correct(self, calc):
        calc.t_correction = ragan_r1_position(T_0) - ragan_r1_position(calc.t)


class RaganR2CorrectingStrategy(CorrectingStrategy):
    """Based on doi:10.1063/1.351951"""
    name = 'Ragan R2'  # (1992)

    def correct(self, calc):
        calc.t_correction = ragan_r2_position(T_0) - ragan_r2_position(calc.t)


class RaganR12CorrectingStrategy(CorrectingStrategy):
    """Based on doi:10.1063/1.351951"""
    name = 'Ragan average'  # (1992)

    def correct(self, calc):
        calc.t_correction = (ragan_r1_position(T_0)-ragan_r1_position(calc.t) +
                             ragan_r2_position(T_0)-ragan_r2_position(calc.t))/2


class NoneCorrectingStrategy(CorrectingStrategy):
    name = 'None'

    def correct(self, calc):
        calc.t_correction = UZERO
