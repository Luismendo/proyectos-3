import urllib
from bs4 import BeautifulSoup
from database import db, Opinion, Index
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


opiniones = Blueprint('opiniones', __name__, template_folder='../templates')


@opiniones.route('/opiniones')
def get():
    index = request.args.get('index')
    if not index:
        return redirect(url_for('indexes.get'))

    opinions = Opinion.query.filter_by(company=index).all()

    lastValuesIndex = Index.query.filter_by(name=index) \
                           .order_by(Index.date.desc()) \
                           .limit(14)

    lastValues,lastDates = [],[]

    for index in lastValuesIndex:
        lastValues.append(index.value)
        lastDates.append(index.date.strftime("%m/%d/%Y"))

    lastValues.reverse()
    lastDates.reverse()

    return render_template('opiniones.html', index=index.name, opinions=opinions, values=lastValues, dates=lastDates)


def fetch_opinions(name):
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
    opinions = []
    title, href = "", ""
    for fila in tabla.find_all("article"):
        if n > 3:
            break

        title = fila.find('a', attrs={'class': 'title'}).text
        bodys = fila.find("p").text
        href = fila.find("a").get("href")

        if "https" not in href:
            href = "https://es.investing.com"+href

        if title:
            try:
                opinions.append(Opinion(company=name, title=title, body=bodys, page=href))
                n += 1
            except ValueError as e:
                print(f"ValueError on fetching opinion: {e}")
                return None
    return opinions


@opiniones.route('/opiniones/update')
def update():
    Opinion.query.delete()
    db.session.commit()

    page = urllib.request.urlopen('https://datosmacro.expansion.com/bolsa').read()

    soup = BeautifulSoup(page, "html5lib")
    # tabla = soup.find('table', attrs={'id': 'tb1_1139'})  # id tabla
    tabla_WhereTr = soup.find('tbody')

    for fila in tabla_WhereTr.find_all("tr"):
        for celda in fila.find('td'):
            name = celda.text
            ops = fetch_opinions(name)
            for op in ops:
                try:
                    db.session.add(op)
                    db.session.commit()
                except Exception as ex:
                    print(f"Error storing opinion: {ex}")

    return redirect(url_for('indexes.get'))


@opiniones.route('/update_Opinions')
def update_legacy():
    return redirect(url_for('opinions.update'))
