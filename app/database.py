# import flask
# import config
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import UniqueConstraint, DateTime
from datetime import datetime, timedelta
from sqlalchemy.dialects.mysql import BIGINT, FLOAT, DOUBLE
import json
from json import JSONEncoder

# app = flask.Flask(__name__)
# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+mysqlconnector://{config.DB_USER}:{config.DB_PASS}@" \
#                                         f"{config.DB_HOST}/{config.DB_DATABASE}"
# db = SQLAlchemy(app)

db = SQLAlchemy()


class Favourite(db.Model):
    __tablename__ = 'favourite_indexes'
    __table_args__ = {'mysql_engine': 'InnoDB'}
    id = db.Column(BIGINT(unsigned=True), primary_key=True)
    user_id = db.Column(BIGINT(unsigned=True), nullable=False)
    index_id = db.Column(BIGINT(unsigned=True), nullable=False)


class User(db.Model):
    __tablename__ = 'users'
    __table_args__ = {'mysql_engine': 'InnoDB'}
    id = db.Column(BIGINT(unsigned=True), primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(190), nullable=False)
    password = db.Column(db.Text(), nullable=False)
    money = db.Column(DOUBLE)


class Index(db.Model):
    __tablename__ = 'indexes'
    __table_args__ = {'mysql_engine': 'InnoDB'}
    id = db.Column(BIGINT(unsigned=True), primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    mic = db.Column(db.String(10), nullable=True)


class Value(db.Model):
    __tablename__ = 'values'
    __table_args__ = {'mysql_engine': 'InnoDB'}
    id = db.Column(BIGINT(unsigned=True), primary_key=True)
    index_id = db.Column(BIGINT(unsigned=True), db.ForeignKey('indexes.id'), nullable=False)
    value = db.Column(FLOAT(precision=10, scale=3), nullable=False)
    variation = db.Column(FLOAT(precision=10, scale=3), nullable=True)
    timestamp = db.Column(db.DateTime(), nullable=False)

    index = db.relationship('Index', backref=db.backref(__tablename__, lazy=True))


class Opinion(db.Model):
    __tablename__ = 'opinions'
    __table_args__ = {'mysql_engine': 'InnoDB'}
    id = db.Column(BIGINT(unsigned=True), primary_key=True)
    index_id = db.Column(BIGINT(unsigned=True), db.ForeignKey('indexes.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    body = db.Column(db.Text(), nullable=False)
    url = db.Column(db.Text(), nullable=False)

    index = db.relationship('Index', backref=db.backref(__tablename__, lazy=True))


class Article(db.Model):
    __tablename__ = 'articles'
    __table_args__ = {'mysql_engine': 'InnoDB'}
    id = db.Column(BIGINT(unsigned=True), primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    body = db.Column(db.Text(), nullable=False)
    url = db.Column(db.Text(), nullable=False)


class Transactions(db.Model):
    __tablename__ = 'transactions'
    __table_args__ = {'mysql_engine': 'InnoDB'}
    id = db.Column(BIGINT(unsigned=True), primary_key=True)
    amount = db.Column(DOUBLE, nullable=False)
    idx_id = db.Column(db.String(10), nullable=False)
    user_id = db.Column(BIGINT(unsigned=True),  db.ForeignKey('users.id'), nullable=False)
    value = db.Column(DOUBLE, nullable=False)
    quantity = db.Column(DOUBLE, nullable=False)
    fecha = db.Column(DateTime, default=datetime.utcnow)
    operation = db.Column(BIGINT(unsigned=True), nullable=False)
    bolsa_id = db.Column(db.String(10), nullable=False)

    user = db.relationship('User', backref=db.backref(__tablename__, lazy=True))


class Avisos(db.Model):
    __tablename__ = 'avisos'
    __table_args__ = {'mysql_engine': 'InnoDB'}
    id = db.Column(BIGINT(unsigned=True), primary_key=True)
    valor = db.Column(DOUBLE, nullable=False)
    aviso = db.Column(BIGINT(unsigned=True), nullable=False)
    user_id = db.Column(BIGINT(unsigned=True),  db.ForeignKey('users.id'), nullable=False)
    idx_id = db.Column(db.String(10), nullable=False)

    user = db.relationship('User', backref=db.backref(__tablename__, lazy=True))


# subclass JSONEncoder
class EmployeeEncoder(JSONEncoder):
        def default(self, o):
            return o._asdict
