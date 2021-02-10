import urllib
from bs4 import BeautifulSoup
from database import db, Noticias
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


noticias = Blueprint('noticias', __name__, template_folder='../templates')


@noticias.route('/noticias')
def get():
    if not g.user:
        return redirect(url_for('auth.login_get'))

    titulo, cuerpo, url = [], [], []
    all_noticias = Noticias.query.all()
    for noticias in all_noticias:
        titulo.append(noticias.titulo)
        cuerpo.append(noticias.cuerpo)
        url.append(noticias.url)

    return render_template('noticias.html', titulo=titulo, cuerpo=cuerpo, url=url)


@noticias.route('/noticias/update')
def update():
    Noticias.query.delete()
    db.session.commit()

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

    return redirect(url_for('noticias.get'))


@noticias.route('/update_Noticias')
def update_legacy():
    return redirect(url_for('noticias.update'))