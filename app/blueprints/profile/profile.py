from flask import (
    g,
    redirect,
    render_template,
    url_for
)
from ..base import profile


@profile.route('/')
def get_profile():
    if not g.user:
        return redirect(url_for('auth.login_get'))

    return render_template('profile.html')
