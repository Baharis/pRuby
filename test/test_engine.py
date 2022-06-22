import unittest
from pruby.engine import Engine
from pruby.calculator import PressureCalculator
from pruby.strategies import \
    BaseStrategy, \
    ReadingStrategies, \
    BackfittingStrategies, \
    PeakfittingStrategies, \
    CorrectingStrategies, \
    TranslatingStrategies, \
    DrawingStrategies


class TestStrategy(unittest.TestCase):
    subengines = ['reader', 'backfitter', 'peakfitter',
                   'corrector', 'translator', 'drawer']
    strategy_types = ['reading', 'peakfitting', 'backfitting',
                      'correcting', 'translating', 'drawing']
    strategy_families = [ReadingStrategies, BackfittingStrategies,
                         PeakfittingStrategies, CorrectingStrategies,
                         TranslatingStrategies, DrawingStrategies]

    def test_create_empty(self):
        self.assertIsNotNone(Engine(calc=PressureCalculator()))

    def test_has_default_strategies(self):
        e = Engine(calc=PressureCalculator())
        for subengine in self.subengines:
            self.assertTrue(hasattr(e, subengine))

    def test_can_set_null_strategies(self):
        s = Engine(calc=PressureCalculator())
        s.set_strategy()
        for sub in self.subengines:
            self.assertIsInstance(getattr(s, sub), BaseStrategy)

    def test_can_set_real_strategies(self):
        s1 = Engine(calc=PressureCalculator())
        s2 = Engine(calc=PressureCalculator())
        for stype, sfamily in zip(self.strategy_types, self.strategy_families):
            name_of_non_default_strategy = [k for k in sfamily.registry.keys()
                                            if k is not sfamily.default.name][0]
            s1.set_strategy(**{stype: name_of_non_default_strategy})
        for sub in self.subengines:
            self.assertNotEqual(type(getattr(s1, sub)), type(getattr(s2, sub)))

    def test_cant_set_unexisting_strategies(self):
        s = Engine(calc=PressureCalculator())
        for sub in self.subengines:
            with self.assertRaises(TypeError):
                s.set_strategy(**{sub: f'dummy {sub} name'})

    def test_can_assign_real_subengines(self):
        s1 = Engine(calc=PressureCalculator())
        s2 = Engine(calc=PressureCalculator())
        for sub, sfamily in zip(self.subengines, self.strategy_families):
            non_default_strategy = [v for v in sfamily.registry.values()
                                    if v.name != sfamily.default.name][0]
            setattr(s1, sub, non_default_strategy)
        for sub in self.subengines:
            self.assertNotEqual(type(getattr(s1, sub)), type(getattr(s2, sub)))


if __name__ == '__main__':
    unittest.main()
