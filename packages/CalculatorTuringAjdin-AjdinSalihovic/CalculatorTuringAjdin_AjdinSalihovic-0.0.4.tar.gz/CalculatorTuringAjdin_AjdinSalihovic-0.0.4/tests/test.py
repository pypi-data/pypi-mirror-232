import unittest
import sys

#System path to make sure we are working with the module created
sys.path.insert(0, '../src')
from CalculatorTuringAjdin import calculator


class TestCalculator(unittest.TestCase):
    def setUp(self):
        self.calculator = calculator()

    # Testing the addition
    def test_addition(self):
        result = self.calculator.add(5.0, 3.0)
        self.assertEqual(result, 8.0)

    # Testing the subtraction
    def test_subtraction(self):
        result = self.calculator.subtract(10.0, 4.0)
        self.assertEqual(result, 6.0)

    # Testing the multiplication
    def test_multiplication(self):
        result = self.calculator.multiply(7.0, 2.0)
        self.assertEqual(result, 14.0)

    # Testing the division
    def test_division(self):
        result = self.calculator.divide(8.0, 2.0)
        self.assertEqual(result, 4.0)

    # Testing the nRoot
    def test_nRoot(self):
        result = self.calculator.n_root(16.0, 2.0)
        self.assertEqual(result, 4.0)

if __name__ == '__main__':
    unittest.main()
