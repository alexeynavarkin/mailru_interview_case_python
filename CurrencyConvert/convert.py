from flask import abort


def convert(currency_rate, cur_from: str, cur_to: str, amount: float) -> float:
    try:
        return currency_rate[cur_to] / currency_rate[cur_from] * amount
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
