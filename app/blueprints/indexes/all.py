import urllib
from bs4 import BeautifulSoup
from database import db, Index, Value
from sqlalchemy import func
from sqlalchemy.orm import selectinload
from datetime import date
from flask import (
    g,
    redirect,
    render_template,
    request,
    flash,
    session,
    url_for
)
from ..base import indexes, root


@indexes.route('/')
def get_indexes():
    if not g.user:
        return redirect(url_for('auth.login_get'))

    all_idx_values = Value.query.filter(func.DATE(Value.timestamp) == date.today())\
                                .options(selectinload(Value.index))\
                                .all()

    max_idx = 0
    idxs_values = []
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

    # Ordenado por valor
    idxs_values.sort(key=lambda idx_val: -idx_val['value'])

    # Ordenado alfabéticamente
    # idxs_values.sort(key=lambda idx_val: idx_val['index']['name'])

    return render_template('index.html', idxs_values=idxs_values, max_idx=max_idx)  # , labels=labels, values=values, urls=urls)


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
