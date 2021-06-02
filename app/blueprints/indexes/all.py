import urllib
from bs4 import BeautifulSoup
from database import db, Index, Value, Favourite, EmployeeEncoder
from sqlalchemy import func
from sqlalchemy.orm import selectinload
from datetime import date
import time
import sys
import simplejson, json
from urllib.parse import unquote
import datetime
from flask import (
    g,
    redirect,
    render_template,
    request,
    flash,
    session,
    flash,
    url_for
)
from ..base import indexes, root


@indexes.route('/date', methods=['POST'])
def get_new_date():

    selected_date = request.get_data()
    selected_date = str(selected_date)
    selected_date = unquote(selected_date)

    if request.method == 'POST' and selected_date:

        selected_date = selected_date[: - 14]
        selected_date = selected_date[16:]
        table_text = 'Datos de ' + selected_date
        selected_date=selected_date.replace(',','')
        selected_date = time.strftime("%Y-%m-%d", time.strptime(selected_date, "%a %d %b %Y"))

        all_idx_values = Value.query.filter(func.DATE(Value.timestamp) == selected_date)\
                                .options(selectinload(Value.index))\
                                .all()

    max_idx = 0
    idxs_values = []
    idxs_values_all = []

    if len(all_idx_values) > 0:
        avg = sum(map(lambda val: val.value, all_idx_values)) / len(all_idx_values)
        for val in all_idx_values:
            if val.value > avg:
                continue
            elif val.value > max_idx:
                max_idx = val.value

            idxs_values.append({
                'value': val.value,
                'variation': val.variation,
                'index': {
                    'id': val.index.id,
                    'name': val.index.name
                }
            })

        for val in all_idx_values:
            idxs_values_all.append({
                'value': val.value,
                'variation': val.variation,
                'index': {
                    'id': val.index.id,
                    'name': val.index.name
                    }
                })

    idxs_values.sort(key=lambda idx_val: -idx_val['value'])
    idxs_values_all.sort(key=lambda idx_val: -idx_val['value'])

    return {'data':idxs_values,'data_all':idxs_values_all}

@indexes.route('/', methods=['GET', 'POST'])
def get_indexes():
    if not g.user:
        return redirect(url_for('auth.login_get'))


    # Tenemos que filtrar por un índice porque las horas son distintas en cada uno, así que si no terminamos con 500 fechas iguales al seleccionar.
    all_dates_available = Value.query.filter(Value.index_id == 1046)\
                                     .distinct(Value.timestamp)\
                                     .all()

    idxs_dates = [val.timestamp for val in all_dates_available]
    idxs_dates.reverse()

    #dtt=datetime.datetime.today()
    dtt=all_dates_available[-1].timestamp
    dtt=dtt.strftime("%a, %d %b %Y")
    table_text = 'Datos de '+ dtt

    dtt=dtt.replace(',','')
    selected_date = time.strftime("%Y-%m-%d", time.strptime(dtt, "%a %d %b %Y"))


    all_idx_values = Value.query.filter(func.DATE(Value.timestamp) == selected_date)\
                                .options(selectinload(Value.index))\
                                .all()

    max_idx = 0
    idxs_values = []
    idxs_values_all = []

    if len(all_idx_values) > 0:
        avg = sum(map(lambda val: val.value, all_idx_values)) / len(all_idx_values)
        for val in all_idx_values:
            if val.value > avg:
                continue
            elif val.value > max_idx:
                max_idx = val.value

            idxs_values.append({
                'value': val.value,
                'variation': val.variation,
                'index': {
                    'id': val.index.id,
                    'name': val.index.name
                    }
                })

        for val in all_idx_values:
            idxs_values_all.append({
                'value': val.value,
                'variation': val.variation,
                'index': {
                    'id': val.index.id,
                    'name': val.index.name
                    }
                })

    # Ordenado por valor
    idxs_values.sort(key=lambda idx_val: -idx_val['value'])
    idxs_values_all.sort(key=lambda idx_val: -idx_val['value'])

    # Ordenado alfabéticamente
    # idxs_values.sort(key=lambda idx_val: idx_val['index']['name'])


    # Inicio Guardar los favoritos en la DB v  v  v v  v  v v  v  v v  v  v v  v  v v  v  v v  v  v v  v  v v  v  v
    favourites=0
    all_fav_index=Favourite.query.filter(Favourite.user_id == g.user.id)\
                                                .distinct(Favourite.index_id)\
                                                .all()
    idxs_fav = []

    for val in all_fav_index:
        idxs_fav.append(str(val.index_id))

    fav_id = request.form.get('fav_id')
    user_id = request.form.get('user_id')

    if request.method == 'POST' and fav_id and user_id  :

        if not fav_id in idxs_fav:
            new_favourite = Favourite(user_id=user_id, index_id=fav_id)
            db.session.add(new_favourite)
            db.session.commit()

        else:
            quit_favourite = Favourite.query.filter_by(index_id=fav_id, user_id=user_id).first()
            db.session.delete(quit_favourite)
            db.session.commit()

            #g.user.id, favourites[0]
            #query para meter el favorito en la base de datos
        all_fav_index=Favourite.query.filter(Favourite.user_id == g.user.id)\
                                                .distinct(Favourite.index_id)\
                                                .all()
        idxs_fav = []

        for val in all_fav_index:
           idxs_fav.append(str(val.index_id))

    # Final Guardar los favoritos en la DB ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^
    return render_template('index.html', idxs_values=idxs_values, idxs_values_all=idxs_values_all, max_idx=max_idx, idxs_dates=idxs_dates, table_text=table_text, favourites=idxs_fav, user_id=g.user.id)  # , labels=labels, values=values, urls=urls)


@indexes.route('/update')
def update_indexes():
    # db.session.query(Index).delete()
    request = urllib.request.Request('https://datosmacro.expansion.com/bolsa')
    request.add_header("User-Agent", "Mozilla/5.0")
    response = urllib.request.urlopen(request)

    soup = BeautifulSoup(response.read(), "html5lib")

    # Obtenemos la tabla por un ID específico
    tabla_WhereTr = soup.find('tbody')

    today = date.today()
    alreadyDone = Value.query.filter(func.DATE(Value.timestamp) == today).first()
    if not alreadyDone:
        all_idxs = Index.query.all()
        all_idxs = {idx.name: idx.id for idx in all_idxs}

        for fila in tabla_WhereTr.find_all("tr"):
            idx, value, variation = None, None, None
            for cell_num, cell in enumerate(fila.find_all('td')):
                if cell_num == 0:
                    idx = cell.text.replace(" [+]", "")
                elif cell_num == 2:
                    value = cell.text.replace(".", "").replace(",", ".")
                elif cell_num == 3:
                    variation = cell.text.replace(",", ".").rstrip("%")

                if cell_num > 3:
                    break

            if idx and value:
                if idx not in all_idxs:
                    new_idx = Index(name=idx)
                    db.session.add(new_idx)
                    db.session.flush()
                    all_idxs[idx] = new_idx.id
                try:
                    new_value = Value(index_id=all_idxs[idx],
                                      value=value,
                                      variation=variation if variation != "" else None,
                                      timestamp=today)
                    db.session.add(new_value)
                except ValueError as e:
                    print(f"ValueError on storing index: {e}")
        db.session.commit()

    return redirect(url_for('indexes.get_indexes'))


@root.route('/update_Indexes')
def update_indexes_legacy():
    return redirect(url_for('indexes.update_indexes'))




















