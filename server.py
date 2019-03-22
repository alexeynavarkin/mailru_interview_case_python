from flask import Flask, request, abort, Response, jsonify
from time import monotonic_ns

import pickle
from os.path import join
from os import listdir

from csv import DictReader
from xml.etree import ElementTree
import json

import logging

import settings


"""
Currency rate relative to base currency (direct quotation),
it's rate should be 1.

Other currencies calculated by cross rate.
"""
currency_rate = settings.currency_rates


def backup_currency_rate():
    global currency_rate
    backup_file = '.'.join([str(monotonic_ns()), 'bkp'])
    backup_file = join(settings.backup_path, backup_file)
    with open(backup_file, "wb") as backup_file:
        pickle.dump(currency_rate, backup_file)


def restore_currency_rate():
    global currency_rate
    backups = listdir(settings.backup_path)
    if backups:
        logging.warning("Found backup files, remove them to run clean instance.")
        backups.sort(reverse=True)
        backup_file_name = join(settings.backup_path, backups[0])
        with open(backup_file_name, 'rb') as backup_file:
            currency_rate = pickle.load(backup_file)


def parse_from_json(data: str) -> dict:
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


def parse_from_xml(data: str) -> dict:
    currency_rate_update = dict()
    try:
        root = ElementTree.fromstring(data)
        for currency in root.iter('currency'):
            name = currency.find('name').text.upper()
            rate = float(currency.find('rate').text)
            if name and rate:
                currency_rate_update.update({name: rate})
            else:
                abort(400, "Error, check values.")
    except ElementTree.ParseError:
        abort(400, "Error parsing XML.")
    except ValueError:
        abort(400, "Error parsing rate value.")
    return currency_rate_update


def parse_from_csv(data: str) -> dict:
    currency_rate_update = dict()
    try:
        csv_reader = DictReader(data.splitlines())
        for line in csv_reader:
            rate = float(line['rate'])
            name = line['name'].upper()
            currency_rate_update.update({name: rate})
    except ValueError:
        abort(400, "Error parsing CSV.")
    except KeyError:
        abort(400, "Wrong values in data provided.")
    return currency_rate_update


def load_data(data: str, data_format: str, merge=True):
    global currency_rate
    currency_rate_update = dict()
    if data_format == 'json':
        currency_rate_update = parse_from_json(data)
    elif data_format == 'xml':
        currency_rate_update = parse_from_xml(data)
    elif data_format == 'csv':
        currency_rate_update = parse_from_csv(data)
    else:
        abort(400, "Format you specified not supported.")
    if merge:
        currency_rate.update(currency_rate_update)
    else:
        currency_rate = currency_rate_update
    backup_currency_rate()


def create_app() -> Flask:
    """
    For initializations before app run.
        Searches for snapshots in backup folder specified in settings.py
    :return: flask.app instance
    """
    app = Flask(__name__)
    restore_currency_rate()

    @app.route('/convert', methods=['GET'])
    def convert():
        global currency_rate
        try:
            con_from = str(request.args['from'])
            con_to = str(request.args['to'])
            amount = float(request.args['amount'])
            converted = currency_rate[con_to] / currency_rate[con_from] * amount
        except KeyError:
            abort(
                400,
                "Looks like we don't know currency you specified\
                or some arguments are missing."
            )
        except ValueError:
            abort(
                400,
                "Looks like amount to convert is invalid."
            )
        except ZeroDivisionError:
            abort(
                500,
                "Looks like value rates db invalid."
            )
        else:
            resp = Response('{{"amount": {:.2f}}}'.format(converted))
            resp.headers['Content-Type'] = 'application/json'
            return resp

    @app.route('/database', methods=['POST'])
    def database():
        global currency_rate
        try:
            data_format = str(request.args['format'])
            merge = bool(int(request.args['merge']))
        except KeyError:
            abort(
                400,
                "Looks like your request missing required values."
            )
        except ValueError:
            abort(
                400,
                "Looks like your request have wrong values."
            )
        else:
            data = request.data
            load_data(data.decode('utf8'), data_format, merge)
        return jsonify(currency_rate)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
