from flask import abort


def currency_rate_update(update: dict) -> dict:
    """
    Here can be implemented logic for validating dict data
    before committing it.

    e.g. check currency in accept list, values ranges etc.
    :param update: currency rates update values
    :return: validated update
    """
    for name, rate in update.items():
        if rate == 0:
            abort(400, "Currency rate can not be zero.")
        if rate < 0:
            abort(400, "Currency rate can not be greater than zero.")
    return update