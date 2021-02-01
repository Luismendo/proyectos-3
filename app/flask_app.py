from flask import (
    Flask,
    g,
    redirect,
    render_template,
    request,
    flash,
    session,
    url_for
)
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from bs4 import BeautifulSoup
from datetime import date
import config
import urllib


app = Flask(__name__)
app.secret_key = 'super secret key'
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+mysqlconnector://{config.DB_USER}:{config.DB_PASS}@" \
                                        f"{config.DB_HOST}/{config.DB_DATABASE}"
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)


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


@app.before_request
def before_request():
    g.user = db.session.query(User) \
               .filter(User.id == session['user_id']) \
               .first() if 'user_id' in session else None


@app.route('/', methods=['GET'])
def index():
    if not g.user:
        return redirect(url_for('login_get'))

    all_idxs = db.session.query(Index) \
                 .filter(Index.date == date.today()) \
                 .all()
    db.session.commit()

    max_idx = None
    labels, values, urls = [], [], []
    if len(all_idxs) > 0:
        avg = sum(map(lambda idx: idx.value, all_idxs)) / len(all_idxs)
        for index in all_idxs:
            if index.value > avg:
                continue
            elif max_idx is None or index.value > max_idx:
                max_idx = index.value
            labels.append(index.name)
            values.append(index.value)
            urls.append('https://www.example.com')

    return render_template('index.html', max=max_idx, labels=labels, values=values, urls=urls)


@app.route('/login', methods=['GET'])
def login_get():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login_post():
    session.pop('user_id', None)

    user = db.session.query(User) \
             .filter(User.username == request.form['username']) \
             .first()

    if not user or not bcrypt.check_password_hash(user.password, request.form['password']):
        flash('Invalid credentials')
        return redirect(url_for('login_get'))

    session['user_id'] = user.id
    return redirect(url_for('index'))


@app.route('/signup', methods=['GET'])
def signup_get():
    return render_template('signup.html')


@app.route('/signup', methods=['POST'])
def signup_post():
    session.pop('user_id', None)

    password = request.form['password']
    check_password = request.form['checkpassword']
    if password == check_password:
        pw_hash = bcrypt.generate_password_hash(password)

        user = User(username=request.form['username'],
                    email=request.form['email'],
                    password=pw_hash)
        db.session.add(user)
        db.session.commit()

        session['user_id'] = user.id

    return redirect(url_for('index'))


@app.route('/logout', methods=['GET'])
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login_get'))


@app.route('/noticias', methods=['GET'])
def noticias_get():
    if not g.user:
        return redirect(url_for('login_get'))

    titulo, cuerpo, url = [], [], []
    all_noticias = db.session.query(Noticias).all()
    for noticias in all_noticias:
        titulo.append(noticias.titulo)
        cuerpo.append(noticias.cuerpo)
        url.append(noticias.url)

    return render_template('noticias.html', titulo=titulo, cuerpo=cuerpo, url=url)


@app.route('/noticias/update', methods=['GET'])
def noticias_update():
    db.session.query(Noticias).delete()

    request = urllib.request.Request('https://es.investing.com/news/stock-market-news')
    request.add_header("User-Agent", "Mozilla/5.0")
    response = urllib.request.urlopen(request)

    soup = BeautifulSoup(response.read(), "html5lib")
    tabla = soup.find('section', attrs={'id': 'leftColumn'})  # id seccion

    cuerpo1 = ""
    titulo1 = ""
    cuerpo = ""
    titulo = ""
    url = ""

    for fila in tabla.find_all("article"):
        if fila.get("class")[1] != "dfp-native":
            cuerpo1 = fila.find('p')
            cuerpo = cuerpo1.text
            cuerpo = cuerpo.rstrip()
            cuerpo = cuerpo.replace("\n", " ")

            titulo1 = fila.find('a', attrs={'class': 'title'})
            titulo = titulo1.text
            if "https" in titulo1.get("href"):
                url = titulo1.get("href")

            else:
                url = "https://es.investing.com"+titulo1.get("href")

            try:
                noticias = Noticias(titulo=titulo, cuerpo=cuerpo, url=url)
                db.session.add(noticias)
            except ValueError:
                pass
    db.session.commit()

    return redirect(url_for('noticias_get'))


@app.route('/update_Noticias', methods=['GET'])
def noticias_update_legacy():
    return redirect(url_for('noticias_update'))


