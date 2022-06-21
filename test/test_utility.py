import unittest
from math import pi, inf
from pruby.utility import cycle, LineSubset
from pruby.utility import polynomial, gaussian, lorentzian, pseudovoigt


class TestCycle(unittest.TestCase):
    def test_creation(self):
        self.assertTrue(cycle('contents'))

    def test_single_yield(self):
        self.assertTrue(next(cycle('contents')))

    def test_multi_yield(self):
        for index in range(100):
            self.assertTrue(next(cycle('contents')))

    def test_yield_order(self):
        c = cycle(list('contents'))
        self.assertEqual(next(c) + next(c) + next(c), 'con')

    def test_start(self):
        c = cycle(list('contents'), start=3)
        self.assertEqual(next(c) + next(c) + next(c), 'ten')


class TestFunctions(unittest.TestCase):
    def test_empty_polynomial(self):
        self.assertAlmostEqual(polynomial()(pi), 0.0)

    def test_empty_pseudovoigt(self):
        insufficient_arguments = 12., -34., 56.
        self.assertRaises(TypeError, pseudovoigt, insufficient_arguments)

    def test_polynomial_callable(self):
        self.assertTrue(callable(polynomial(12., -34., 56.)))

    def test_gaussian_callable(self):
        self.assertTrue(callable(gaussian(12., -34., 56.)))

    def test_lorenzian_callable(self):
        self.assertTrue(callable(lorentzian(12., -34., 56.)))

    def test_pseudovoigt_callable(self):
        self.assertTrue(callable(pseudovoigt(12., -34., 56., 78.)))

    def test_polynomial_value(self):
        self.assertAlmostEqual(polynomial(12., -34., 56.)(pi), 457.8836962389)

    def test_gaussian_value(self):
        self.assertAlmostEqual(gaussian(12., -34., 56.)(pi), 9.6307508535)

    def test_lorenzian_value(self):
        self.assertAlmostEqual(lorentzian(12., -34., 56.)(pi), 8.3339646686)

    def test_pseudovoigt_value(self):
        self.assertAlmostEqual(pseudovoigt(12, -34, 56, 78)(pi), -58.3996662756)


class TestLineSubset(unittest.TestCase):
    def test_create_from_pair(self):
        self.assertTrue(LineSubset(1.2, inf))

    def test_create_from_list(self):
        self.assertTrue(LineSubset([(-inf, -2), (-1, 1), (1.2, inf)]))

    def test_create_empty(self):
        self.assertTrue(LineSubset())

    def test_create_incorrect(self):
        with self.assertRaises(ValueError):
            LineSubset(3, 2)

    def test_merging(self):
        self.assertEqual(LineSubset([(0, 1), (1, 2), (2, 3)]), LineSubset(0, 3))

    def test_negation(self):
        self.assertEqual(LineSubset([(-inf, -2.2), (3.3, inf)]),
                         -LineSubset(-2.2, 3.3))

    def test_empty_infinity_negation(self):
        self.assertEqual(-(-LineSubset()), LineSubset())

    def test_equal(self):
        self.assertTrue(LineSubset(1.1, 2.2) == LineSubset([(1.1, 2.2)]))

    def test_lesser_than(self):
        self.assertTrue(LineSubset(2.2, 3.3) < LineSubset([(1.1, 3.3), (4, 5)]))

    def test_lesser_equal(self):
        self.assertTrue(LineSubset(1.1, 3.3) <= LineSubset(1.1, 3.3))

    def test_union(self):
        self.assertEqual(LineSubset(1.1, 3.3) + LineSubset(2.2, inf),
                         LineSubset(1.1, inf))

    def test_intersection(self):
        self.assertEqual(LineSubset(-inf, 2.2) * LineSubset(1.1, 3.3),
                         LineSubset(1.1, 2.2))

    def test_subtraction(self):
        self.assertEqual(LineSubset(-inf, 2.2) - LineSubset(1.1, 3.3),
                         LineSubset(-inf, 1.1))

    def test_division(self):
        self.assertEqual(LineSubset(-inf, 2.2) / LineSubset(1.1, 3.3),
                         LineSubset([(-inf, 1.1), (2.2, 3.3)]))

    def test_representation(self):
        self.assertIn('2.2, inf', repr(LineSubset(2.2, inf)))

    def test_string(self):
        self.assertIn('2.2, inf', str(LineSubset(2.2, inf)))

    def test_max(self):
        self.assertEqual(max(LineSubset(-inf, -2.2)), -2.2)

    def test_iterator(self):
        self.assertEqual(list(LineSubset([(0, 1), (2, 3)])), [0, 1, 2, 3])

    def test_contains_float(self):
        self.assertIn(1.1, LineSubset(1.1, inf))

    def test_contains_other(self):
        self.assertIn(LineSubset(1.1, 3.3), LineSubset(1.1, inf))


if __name__ == '__main__':
    unittest.main()
