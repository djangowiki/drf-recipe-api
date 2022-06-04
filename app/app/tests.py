""" Simple test """

from django.test import SimpleTestCase

from app import calc


class CalcTests(SimpleTestCase):
    """Test the calc module"""

    def test_add_two_numbers(self):
        """Test adding two numbers"""
        res = calc.add(5, 6)

        self.assertEqual(res, 11)

    def test_subtract_two_numbers(self):
        """Test subtracting two numbers"""
        res = calc.subtract(15, 10)
        self.assertEqual(res, 5)
