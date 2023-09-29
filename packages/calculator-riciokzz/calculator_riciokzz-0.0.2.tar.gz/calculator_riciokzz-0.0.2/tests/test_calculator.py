import unittest
from ..src.calculator_riciokzz.calculator import Calculator


class TestCalculator(unittest.TestCase):
    def test_functions(self):
        """
        Testing all calculator functions with numbers inputs.
        Creating new instance for all functions. Setting up
        default value in memory which will be used for
        calculations.
        """
        test_add = calculator.Calculator()
        test_add.memory = 5
        test_add.add(5)
        self.assertEqual(test_add.memory, 10)

        test_sub = calculator.Calculator()
        test_sub.memory = 5
        test_sub.sub(2)
        self.assertEqual(test_sub.memory, 3)

        test_multi = calculator.Calculator()
        test_multi.memory = 5
        test_multi.multi(2)
        self.assertEqual(test_multi.memory, 10)

        test_div = calculator.Calculator()
        test_div.memory = 5
        test_div.div(2)
        self.assertEqual(test_div.memory, 2.5)

        test_root = calculator.Calculator()
        test_root.memory = 5
        test_root.root(2)
        self.assertAlmostEqual(test_root.memory, places=3)

    def test_input(self):
        """
        Test for other inputs like strings, list, etc...
        Setting up default value of memory to 5.
        """
        test2 = calculator.Calculator()
        test2.memory = 5

        # Test for a string.
        test2.add("test")
        self.assertEqual(test2.memory, 5)

        # Test for a list.
        test2.sub([12, 14])
        self.assertEqual(test2.memory, 5)

        # Test for a dict.
        test2.multi({"test": 12})
        self.assertEqual(test2.memory, 5)

        # Test for division of 0
        test2.div(0)
        self.assertEqual(test2.memory, 5)

        # Test for negative root.
        test2.root(-1)
        self.assertEqual(test2.memory, 5)


if __name__ == "__main__":
    unittest.main()
