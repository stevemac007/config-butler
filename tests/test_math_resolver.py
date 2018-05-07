import unittest

from configbutler.resolvers import MathResolver


class TestMathResolver(unittest.TestCase):

    def test_invalid(self):
        undertest = MathResolver()
        self.assertEqual(undertest.resolve(["invalid", "1", "2"], dict), None)

    def test_add(self):
        undertest = MathResolver()
        self.assertEqual(undertest.resolve(["add", "1", "2"], dict), 3.0)

    def test_subtract(self):
        undertest = MathResolver()
        self.assertEqual(undertest.resolve(["subtract", "1", "2"], dict), -1.0)

    def test_multiply(self):
        undertest = MathResolver()
        self.assertEqual(undertest.resolve(["multiply", "36", "2"], dict), 72.0)

    def test_divide(self):
        undertest = MathResolver()
        self.assertEqual(undertest.resolve(["divide", "10", "2"], dict), 5.0)

    # def test_invalid_val1(self):
    #     undertest = MathResolver()
    #
    #     self.assertEqual(undertest.resolve(["add", "one", "2"], dict), 3.0)
