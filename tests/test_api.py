import CurrencyConvert

from unittest import TestCase, skip
from time import sleep
from json import loads, dumps
from requests import get, post
import subprocess

currency_rate = dict()

# class ConvertTest(TestCase):
#     def test_convert(self):
#         CurrencyConvert.server.convert()


class ApiTest(TestCase):
    def setUp(self):
        self._server = subprocess.Popen(("python","-m","CurrencyConvert"))
        sleep(1)

    def test_database_json(self):
        currency_rate = {
            'RUR': 1.0,
            'EUR': 2.0,
            'USD': 3.0,
        }
        data = dumps(currency_rate)
        response = post("http://127.0.0.1:5000/database?format=json&merge=0", data=data)
        self.assertEqual(currency_rate, loads(response.text))

    # def test_database_json_merge(self):
    #     self.test_database_json()
    #     currency_rate = {
    #         'RUR': 2.0
    #     }
    #     data = dumps(currency_rate)
    #     response = post("http://127.0.0.1:5000/database?format=json&merge=0", data=data)
    #     self.assertEqual(currency_rate, loads(response.text))


    def test_database_csv(self):
        check_data = {
            "RUR": 10,
            "CSV": 20,
            "USD": 30
        }
        check_data_csv = 'name,rate\nRUR,10\ncsv,20\nusd,30\n'
        response = post("http://127.0.0.1:5000/database?format=csv&merge=0", data=check_data_csv)
        self.assertEqual(check_data, loads(response.text))

    def test_database_xml(self):
        check_data = {
            "RUR": 100,
            "USD": 100
        }
        check_data_csv = '''<?xml version="1.0"?>
<data>
	<currency>
		<name>RUR</name>
		<rate>100</rate>
	</currency>
	<currency>
		<name>USD</name>
		<rate>100</rate>
	</currency>
</data>'''
        response = post("http://127.0.0.1:5000/database?format=xml&merge=0", data=check_data_csv)
        print(response.text)
        self.assertEqual(check_data, loads(response.text))

    def tearDown(self):
        self._server.terminate()
        self._server.wait()