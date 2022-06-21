import unittest
import os
from pruby.calculator import PressureCalculator


class TestCalculator(unittest.TestCase):
    def test_create_empty(self):
        self.assertIsNotNone(PressureCalculator())

    def test_zero_pressure_on_start(self):
        calc = PressureCalculator()
        calc.calculate_p_from_r1()
        self.assertAlmostEqual(calc.p.n, 0.0, places=1)

    def test_pressure_changes_with_input(self):
        calc = PressureCalculator()
        p1 = calc.p
        calc.r1 = calc.r1 + 0.1
        calc.calculate_p_from_r1()
        p2 = calc.p
        calc.t = calc.t + 1.0
        calc.calculate_p_from_r1()
        p3 = calc.p
        self.assertNotAlmostEqual(p1.n, p2.n)
        self.assertNotAlmostEqual(p2.n, p3.n)

    def test_reference_changes(self):
        calc = PressureCalculator()
        calc.r1 = calc.r1 + 0.1
        calc.t = calc.t + 1.0
        calc.set_current_as_reference()
        calc.calculate_p_from_r1()
        self.assertAlmostEqual(calc.p.n, 0.0, places=4)

    def test_r1_calculations_in_modest_range(self):
        calc = PressureCalculator()
        calc.p = calc.p + 100.0
        calc.calculate_r1_from_p()
        self.assertGreater(calc.r1, 710.0)
        calc.p = calc.p - 110.0
        calc.calculate_r1_from_p()
        self.assertLess(calc.r1, 693.0)

    @staticmethod
    def _get_absolute_example_path(typ_):
        test_wd = os.path.dirname(os.path.realpath(__file__))
        example_wd = os.path.join(test_wd, '..', 'resources')
        if typ_ == 'simple':
            return os.path.join(example_wd, 'example1.txt')
        else:
            return os.path.join(example_wd, 'example2.txt')

    def test_reading_and_fitting_simple_raw_file(self):
        calc = PressureCalculator()
        calc.filename = self._get_absolute_example_path('simple')
        calc.read_and_fit()
        self.assertGreater(calc.r1.n, 694.0)

    def test_reading_and_fitting_meta_file(self):
        calc = PressureCalculator()
        calc.strategy.set(reading='Metadata txt')
        calc.filename = self._get_absolute_example_path('meta')
        calc.read_and_fit()
        self.assertGreater(calc.r1.n, 694.0)

    def test_different_fitters_give_different_r1(self):
        calc1 = PressureCalculator()
        calc2 = PressureCalculator()
        calc3 = PressureCalculator()
        calc1.filename = self._get_absolute_example_path('simple')
        calc2.filename = self._get_absolute_example_path('simple')
        calc3.filename = self._get_absolute_example_path('simple')
        calc1.strategy.set(backfitting='Linear Huber',
                           peakfitting='Gaussian')
        calc2.strategy.set(backfitting='Linear Satelite',
                           peakfitting='Gaussian')
        calc3.strategy.set(backfitting='Linear Huber',
                           peakfitting='Pseudovoigt')
        calc1.read_and_fit()
        calc2.read_and_fit()
        calc3.read_and_fit()
        self.assertNotAlmostEqual(calc1.r1.n, calc2.r1.n)
        self.assertNotAlmostEqual(calc1.r1.n, calc3.r1.n)

    def test_different_correctors_translators_give_different_p(self):
        calc1 = PressureCalculator()
        calc2 = PressureCalculator()
        calc3 = PressureCalculator()
        calc1.r1, calc1.t = calc1.r1 + 2.0, calc1.t + 2.0
        calc1.r2, calc2.t = calc2.r1 + 2.0, calc2.t + 2.0
        calc1.r3, calc3.t = calc3.r1 + 2.0, calc3.t + 2.0
        calc1.strategy.set(correcting='Vos R1',
                           translating='Liu')
        calc2.strategy.set(correcting='Ragan R1',
                           translating='Liu')
        calc3.strategy.set(correcting='Vos R1',
                           translating='Piermarini')
        calc1.calculate_p_from_r1()
        calc2.calculate_p_from_r1()
        calc3.calculate_p_from_r1()
        self.assertNotAlmostEqual(calc1.p.n, calc2.p.n)
        self.assertNotAlmostEqual(calc1.p.n, calc3.p.n)

    def test_at_least_pretends_to_draw_anything(self):
        calc = PressureCalculator()
        calc.filename = self._get_absolute_example_path('simple')
        calc.read_and_fit()
        calc.calculate_p_from_r1()
        calc.draw()
        self.assertIsNotNone(calc.fig)
        self.assertIsNotNone(calc.ax)


if __name__ == '__main__':
    unittest.main()
