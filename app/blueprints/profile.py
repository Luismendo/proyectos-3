import urllib
from bs4 import BeautifulSoup
from database import db, Opinion
from flask import (
    g,
    Blueprint,
    redirect,
    render_template,
    jsonify,
    request,
    flash,
    session,
    url_for
)


profile = Blueprint('profile', __name__, template_folder='../templates')


@profile.route('/profile')
def get():
    if not g.user:
        return redirect(url_for('login_get'))

    return render_template('profile.html')
