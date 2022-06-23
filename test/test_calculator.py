import pathlib
import unittest
from pruby.engine import Engine
from pruby.calculator import PressureCalculator
from pruby import strategies


test_data1_path = str(pathlib.Path(__file__).parent.joinpath('test_data1.txt'))
test_data2_path = str(pathlib.Path(__file__).parent.joinpath('test_data2.txt'))

subengines = \
    [
        'reader',
        'backfitter',
        'peakfitter',
        'corrector',
        'translator',
        'drawer'
    ]
strategy_types = \
    [
        'reading',
        'peakfitting',
        'backfitting',
        'correcting',
        'translating',
        'drawing'
    ]
strategy_families = \
    [
        strategies.ReadingStrategies,
        strategies.BackfittingStrategies,
        strategies.PeakfittingStrategies,
        strategies.CorrectingStrategies,
        strategies.TranslatingStrategies,
        strategies.DrawingStrategies
    ]
strategy_parents = \
    [
        strategies.ReadingStrategy,
        strategies.BackfittingStrategy,
        strategies.PeakfittingStrategy,
        strategies.CorrectingStrategy,
        strategies.TranslatingStrategy,
        strategies.DrawingStrategy
    ]


class TestEngine(unittest.TestCase):
    def test_create_empty(self):
        self.assertIsNotNone(Engine(calc=PressureCalculator()))

    def test_has_default_strategies(self):
        e = Engine(calc=PressureCalculator())
        for subengine in subengines:
            self.assertTrue(hasattr(e, subengine))

    def test_can_set_null_strategies(self):
        s = Engine(calc=PressureCalculator())
        s.set_strategy()
        for sub in subengines:
            self.assertIsInstance(getattr(s, sub), strategies.BaseStrategy)

    def test_can_set_real_strategies(self):
        s1 = Engine(calc=PressureCalculator())
        s2 = Engine(calc=PressureCalculator())
        for stype, sfamily in zip(strategy_types, strategy_families):
            name_of_non_default_strategy = [k for k in sfamily.registry.keys()
                                            if k is not sfamily.default.name][0]
            s1.set_strategy(**{stype: name_of_non_default_strategy})
        for sub in subengines:
            self.assertNotEqual(type(getattr(s1, sub)), type(getattr(s2, sub)))

    def test_cant_set_unexisting_strategies(self):
        engine = Engine(calc=PressureCalculator())
        for sub in subengines:
            with self.assertRaises(TypeError):
                engine.set_strategy(**{sub: f'dummy {sub} name'})

    def test_can_assign_real_subengines(self):
        s1 = Engine(calc=PressureCalculator())
        s2 = Engine(calc=PressureCalculator())
        for sub, sfamily in zip(subengines, strategy_families):
            non_default_strategy = [v for v in sfamily.registry.values()
                                    if v.name != sfamily.default.name][0]
            setattr(s1, sub, non_default_strategy)
        for sub in subengines:
            self.assertNotEqual(type(getattr(s1, sub)), type(getattr(s2, sub)))


# noinspection PyTypeChecker
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

    def test_reading_and_fitting_simple_raw_file(self):
        calc = PressureCalculator()
        calc.read(test_data1_path)
        self.assertGreater(calc.r1.n, 694.0)

    def test_reading_and_fitting_meta_file(self):
        calc = PressureCalculator()
        calc.engine.set_strategy(reading='Metadata txt')
        calc.read(test_data2_path)
        self.assertGreater(calc.r1.n, 694.0)

    def test_different_fitters_give_different_r1(self):
        calc1 = PressureCalculator()
        calc2 = PressureCalculator()
        calc3 = PressureCalculator()
        calc1.engine.set_strategy(backfitting='Linear Huber',
                                  peakfitting='Gaussian')
        calc2.engine.set_strategy(backfitting='Linear Satelite',
                                  peakfitting='Gaussian')
        calc3.engine.set_strategy(backfitting='Linear Huber',
                                  peakfitting='Pseudovoigt')
        calc1.read(test_data1_path)
        calc2.read(test_data1_path)
        calc3.read(test_data1_path)
        self.assertNotAlmostEqual(calc1.r1.n, calc2.r1.n)
        self.assertNotAlmostEqual(calc1.r1.n, calc3.r1.n)

    def test_different_correctors_translators_give_different_p(self):
        calc1 = PressureCalculator()
        calc2 = PressureCalculator()
        calc3 = PressureCalculator()
        calc1.r1, calc1.t = calc1.r1 + 2.0, calc1.t + 2.0
        calc1.r2, calc2.t = calc2.r1 + 2.0, calc2.t + 2.0
        calc1.r3, calc3.t = calc3.r1 + 2.0, calc3.t + 2.0
        calc1.engine.set_strategy(correcting='Vos R1', translating='Liu')
        calc2.engine.set_strategy(correcting='Ragan R1', translating='Liu')
        calc3.engine.set_strategy(correcting='Vos R1', translating='Piermarini')
        calc1.calculate_p_from_r1()
        calc2.calculate_p_from_r1()
        calc3.calculate_p_from_r1()
        self.assertNotAlmostEqual(calc1.p.n, calc2.p.n)
        self.assertNotAlmostEqual(calc1.p.n, calc3.p.n)


if __name__ == '__main__':
    unittest.main()
