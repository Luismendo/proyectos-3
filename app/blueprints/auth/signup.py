from hashing import bcrypt
from database import db, User
from flask import (
    redirect,
    render_template,
    request,
    session,
    url_for
)
from ..base import auth
from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField

class RegisterForm(FlaskForm):
    email = StringField('Email')
    username = StringField('Username')
    password = PasswordField('Password')
    checkpassword = PasswordField('Confirm Password')

@auth.route('/signup')
def signup_get():
    form = RegisterForm()
    return render_template('signup.html',form=form)


@auth.route('/signup', methods=['POST'])
def signup_post():
    session.pop('user_id', None)

    form = RegisterForm()
    if (password := form.password.data) == form.checkpassword.data:
        pw_hash = bcrypt.generate_password_hash(password)

        user = User(username=form.username.data,
                    email=form.email.data,
                    password=pw_hash)
        db.session.add(user)
        db.session.commit()

        session['user_id'] = user.id

    return redirect(url_for('indexes.get_indexes'))
