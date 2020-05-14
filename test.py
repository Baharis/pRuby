import unittest
from pruby.utility.line_subset import LineSubset


class TestLineSubset(unittest.TestCase):
    inf = float('inf')

    def test_create_from_pair(self):
        self.assertTrue(LineSubset(1.2, self.inf))

    def test_create_from_list(self):
        self.assertTrue(LineSubset([(-self.inf, -2), (-1, 1), (1.2, self.inf)]))

    def test_create_empty(self):
        self.assertTrue(LineSubset())

    def test_create_incorrect(self):
        with self.assertRaises(ValueError):
            LineSubset(3, 2)

    def test_merging(self):
        self.assertEqual(LineSubset([(0, 1), (1, 2), (2, 3)]), LineSubset(0, 3))

    def test_negation(self):
        self.assertEqual(LineSubset([(-self.inf, -2.2), (3.3, self.inf)]),
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
        self.assertEqual(LineSubset(1.1, 3.3) + LineSubset(2.2, self.inf),
                         LineSubset(1.1, self.inf))

    def test_intersection(self):
        self.assertEqual(LineSubset(-self.inf, 2.2) * LineSubset(1.1, 3.3),
                         LineSubset(1.1, 2.2))

    def test_subtraction(self):
        self.assertEqual(LineSubset(-self.inf, 2.2) - LineSubset(1.1, 3.3),
                         LineSubset(-self.inf, 1.1))

    def test_division(self):
        self.assertEqual(LineSubset(-self.inf, 2.2) / LineSubset(1.1, 3.3),
                         LineSubset([(-self.inf, 1.1), (2.2, 3.3)]))

    def test_representation(self):
        self.assertIn('2.2, inf', repr(LineSubset(2.2, self.inf)))

    def test_string(self):
        self.assertIn('2.2, inf', str(LineSubset(2.2, self.inf)))

    def test_max(self):
        self.assertEqual(max(LineSubset(-self.inf, -2.2)), -2.2)

    def test_iterator(self):
        self.assertEqual(list(LineSubset([(0, 1), (2, 3)])), [0, 1, 2, 3])

    def test_contains_float(self):
        self.assertIn(1.1, LineSubset(1.1, self.inf))

    def test_contains_other(self):
        self.assertIn(LineSubset(1.1, 3.3), LineSubset(1.1, self.inf))


if __name__ == '__main__':
    unittest.main()
