import urllib
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from sqlalchemy import func
from database import db, Opinion, Value, Index
from flask import (
    g,
    redirect,
    render_template,
    request,
    flash,
    session,
    url_for,
    flash
)
from ..base import indexes, root

@indexes.route('/<index>/range', methods=['POST'])
def get_index_opinions_range(index):

    pepito = request.get_data()

    range = int(pepito[6:-40])

    if range > 9:
        min_date_timestamp = pepito[18:-20]
        max_date_timestamp = pepito[38:]
    else:
        min_date_timestamp = pepito[17:-20]
        max_date_timestamp = pepito[37:]

    min_date = datetime.fromtimestamp(int(min_date_timestamp))
    min_date = min_date.strftime("%Y-%m-%d")
    max_date = datetime.fromtimestamp(int(max_date_timestamp))
    max_date = max_date.strftime("%Y-%m-%d")

    idx = Index.query.filter(Index.id == index).first_or_404()

    latest_values = Value.query.filter(Value.index_id == idx.id) \
                            .filter(Value.timestamp >= min_date ) \
                            .filter(Value.timestamp <= max_date ) \
                            .order_by(Value.timestamp.desc()) \
                            .all()

    latest_values = [{'value': value.value,
                     'timestamp': value.timestamp.strftime("%Y/%m/%d")}
                     for value in latest_values]

    latest_values.reverse()

    return {'data':latest_values}

@indexes.route('/<index>')
def get_index_opinions(index):
    idx = Index.query.filter(Index.id == index).first_or_404()
    index_id = idx.id
    opinions = Opinion.query.filter(Opinion.index_id == idx.id).all()
    latest_values = Value.query.filter(Value.index_id == idx.id) \
                               .order_by(Value.timestamp.desc()) \
                               .all()
    latest_values = [{'value': value.value,
                      'timestamp': value.timestamp.strftime("%Y/%m/%d")}
                     for value in latest_values]
    latest_values.reverse()
    sliderRange = len(latest_values)

    return render_template('opinions.html', index=idx, opinions=opinions, latest_values=latest_values, sliderRange=sliderRange, index_id=index_id)


def download_opinions(index):
    print(f"Downloading opinions for {index.name}")
    query_string = urllib.parse.urlencode({"q": index.name})

    request = urllib.request.Request(f'https://es.investing.com/search/?{query_string}')
    request.add_header("User-Agent", "Mozilla/5.0")
    response = urllib.request.urlopen(request)

    soup = BeautifulSoup(response.read(), "html5lib")
    link = soup.find("a", class_="js-inner-all-results-quote-item row")
    if not link:
        return
    link = link.get('href')

    request = urllib.request.Request(f'https://es.investing.com{link}-opinion')
    request.add_header("User-Agent", "Mozilla/5.0")
    response = urllib.request.urlopen(request)

    soup = BeautifulSoup(response.read(), "html5lib")
    tabla = soup.find('section')  # id seccion

    n = 0
    for fila in tabla.find_all("article"):
        if n > 3:
            break

        title = fila.find('a', attrs={'class': 'title'}).text
        body = fila.find("p").text
        url = fila.find("a").get("href")

        if "https://" not in url:
            url = "https://es.investing.com/" + url.strip('/')

        if title and body and url:
            try:
                op = Opinion(index_id=index.id,
                             title=title.strip(),
                             body=body.strip(),
                             url=url)
                db.session.add(op)
            except Exception:
                continue
            n += 1

    if n > 0:
        db.session.commit()


@indexes.route('/opinions/update')
def update_indexes_opinions():
    Opinion.query.delete()
    db.session.commit()

    all_idxs = Index.query.all()
    for idx in all_idxs:
        download_opinions(idx)

    return redirect(url_for('indexes.get_indexes'))


@root.route('/update_Opinions')
def update_indexes_opinions_legacy():
    return redirect(url_for('indexes.update_indexes_opinions'))
