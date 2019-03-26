from CurrencyConvert import server

from werkzeug.exceptions import BadRequest

from unittest import TestCase, skip
from time import sleep
from json import loads, dumps
from requests import get, post
import subprocess


class ParseTest(TestCase):

    def test_json(self):
        test_rates = { "RUR": 10, "USD": 10 }
        res = server.parse_from_json(dumps(test_rates))
        self.assertEqual(test_rates, res)

    def test_json_type(self):
        test_rates = {"RUR": 10, "USD": "ab"}
        with self.assertRaises(BadRequest):
            server.parse_from_json(dumps(test_rates))

    def test_json_bad(self):
        test_rates = {"RUR": 10, "USD": { "key": "value"}}
        with self.assertRaises(BadRequest):
            server.parse_from_json(dumps(test_rates))

    def test_xml(self):
        test_rates = {"RUR": 100, "USD": 1000}
        check_data_xml = '''<?xml version="1.0"?>
                            <data>
                                <currency>
                                    <name>RUR</name>
                                    <rate>100</rate>
                                </currency>
                                <currency>
                                    <name>USD</name>
                                    <rate>1000</rate>
                                </currency>
                            </data>'''
        res = server.parse_from_xml(check_data_xml)
        self.assertEqual(test_rates, res)

    def test_xml_type(self):
        check_data_xml = '''<?xml version="1.0"?>
                            <data>
                                <currency>
                                    <name>RUR</name>
                                    <rate>RUR</rate>
                                </currency>
                                <currency>
                                    <name>USD</name>
                                    <rate>100.0</rate>
                                </currency>
                            </data>'''
        with self.assertRaises(BadRequest):
            server.parse_from_xml(check_data_xml)

    def test_xml_miss_value(self):
        check_data_xml = '''<?xml version="1.0"?>
                            <data>
                                <currency>
                                    <name>RUR</name>
                                </currency>
                                <currency>
                                    <name>USD</name>
                                    <rate>100.0</rate>
                                </currency>
                            </data>'''
        with self.assertRaises(BadRequest):
            server.parse_from_xml(check_data_xml)

    def test_xml_bad(self):
        check_data_xml = '''<?xml version="1.0"?>
                            <data>
                                <currency>
                                    <name>RUR</name>
                                    <rate>100.0</rate>
                                <currency>
                                    <name>USD</name>
                                    <rate>100.0</rate>
                                </currency>
                            </data>'''
        with self.assertRaises(BadRequest):
            server.parse_from_xml(check_data_xml)

    def test_csv(self):
        check_data = {
            "RUR": 1,
            "CSV": 2,
            "USD": 3
        }
        check_data_csv = 'name,rate\nRUR,1\ncsv,2\nusd,3\n'
        res = server.parse_from_csv(check_data_csv)
        self.assertEqual(check_data, res)

    def test_csv_missing(self):
        check_data_csv = 'name\nRUR\ncsv\nusd\n'
        with self.assertRaises(BadRequest):
            server.parse_from_csv(check_data_csv)
        check_data_csv = 'name,rate\nRUR\ncsv,2\nusd,3\n'
        with self.assertRaises(BadRequest):
            server.parse_from_csv(check_data_csv)

    def test_csv_type(self):
        check_data_csv = 'name,rate\nRUR,RUR\ncsv,2\nusd,3\n'
        with self.assertRaises(BadRequest):
            server.parse_from_csv(check_data_csv)




class ConvertTest(TestCase):

    def test_convert(self):
        server.currency_rate = {"USD":1,"RUR":10}
        converted = server.convert("RUR","USD",10)
        self.assertEqual(converted, 1.0)




class ApiTest(TestCase):
    """
    Not clearly unit testing but not excessive to test like this.
    Fastest way to complex functionality test.
    """
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

    def tearDown(self):
        self._server.terminate()
        self._server.wait()