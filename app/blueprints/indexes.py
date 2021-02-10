import urllib
from bs4 import BeautifulSoup
from database import db, Index
from datetime import date
from flask import (
    g,
    Blueprint,
    redirect,
    render_template,
    request,
    flash,
    session,
    url_for
)


indexes = Blueprint('indexes', __name__, template_folder='../templates')


@indexes.route('/')
def get():
    if not g.user:
        return redirect(url_for('auth.login_get'))

    all_idxs = Index.query.filter_by(date=date.today()).all()

    max_idx = 0
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


@indexes.route('/indexes/update')
def update():
    # db.session.query(Index).delete()
    request = urllib.request.Request('https://datosmacro.expansion.com/bolsa')
    request.add_header("User-Agent", "Mozilla/5.0")
    response = urllib.request.urlopen(request)

    soup = BeautifulSoup(response.read(), "html5lib")

    # Obtenemos la tabla por un ID específico
    tabla_WhereTr = soup.find('tbody')

    today = date.today()
    alreadyDone = Index.query.filter_by(date=today).first()
    if not alreadyDone:
        for fila in tabla_WhereTr.find_all("tr"):
            nroCelda = 0
            name, price, change = None, None, 0
            for celda in fila.find_all('td'):
                if nroCelda == 0:
                    name = celda.text.replace(" [+]", "")
                elif nroCelda == 2:
                    price = celda.text.replace(".", "").replace(",", ".")
                elif nroCelda == 3:
                    change = celda.text.replace(",", ".").rstrip("%")

                nroCelda += 1
                if nroCelda > 3:
                    break

            if name and price:
                try:
                    index = Index(name=name,
                                  value=price,
                                  variation=change,
                                  date=today)
                    db.session.add(index)
                    db.session.commit()
                except ValueError as e:
                    print(f"ValueError on storing index: {e}")

    return redirect(url_for('indexes.get'))


@indexes.route('/update_Indexes')
def update_legacy():
    return redirect(url_for('indexes.update'))
