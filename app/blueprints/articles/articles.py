import urllib
from bs4 import BeautifulSoup
from database import db, Article
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
from ..base import articles, root


@articles.route('/')
def get_articles():
    if not g.user:
        return redirect(url_for('auth.login_get'))

    articles = Article.query.all()

    return render_template('articles.html', articles=articles)


@articles.route('/update')
def update_articles():
    Article.query.delete()
    db.session.commit()

    request = urllib.request.Request('https://es.investing.com/news/stock-market-news')
    request.add_header("User-Agent", "Mozilla/5.0")
    response = urllib.request.urlopen(request)

    soup = BeautifulSoup(response.read(), "html5lib")
    tabla = soup.find('section', attrs={'id': 'leftColumn'})  # id seccion

    inserted = 0
    for fila in tabla.find_all("article"):
        if fila.get("class")[1] != "dfp-native":
            body = fila.find('p').text
            body = body.replace("\n", " ")
            body = body.strip()

            title_href = fila.find('a', attrs={'class': 'title'})
            title = title_href.text

            url = title_href.get("href")

            if "https" not in url:
                url = "https://es.investing.com/" + url.strip("/")

            try:
                article = Article(title=title,
                                  body=body,
                                  url=url)
                db.session.add(article)
            except ValueError:
                continue
            inserted += 1

    if inserted > 0:
        db.session.commit()

    return redirect(url_for('articles.get_articles'))


@root.route('/update_Noticias')
def update_legacy():
    return redirect(url_for('articles.update_articles'))
