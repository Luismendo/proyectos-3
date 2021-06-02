from hashing import bcrypt
from database import db, User
from flask import (
    redirect,
    render_template,
    request,
    session,
    url_for,
    flash
)
from ..base import auth
from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField

class RegisterForm(FlaskForm):
    email = StringField('Email')
    username = StringField('Username')
    password = PasswordField('Password')
    checkpassword = PasswordField('Confirm Password')

def _signup_error(message):
    flash(message)
    return redirect(url_for('auth.signup_get'))

@auth.route('/signup')
def signup_get():
    form = RegisterForm()
    return render_template('signup.html',form=form)

@auth.route('/signup', methods=['POST'])
def signup_post():
    session.pop('user_id', None)

    form = RegisterForm()

    # Validate username
    username = form.username.data.strip()
    if len(username) < 5:
        return _signup_error("Username must be at least 5 characters.")
    elif not username.isalnum():
        return _signup_error("Username must be made of alphanumeric characters only.")

    # Validate password
    password = form.password.data
    password_check = form.checkpassword.data
    if len(password) < 8 or password != password_check:
        return _signup_error("Password must be at least 8 characters")

    # Validate email
    email = form.email.data.strip()
    email_parts = email.split("@")
    email_valid = False
    if len(email_parts) == 2:
        email_domain = email_parts.pop()
        email_parts.extend(email_domain.split("."))
        if len(email_parts) == 3 and\
           all(True for part in email_parts if part.isalnum() and len(part.strip()) > 0):
            email_valid = True
    if not email_valid:
        return _signup_error("Email is invalid")

    # Check username isn't already in use
    user = User.query.filter_by(username=form.username.data).first()
    if user is not None:
        return _signup_error("Username is already in use")

    # Create user
    pw_hash = bcrypt.generate_password_hash(password)
    user = User(username=username, email=email,
                password=pw_hash, money=100000)
    db.session.add(user)
    db.session.commit()

    session['user_id'] = user.id

    return redirect(url_for('indexes.get_indexes'))