@app.route('/opiniones', methods=['GET'])
def opinions_get():
    index = request.args.get('index')
    if not index:
        return redirect(url_for('index'))

    opinions = db.session.query(Opinion) \
                 .filter(Opinion.company == index) \
                 .all()

    return render_template('opiniones.html', index=index, opinions=opinions)


@app.route('/opiniones/update', methods=['GET'])
def opinions_update():
    db.session.query(Opinion).delete()

    def opiniones(name):
        name = name.replace(" [+]", "")
        query_string = urllib.parse.urlencode({"q": name})

        request = urllib.request.Request(f'https://es.investing.com/search/?{query_string}')
        request.add_header("User-Agent", "Mozilla/5.0")
        response = urllib.request.urlopen(request)

        soup = BeautifulSoup(response.read(), "html5lib")
        link = soup.find("a", class_="js-inner-all-results-quote-item row") \
                   .get('href')

        request = urllib.request.Request(f'https://es.investing.com{link}-opinion')
        request.add_header("User-Agent", "Mozilla/5.0")
        response = urllib.request.urlopen(request)

        soup = BeautifulSoup(response.read(), "html5lib")
        tabla = soup.find('section')  # id seccion

        n = 0
        title, href = "", ""
        for fila in tabla.find_all("article"):
            if n < 3:
                title = fila.find('a', attrs={'class': 'title'}).text
                bodys = fila.find("p").text
                href = fila.find("a").get("href")
                print("Titulo: ", title)
                print("Cuerpo: ", name)
                if "https" in href:
                    print("Dirección: ", href)
                else:
                    href = "https://es.investing.com"+href

                if title:
                    try:
                        index = Opinion(company=name, title=title, body=bodys, page=href)
                        db.session.add(index)
                        db.session.commit()
                    except ValueError as e:
                        print(f"{e}")
                n += 1

    page = urllib.request.urlopen('https://datosmacro.expansion.com/bolsa').read()

    soup = BeautifulSoup(page, "html5lib")
    tabla = soup.find('table', attrs={'id': 'tb1_1139'})  # id tabla
    tabla_WhereTr = soup.find('tbody')

    nroFila = 0
    name, price = "", ""
    for fila in tabla_WhereTr.find_all("tr"):
        nroCelda = 0
        for celda in fila.find_all('td'):
            if nroCelda == 0:
                name = celda.text
                print(f"Indice: {name}")
            elif nroCelda == 2:
                price = celda.text
            elif nroCelda == 3:
                change = celda.text
                try:
                    print("Calling opiniones")
                    opiniones(name)
                    print("Called opiniones")
                except Exception as ex:
                    print(f"{ex}")
            nroCelda += 1
    return redirect(url_for('index'))


@app.route('/update_Opinions', methods=['GET'])
def opinions_update_legacy():
    return redirect(url_for('opinions_update'))


@app.route('/indexes/update', methods=['GET'])
def indexes_update():
    # db.session.query(Index).delete()
    request = urllib.request.Request('https://datosmacro.expansion.com/bolsa')
    request.add_header("User-Agent", "Mozilla/5.0")
    response = urllib.request.urlopen(request)

    soup = BeautifulSoup(response.read(), "html5lib")

    # Obtenemos la tabla por un ID específico
    tabla_WhereTr = soup.find('tbody')

    alreadyDone = db.session.query(Index) \
                    .filter(Index.date == date.today()) \
                    .first()

    if not alreadyDone:
        for fila in tabla_WhereTr.find_all("tr"):
            nroCelda = 0
            for celda in fila.find_all('td'):
                if nroCelda == 0:
                    name = celda.text.replace(" [+]", "")
                    print("Indice:", name)
                elif nroCelda == 2:
                    price = celda.text \
                                 .replace(".", "") \
                                 .replace(",", ".")
                    print("Valor:", price)
                elif nroCelda == 3:
                    change = celda.text \
                                  .replace(",", ".") \
                                  .rstrip("%")
                    print("%Change:", change)
                nroCelda += 1

            if name and price:
                try:
                    index = Index(name=name,
                                  value=price,
                                  variation=change,
                                  date=date.today())
                    db.session.add(index)
                except ValueError:
                    pass
        db.session.commit()

    return redirect(url_for('index'))


@app.route('/update_Indexes', methods=['GET'])
def indexes_update_legacy():
    return redirect(url_for('indexes_update'))


if __name__ == "__main__":
    app.run(debug=True)
