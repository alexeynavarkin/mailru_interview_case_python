from flask import abort

from csv import DictReader
from xml.etree import ElementTree
import json


def from_json(data: str) -> dict:
    currency_rate_update = dict()
    try:
        data = json.loads(data)
        for key, value in data.items():
            currency_rate_update.update({key.upper(): float(value)})
    except json.JSONDecodeError:
        abort(400, "Error parsing json.")
    except (TypeError, ValueError):
        abort(400, "Error, check values.")
    return currency_rate_update


def from_xml(data: str) -> dict:
    currency_rate_update = dict()
    try:
        root = ElementTree.fromstring(data)
        for currency in root.iter('currency'):
            name = currency.find('name')
            rate = currency.find('rate')
            if name is None or rate is None:
                abort(400, "Error, check values.")
            name = name.text.upper()
            rate = float(rate.text)
            currency_rate_update.update({name: rate})
    except ElementTree.ParseError:
        abort(400, "Error parsing XML.")
    except ValueError:
        abort(400, "Error parsing rate value.")
    return currency_rate_update


def from_csv(data: str) -> dict:
    currency_rate_update = dict()
    try:
        csv_reader = DictReader(data.splitlines())
        for line in csv_reader:
            rate = float(line['rate'])
            name = line['name'].upper()
            currency_rate_update.update({name: rate})
    except ValueError:
        abort(400, "Error parsing CSV.")
    except (KeyError, TypeError):
        abort(400, "Wrong values in data provided.")
    return currency_rate_update
