import unittest
from pruby.strategy import Strategy
from pruby.calculator import PressureCalculator


class TestStrategy(unittest.TestCase):
    def test_create_empty(self):
        self.assertIsNotNone(Strategy(calc=PressureCalculator()))

    def test_has_default_strategies(self):
        self.assertIsNotNone(Strategy(calc=PressureCalculator()).reader)
        self.assertIsNotNone(Strategy(calc=PressureCalculator()).backfitter)
        self.assertIsNotNone(Strategy(calc=PressureCalculator()).peakfitter)
        self.assertIsNotNone(Strategy(calc=PressureCalculator()).corrector)
        self.assertIsNotNone(Strategy(calc=PressureCalculator()).translator)
        self.assertIsNotNone(Strategy(calc=PressureCalculator()).drawer)

    def test_can_set_null_strategies(self):
        s1 = Strategy(calc=PressureCalculator())
        s2 = Strategy(calc=PressureCalculator())
        s1.set()
        self.assertEqual(s1.reader.name, s2.reader.name)
        self.assertEqual(s1.backfitter.name, s2.backfitter.name)
        self.assertEqual(s1.peakfitter.name, s2.peakfitter.name)
        self.assertEqual(s1.corrector.name, s2.corrector.name)
        self.assertEqual(s1.translator.name, s2.translator.name)
        self.assertEqual(s1.drawer.name, s2.drawer.name)

    def test_can_set_real_strategies(self):
        s1 = Strategy(calc=PressureCalculator())
        s2 = Strategy(calc=PressureCalculator())
        s1.set(reading=Strategy.readers[-1].name)
        s1.set(peakfitting=Strategy.peakfitters[-1].name)
        s1.set(backfitting=Strategy.backfitters[-1].name)
        s1.set(correcting=Strategy.correctors[-1].name)
        s1.set(translating=Strategy.translators[-1].name)
        s1.set(drawing=Strategy.drawers[-1].name)
        self.assertNotEqual(s1.reader.name, s2.reader.name)
        self.assertNotEqual(s1.backfitter.name, s2.backfitter.name)
        self.assertNotEqual(s1.peakfitter.name, s2.peakfitter.name)
        self.assertNotEqual(s1.corrector.name, s2.corrector.name)
        self.assertNotEqual(s1.translator.name, s2.translator.name)
        self.assertNotEqual(s1.drawer.name, s2.drawer.name)

    def test_cant_set_unexisting_strategies(self):
        s = Strategy(calc=PressureCalculator())
        with self.assertRaises(KeyError):
            s.set(reading='dummy reader name')
        with self.assertRaises(KeyError):
            s.set(peakfitting='dummy peakfitter name')
        with self.assertRaises(KeyError):
            s.set(backfitting='dummy backfitter name')
        with self.assertRaises(KeyError):
            s.set(correcting='dummy corrector name')
        with self.assertRaises(KeyError):
            s.set(translating='dummy translator name')
        with self.assertRaises(KeyError):
            s.set(drawing='dummy drawer name')


if __name__ == '__main__':
    unittest.main()
