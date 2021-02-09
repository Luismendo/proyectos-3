import config
import blueprints
from app import app
from bcrypt import bcrypt
from database import db, User
from flask import (g, session)


@app.before_request
def before_request():
    if 'user_id' in session:
        g.user = User.query.filter_by(id=session['user_id']).first()
    else:
        g.user = None


if __name__ == '__main__':
    db.init_app(app)
    bcrypt.init_app(app)

    app.register_blueprint(blueprints.auth)
    app.register_blueprint(blueprints.indexes)
    app.register_blueprint(blueprints.noticias)
    app.register_blueprint(blueprints.opiniones)

    app.run(debug=config.DEBUG)
