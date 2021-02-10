from hashing import bcrypt
from database import db, User
from flask import (
    Blueprint,
    redirect,
    render_template,
    request,
    flash,
    session,
    url_for
)


auth = Blueprint('auth', __name__, template_folder='../templates')


@auth.route('/login')
def login_get():
    return render_template('login.html')


@auth.route('/login', methods=['POST'])
def login_post():
    session.pop('user_id', None)

    user = User.query.filter_by(username=request.form['username']).first()
    if not user or not bcrypt.check_password_hash(user.password, request.form['password']):
        flash('Invalid credentials')
        return redirect(url_for('auth.login_get'))

    session['user_id'] = user.id
    return redirect(url_for('indexes.get'))


@auth.route('/signup')
def signup_get():
    return render_template('signup.html')


@auth.route('/signup', methods=['POST'])
def signup_post():
    session.pop('user_id', None)

    if (password := request.form['password']) == request.form['checkpassword']:
        pw_hash = bcrypt.generate_password_hash(password)

        user = User(username=request.form['username'],
                    email=request.form['email'],
                    password=pw_hash)
        db.session.add(user)
        db.session.commit()

        session['user_id'] = user.id

    return redirect(url_for('indexes.get'))


@auth.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('auth.login_get'))