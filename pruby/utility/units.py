class UnitConverter:
    def __init__(self, base_unit):
        self.units = [base_unit]
        self.converters_to_base = {base_unit: lambda x: x}
        self.converters_from_base = {base_unit: lambda x: x}

    def add_unit(self, name, converter_to_base, converter_from_base):
        self.units.append(name)
        self.converters_to_base[name] = converter_to_base
        self.converters_from_base[name] = converter_from_base

    def convert(self, value, from_, to):
        value_in_base_unit = self.converters_to_base[from_](value)
        value_in_new_unit = self.converters_from_base[to](value_in_base_unit)
        return value_in_new_unit


def c_to_k(c):
    return c + 273.0


def f_to_k(f):
    return 5.0 / 9.0 * (f - 32.0) + 273.0


def k_to_c(k):
    return k - 273.0


def k_to_f(k):
    return 9.0 / 5.0 * (k - 273.0) + 32.0


temperature = UnitConverter(base_unit='K')
temperature.add_unit('\u00B0C', c_to_k, k_to_c)
temperature.add_unit('\u00B0F', f_to_k, k_to_f)


def nm_rec_cm_conv(nm_or_cm):
    return 1e7 / nm_or_cm


wavelength = UnitConverter(base_unit='nm')
wavelength.add_unit('cm\u207B\u00B9', nm_rec_cm_conv, nm_rec_cm_conv)


def kbar_to_gpa(kbar):
    return kbar / 10.0


def gpa_to_kbar(gpa):
    return gpa * 10.0


pressure = UnitConverter(base_unit='GPa')
pressure.add_unit('kbar', kbar_to_gpa, gpa_to_kbar)
