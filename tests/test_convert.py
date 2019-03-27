from unittest import TestCase

from CurrencyConvert import convert
from werkzeug.exceptions import BadRequest


class ConvertTest(TestCase):

    def test_convert(self):
        currency_rate = {"USD": 1, "RUR": 10}
        converted = convert.convert(currency_rate, "RUR", "USD", 10)
        self.assertEqual(converted, 1.0)

    def test_convert_zero_division(self):
        currency_rate = {"USD": 10, "RUR": 0}
        with self.assertRaises(BadRequest):
            convert.convert(currency_rate, "RUR", "USD", 10)

    def test_convert_no_cur(self):
        currency_rate = {"USD": 10, "RUR": 0}
        with self.assertRaises(BadRequest):
            convert.convert(currency_rate, "RUR", "YEN", 10)
