from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "Users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255))
    email = db.Column(db.String(255))
    password = db.Column(db.String(255))


class Index(db.Model):
    __tablename__ = "Indexes"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    value = db.Column(db.Float)
    variation = db.Column(db.Float)
    date = db.Column(db.Date)


class Opinion(db.Model):
    __tablename__ = "Opinions"
    id = db.Column(db.Integer, primary_key=True)
    company = db.Column(db.String(50))
    title = db.Column(db.String(200))
    body = db.Column(db.String(500))
    page = db.Column(db.Text())


class Noticias(db.Model):
    __tablename__ = "Noticias"
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(255))
    cuerpo = db.Column(db.Text())
    url = db.Column(db.String(255))
