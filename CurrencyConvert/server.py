from flask import Flask, request, abort, Response, jsonify


from . import backup
from . import parse
from . import validate
from . import convert

"""
Currency rate relative to base currency (direct quotation),
it's rate should be 1.

Other currencies calculated by cross rate.
"""
# Safe in threading mode because of GIL,
# but for multiprocessing mode DB should be used or sync between processes on POST
currency_rate = dict()
# Or we can use singleton dict by meta or module instead of global variable
# from .singleton import SingletonMeta
# class SingleDict(dict, metaclass=SingletonMeta): pass


def currency_rate_update(data: str, data_format: str, merge=True):
    global currency_rate
    currency_rate_update = dict()
    if data_format == 'json':
        currency_rate_update = parse.from_json(data)
    elif data_format == 'xml':
        currency_rate_update = parse.from_xml(data)
    elif data_format == 'csv':
        currency_rate_update = parse.from_csv(data)
    else:
        abort(400, "Format you specified not supported.")

    currency_rate_update = validate.currency_rate_update(currency_rate_update)

    if merge:
        currency_rate.update(currency_rate_update)
    else:
        currency_rate = currency_rate_update


def create_app() -> Flask:
    """
    For initializations before app run.
    Searches for snapshots in backup folder specified in settings.py
    :return: flask.app instance
    """
    global currency_rate
    app = Flask(__name__)
    app.config.from_pyfile("config.py")
    backup_file_path = backup.find_latest(app.config['BACKUP_PATH'])
    if backup_file_path:
        app.logger.info("Found backup snapshot, trying to restore.")
        currency_rate = backup.load(backup_file_path)
        app.logger.info(f"Restored from: {backup_file_path}.")
        app.logger.info(currency_rate)

    @app.route('/convert', methods=['GET'])
    def handle_convert():
        global currency_rate

        cur_from = request.args.get('from')
        cur_to = request.args.get('to')
        amount = request.args.get('amount')

        if not cur_from:
            abort(400, "No from parameter specified.")
        elif not cur_to:
            abort(400, "No to parameter specified.")
        elif not amount:
            abort(400, "No amount parameter specified.")

        try:
            cur_from = str(cur_from).upper()
            cur_to = str(cur_to).upper()
            amount = float(amount)
        except ValueError:
            abort(400, "Wrong argument type.")

        converted = convert.convert(currency_rate, cur_from, cur_to, amount)
        resp = Response('{{"amount": {:.2f}}}'.format(converted))
        resp.headers['Content-Type'] = 'application/json'
        return resp

    @app.route('/database', methods=['POST']) # PUT?
    def handle_database():
        data_format = request.args.get('format')
        merge = request.args.get('merge')

        if not data_format:
            abort(400, "No format parameter specified.")
        elif not merge:
            # Or set to default value
            # merge = 0
            abort(400, "No merge parameter specified.")

        try:
            data_format = str(data_format)
            merge = bool(int(merge))
        except ValueError:
            abort(
                400, "Looks like your request has wrong values.")
        else:
            data = request.data
            currency_rate_update(data.decode('utf8'), data_format, merge)
            backup.perform(app.config["BACKUP_PATH"], currency_rate)
        return jsonify(currency_rate)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(threaded=True)
