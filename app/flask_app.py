import config
from blueprints import base
from app import app
from hashing import bcrypt
from database import db, User
from flask import (g, session)


db.init_app(app)
bcrypt.init_app(app)

app.register_blueprint(base.root)

app.register_blueprint(base.api)
app.register_blueprint(base.articles)
app.register_blueprint(base.auth)
app.register_blueprint(base.exchanges)
app.register_blueprint(base.indexes)
#app.register_blueprint(base.marketstack)
app.register_blueprint(base.profile)


@app.before_request
def before_request():
    if 'user_id' in session:
        g.user = User.query.filter_by(id=session['user_id']).first()
    else:
        g.user = None


if __name__ == '__main__':
    app.run(debug=config.DEBUG)
