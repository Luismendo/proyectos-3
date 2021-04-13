from flask import Flask
from flask_bootstrap import Bootstrap
import config


app = Flask(__name__)
app.secret_key = config.APP_SECRET
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+mysqlconnector://{config.DB_USER}:{config.DB_PASS}@" \
                                        f"{config.DB_HOST}/{config.DB_DATABASE}"
Bootstrap(app)
