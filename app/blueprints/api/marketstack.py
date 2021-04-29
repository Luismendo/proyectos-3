import json
import config
import urllib
from database import Index
from datetime import datetime, timedelta
from flask import (
    g,
    Blueprint,
    redirect,
    jsonify,
    request,
    url_for
)
from werkzeug.exceptions import NotFound
from ..base import api


BASE_URL = "http://api.marketstack.com/v1"


def _make_request(path, parameters=dict()):
    params = {'access_key': config.MARKETSTACK_KEY}
    params.update(parameters)
    params = urllib.parse.urlencode(params)
    request = urllib.request.Request(f'{BASE_URL}/{path}?{params}')
    request.add_header("User-Agent", "Mozilla/5.0")
    try:
        response = urllib.request.urlopen(request)
        return json.loads(response.read())
    except urllib.error.HTTPError:
        raise NotFound('Unable to find results')


@api.route('/exchanges')
def list_exchanges():
    if not g.user:
        return redirect(url_for('auth.login_get'))

    return jsonify(_make_request('exchanges'))


@api.route('/exchanges/<mic>')
def list_tickers(mic):
    try:
        offset = int(request.args.get('offset'))
    except (KeyError, TypeError, ValueError):
        offset = 0

    return jsonify(_make_request(f"exchanges/{mic}/tickers", {'offset': offset, 'limit': 200})) #el limit para la presentacion es de 19


@api.route('/exchanges/<mic>/symbols/<symbol>')
def list_symbol_values(mic, symbol):
    try:
        offset = int(request.args.get('offset'))
    except (KeyError, TypeError, ValueError):
        offset = 0

    return jsonify(_make_request('eod', {
                                 'offset': offset,
                                 'symbols': symbol,
                                 'exchange': mic,
                                 'date_from': (datetime.utcnow() - timedelta(days=365)).strftime(r'%Y-%m-%d'),
                                 'date_to': datetime.utcnow().strftime(r'%Y-%m-%d'),
                                 'limit': 200
                                 }))
