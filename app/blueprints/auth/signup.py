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

    return redirect(url_for('indexes.get_indexes'))
