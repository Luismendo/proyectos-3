from ..base import profile
from flask import render_template

@profile.route('/favourites')
def get_favourites():
    return render_template('favourites.html')