import json
import config
import urllib
from datetime import datetime, timedelta
from flask import (
    g,
    Blueprint,
    redirect,
    jsonify,
    request,
    url_for
)


BASE_URL = "http://api.marketstack.com/v1"

marketstack = Blueprint('marketstack', __name__, template_folder='../templates', url_prefix='/marketstack')


def _make_request(path, parameters = dict()):
    params = {'access_key': config.MARKETSTACK_KEY}
    params.update(parameters)
    params = urllib.parse.urlencode(params)
    request = urllib.request.Request(f'{BASE_URL}/{path}?{params}')
    request.add_header("User-Agent", "Mozilla/5.0")
    response = urllib.request.urlopen(request)
    return json.loads(response.read())


@marketstack.route('/exchanges')
def get():
    if not g.user:
        return redirect(url_for('auth.login_get'))

    return jsonify(_make_request('exchanges'))


@marketstack.route('/exchanges/<exchange>/symbols')
def list_exchanges(exchange):
    if not g.user:
        return redirect(url_for('auth.login_get'))

    try:
        offset = int(request.args.get('offset'))
    except (KeyError, TypeError, ValueError):
        offset = 0

    return jsonify(_make_request(f"exchanges/{exchange}/tickers", {'offset': offset}))


@marketstack.route('/exchanges/<exchange>/symbols/<symbol>')
def list_exchange_symbols(exchange, symbol):
    try:
        offset = int(request.args.get('offset'))
    except (KeyError, TypeError, ValueError):
        offset = 0

    return jsonify(_make_request('eod', {
                                 'offset': offset,
                                 'symbols': symbol,
                                 'date_from': (datetime.utcnow() - timedelta(days=30)).strftime(r'%Y-%m-%d'),
                                 'date_to': datetime.utcnow().strftime(r'%Y-%m-%d')
                                }))
