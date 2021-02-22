from hashing import bcrypt
from database import db, User
from flask import (
    redirect,
    request,
    session,
    url_for,
    render_template
)
from ..base import auth


@auth.route('/login')
def login_get():
    return render_template('login.html')


@auth.route('/login', methods=['POST'])
def login_post():
    session.pop('user_id', None)

    user = User.query.filter_by(username=request.form['username']).first()
    if not user or not bcrypt.check_password_hash(user.password, request.form['password']):
        return redirect(url_for('auth.login_get'))

    session['user_id'] = user.id
    return redirect(url_for('indexes.get_indexes'))


@auth.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('auth.login_get'))
