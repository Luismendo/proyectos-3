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
    url_for,
    render_template
)
from werkzeug.exceptions import NotFound
from ..base import businesses

@businesses.route('/')
def get_businesses():
    return render_template('business.html')
