from unittest import TestCase
from time import sleep
from json import loads, dumps
from requests import post
import subprocess


class ApiTest(TestCase):
    """
    Not clearly unit testing but not excessive to test like this.
    Fastest way to complex functionality test.
    """
    def setUp(self):
        self._server = subprocess.Popen(("python", "-m", "CurrencyConvert"))
        sleep(1)

    def test_database_json(self):
        currency_rate = {
            "RUR": 1.0,
            "EUR": 2.0,
            "USD": 3.0,
        }
        data = dumps(currency_rate)
        response = post("http://127.0.0.1:5000/database?format=json&merge=0", data=data)
        self.assertEqual(currency_rate, loads(response.text))

    def test_database_json_merge(self):
        self.test_database_json()
        currency_rate = {
            "RUR": 2.0,
            "USD": 4.0
        }
        currency_rate_2 = {
            "USD": 3.0
        }
        data = dumps(currency_rate)
        post("http://127.0.0.1:5000/database?format=json&merge=0", data=data)
        data = dumps(currency_rate_2)
        response = post("http://127.0.0.1:5000/database?format=json&merge=1", data=data)
        currency_rate.update(currency_rate_2)
        self.assertEqual(currency_rate, loads(response.text))

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
        check_data_xml = '''<?xml version="1.0"?>
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
        response = post("http://127.0.0.1:5000/database?format=xml&merge=0", data=check_data_xml)
        print(response.text)
        self.assertEqual(check_data, loads(response.text))

    def test_persistency(self):
        currency_rate = {
            'RUR': 3.0,
            'EUR': 2.0,
            'USD': 1.0,
        }
        data = dumps(currency_rate)
        response = post("http://127.0.0.1:5000/database?format=json&merge=0", data=data)
        self.tearDown()
        self.setUp()
        self.assertEqual(currency_rate, loads(response.text))

    def tearDown(self):
        self._server.terminate()
        self._server.wait()
