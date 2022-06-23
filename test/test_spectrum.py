import unittest
from math import pi, sin
from pruby.spectrum import Curve, Spectrum
from pruby.utility import LineSubset


class TestCurve(unittest.TestCase):
    def test_creation_without_arguments(self):
        self.assertTrue(Curve(lambda x: x ** 2))

    def test_creation_with_arguments(self):
        self.assertTrue(Curve(func=lambda x, a, n: a * x ** n, args=(1.2, 3.4)))

    def test_call_without_arguments(self):
        self.assertAlmostEqual(Curve(lambda x: x ** 2)(pi), 9.8696044011)

    def test_call_with_default_arguments(self):
        self.assertAlmostEqual(Curve(lambda x, a: a * x, (1.2,))(pi),
                               3.7699111843)

    def test_call_with_new_arguments(self):
        self.assertAlmostEqual(Curve(lambda x, a: a * x, (1.2,))(pi, 3.4),
                               10.6814150222)

    def test_call_with_no_arguments(self):
        curve = Curve(lambda x, a: a * x, (1.2,))
        with self.assertRaises(IndexError):
            curve()

    def test_call_with_too_many_arguments(self):
        curve = Curve(lambda x, a: a * x, (1.2,))
        with self.assertRaises(IndexError):
            curve(pi, pi, pi)


class TestSpectrum(unittest.TestCase):
    x = [1.0, 2.0, 3.0]
    y = [1.2, 3.4, 5.6]

    def test_creation_of_empty(self):
        self.assertIsNotNone(Spectrum())

    def test_creation_with_datapoints(self):
        self.assertIsNotNone(Spectrum(self.x, self.y))

    def test_creation_with_custom_curve(self):
        self.assertIsNotNone(Spectrum(self.x, self.y, curve=Curve()))

    def test_creation_with_custom_focus(self):
        self.assertIsNotNone(Spectrum(self.x, self.y, focus=LineSubset()))

    def test_creation_with_equal_sigma_type(self):
        self.assertIsNotNone(Spectrum(self.x, self.y, sigma_type='equal'))

    def test_creation_with_huber_sigma_type(self):
        self.assertIsNotNone(Spectrum(self.x, self.y, sigma_type='huber'))

    def test_length(self):
        self.assertEqual(len(Spectrum(self.x, self.y)), 3)

    def test_true_if_has_datapoints(self):
        self.assertTrue(Spectrum(self.x, self.y))

    def test_false_if_empty(self):
        self.assertFalse(Spectrum())

    def test_f(self):
        self.assertAlmostEqual(
            sum(Spectrum(self.x, self.y, curve=Curve(lambda x: x)).f), 6.0)

    def test_delta(self):
        self.assertAlmostEqual(
            sum(Spectrum(self.x, self.y, curve=Curve(lambda x: x)).delta), 4.2)

    def test_si_equal(self):
        self.assertAlmostEqual(
            sum(Spectrum(self.x, self.y, curve=Curve(lambda x: x)).si), 3.0)

    def test_si_huber(self):
        self.assertAlmostEqual(1.132992,
            sum(Spectrum(self.x, self.y, sigma_type='huber').si))

    def test_si_unknown(self):
        with self.assertRaises(ValueError):
            _ = Spectrum(self.x, self.y, sigma_type='nonexistent sigma type').si

    def test_mse(self):
        self.assertAlmostEqual(
            Spectrum(self.x, self.y, curve=Curve(lambda x: x)).mse, 2.92)

    def test_domain(self):
        self.assertEqual(Spectrum(self.x, self.y).domain, LineSubset(1.0, 3.0))

    def test_focused(self):
        self.assertAlmostEqual(4.6,
            sum(Spectrum(self.x, self.y, focus=LineSubset(0.5, 2.5)).focused.y))

    def test_within(self):
        self.assertAlmostEqual(
            sum(Spectrum(self.x, self.y).within(LineSubset(0.5, 2.5)).y), 4.6)

    def test_focus_on_edge(self):
        spectrum = Spectrum(self.x, self.y)
        spectrum.focus_on_edge(width=0.5)
        self.assertAlmostEqual(sum(spectrum.focused.y), 6.8)

    def test_focus_on_whole(self):
        spectrum = Spectrum(self.x, self.y)
        spectrum.focus_on_whole()
        self.assertAlmostEqual(sum(spectrum.focused.y), 10.2)

    def test_focus_on_points(self):
        spectrum = Spectrum(self.x, self.y)
        spectrum.focus_on_points(points=(2.0,), width=1.5)
        self.assertAlmostEqual(sum(spectrum.focused.y), 3.4)


if __name__ == '__main__':
    unittest.main()
