from flask import Flask, request, abort, Response, jsonify

from time import monotonic_ns

import pickle
from os.path import join, exists
from os import listdir, makedirs

from csv import DictReader
from xml.etree import ElementTree
import json


"""
Currency rate relative to base currency (direct quotation),
it's rate should be 1.

Other currencies calculated by cross rate.
"""
currency_rate = dict()
# Or we can use singleton dict by meta or module instead of global variable
# from .singleton import SingletonMeta
# class SingleDict(dict, metaclass=SingletonMeta): pass


def perform_backup(backup_folder_path: str):
    """
    Backups currency rates dict to filesystem folder specified in settings.py
    """
    global currency_rate
    if not exists(backup_folder_path):
        makedirs(backup_folder_path)
    backup_file = '.'.join([str(monotonic_ns()), 'bkp'])
    backup_file = join(backup_folder_path, backup_file)
    with open(backup_file, "wb") as backup_file:
        pickle.dump(currency_rate, backup_file)


def load_backup(backup_file_path: str) -> dict:
    """
    Loads currency rate dict from data stored in backup_file_path
    :param backup_file_path: path to file restore from
    """
    global currency_rate
    with open(backup_file_path, 'rb') as backup_file:
        return pickle.load(backup_file)


def find_latest_backup(backup_folder_path: str) -> str:
    """
    Find backup files in path specified path and
    :return: backup_file_path
    """
    # if not exists(app.config['backup_path']):
    #     return ""
    if not exists(backup_folder_path):
        return ""
    backups = listdir(backup_folder_path)
    if not backups:
        return ""
    backups.sort(reverse=True)
    return join(backup_folder_path, backups[0])


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
    except (KeyError, TypeError):
        abort(400, "Wrong values in data provided.")
    return currency_rate_update


def validate_currency_rate_update(update: dict) -> dict:
    """
    Here can be implemented logic for validating dict data
    before committing it.

    e.g. check currency in accept list, values ranges etc.
    :param update: currency rates update values
    :return:
    """
    for rate, name in update.items():
        if rate == 0:
            abort(400, "Currency rate can not be zero value.")

    return update


def update_currency_rate(data: str, data_format: str, merge=True):
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

    currency_rate_update = validate_currency_rate_update(currency_rate_update)

    if merge:
        currency_rate.update(currency_rate_update)
    else:
        currency_rate = currency_rate_update


def convert(cur_from: str, cur_to: str, amount: float) -> float:
    return currency_rate[cur_to] / currency_rate[cur_from] * amount


def create_app() -> Flask:
    """
    For initializations before app run.
    Searches for snapshots in backup folder specified in settings.py
    :return: flask.app instance
    """
    global currency_rate

    app = Flask(__name__)
    app.config.from_pyfile("config.py")
    backup_file_path = find_latest_backup(app.config['BACKUP_PATH'])
    if backup_file_path:
        app.logger.info("Found backup snapshot, trying to restore.")
        currency_rate = load_backup(backup_file_path)
        app.logger.info(f"Restored from: {backup_file_path}.")
        app.logger.info(currency_rate)

    @app.route('/convert', methods=['GET'])
    def handle_convert():
        global currency_rate

        cur_from = request.args.get('from')
        cur_to = request.args.get('to')
        amount = request.args.get('amount')

        if not cur_from:
            abort(400)
        elif not cur_to:
            abort(400)
        elif not amount:
            abort(400)

        try:
            cur_from = str(cur_from).upper()
            cur_to = str(cur_to).upper()
            amount = float(amount)
        except ValueError:
            abort(400, "Wrong argument type.")

        try:
            converted = convert(cur_from, cur_to, amount)
        except KeyError:
            abort(
                400,
                "No rate info about currency you specified."
            )
        except ZeroDivisionError:
            abort(
                400,
                "Looks like value rates db invalid. Currency rate can not be zero."
            )
        else:
            resp = Response('{{"amount": {:.2f}}}'.format(converted))
            resp.headers['Content-Type'] = 'application/json'
            return resp

    @app.route('/database', methods=['POST'])
    def handle_database():
        data_format = request.args.get('format')
        merge = request.args.get('merge')

        if not data_format:
            abort(400)
        elif not merge:
            # Or set to default value
            # merge = 0
            abort(400)

        try:
            data_format = str(data_format)
            merge = bool(int(merge))
        except ValueError:
            abort(
                400,
                "Looks like your request has wrong values."
            )
        else:
            data = request.data
            update_currency_rate(data.decode('utf8'), data_format, merge)
            perform_backup(app.config["BACKUP_PATH"])
        return jsonify(currency_rate)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run()
