from unittest import TestCase
from CurrencyConvert import parse
from werkzeug.exceptions import BadRequest
from json import dumps

class ParseTest(TestCase):

    def test_json(self):
        test_rates = {"RUR": 10, "USD": 10}
        res = parse.from_json(dumps(test_rates))
        self.assertEqual(test_rates, res)

    def test_json_type(self):
        test_rates = {"RUR": 10, "USD": "ab"}
        with self.assertRaises(BadRequest):
            parse.from_json(dumps(test_rates))

    def test_json_bad(self):
        test_rates = {"RUR": 10, "USD": {"key": "value"}}
        with self.assertRaises(BadRequest):
            parse.from_json(dumps(test_rates))

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
        res = parse.from_xml(check_data_xml)
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
            parse.from_xml(check_data_xml)

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
            parse.from_xml(check_data_xml)

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
            parse.from_xml(check_data_xml)

    def test_csv(self):
        check_data = {
            "RUR": 1,
            "CSV": 2,
            "USD": 3
        }
        check_data_csv = 'name,rate\nRUR,1\ncsv,2\nusd,3\n'
        res = parse.from_csv(check_data_csv)
        self.assertEqual(check_data, res)

    def test_csv_missing(self):
        check_data_csv = 'name\nRUR\ncsv\nusd\n'
        with self.assertRaises(BadRequest):
            parse.from_csv(check_data_csv)
        check_data_csv = 'name,rate\nRUR\ncsv,2\nusd,3\n'
        with self.assertRaises(BadRequest):
            parse.from_csv(check_data_csv)

    def test_csv_type(self):
        check_data_csv = 'name,rate\nRUR,RUR\ncsv,2\nusd,3\n'
        with self.assertRaises(BadRequest):
            parse.from_csv(check_data_csv)
