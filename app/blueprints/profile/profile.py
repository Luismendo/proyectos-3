from flask import (
    g,
    redirect,
    render_template,
    request,
    flash,
    url_for
)
from ..base import profile
from database import db, Index, Value, Favourite, EmployeeEncoder, Transactions, User, Avisos
from sqlalchemy.orm import selectinload
from sqlalchemy import desc
from sqlalchemy import func


@profile.route('/deposit', methods=['GET', 'POST'])
def deposit():
    if not g.user:
        return redirect(url_for('auth.login_get'))


    amount = request.form['money']

    try:
        user = User.query.filter(User.id == g.user.id).first()
        user.money=float(user.money)+float(amount)
        db.session.commit()
        flash("Ingreso realizado con éxito.")
    except Exception:
        flash("Error.")
    return redirect(url_for("profile.get_profile"))

@profile.route('/sacar', methods=['GET', 'POST'])
def sacar():

    if not g.user:
        return redirect(url_for('auth.login_get'))
    user = User.query.filter(User.id == g.user.id).first()
    amount = request.form['money']

    if float(user.money) > float(amount):
        try:
            user.money=float(user.money)-float(amount)
            db.session.commit()
            flash("Extracción realizada con éxito.")
        except Exception:
            flash("Error.")
    else:
        flash("No tienes suficiente dinero.")
    return redirect(url_for("profile.get_profile"))

@profile.route('/aviso', methods=['GET', 'POST'])
def aviso():
    if not g.user:
        return redirect(url_for('auth.login_get'))

    action=request.form['accion']
    valor=request.form['valor']
    aviso=0
    if float(action) > float(valor):
        aviso=0
    else:
        aviso=1
    #idx_id=idx_id
    idx_id=request.form['idx_id']
    try:
        new_aviso = Avisos(user_id=g.user.id, idx_id=idx_id, valor=valor, aviso=aviso)
        db.session.add(new_aviso)
        db.session.commit()
        flash("Aviso realizado con éxito.")
    except Exception:
        flash("Error.")
    #return "Error"
    return redirect(url_for("profile.get_profile"))

@profile.route('/', methods=['GET', 'POST'])
def get_profile():
    if not g.user:
        return redirect(url_for('auth.login_get'))

    fav_id = request.form.get('fav_id')
    user_id = request.form.get('user_id')

    if request.method == 'POST' and fav_id and user_id:

        quit_favourite = Favourite.query.filter_by(index_id=fav_id, user_id=user_id).first()
        db.session.delete(quit_favourite)
        db.session.commit()

    all_favs=Favourite.query.filter(Favourite.user_id == g.user.id)\
                                        .distinct(Favourite.index_id)\
                                        .all()

    idxs_fav = []

    for val in all_favs:
        idxs_fav.append(str(val.index_id))

    all_idx_values = Value.query.filter(Value.index_id.in_(idxs_fav))\
                            .order_by(Value.timestamp.desc())\
                            .options(selectinload(Value.index))\
                            .limit(len(idxs_fav))

    idxs_values = []

    for val in all_idx_values:
        idxs_values.append({
                    'value': val.value,
                    'variation': val.variation,
                    'index': {
                        'id': val.index.id,
                        'name': val.index.name
                    }
                })

    idxs_values.sort(key=lambda idx_val: -idx_val['value'])


    transactions = Transactions.query.filter(Transactions.user_id == g.user.id).order_by(desc(Transactions.fecha)).all()
    compras=0
    ventas=0
    for trans in transactions:
        if trans.operation == 1:
            compras+=1
        else:
            ventas+=1
    trans_values = []
    acciones = []
    acciones_mias=[]
    if len(transactions) > 0:
        for val in transactions:
            acciones.append(val.idx_id)

            #index = Index.query.filter(Index.id == val.idx_id).first()
            trans_values.append({
                'id': val.id,
                'amount': val.amount,
                'idx_id': val.idx_id,
                'user_id': val.user_id,
                'value': val.value,
                'quantity': val.quantity,
                'fecha': val.fecha,
                'operation': val.operation,
                'bolsa_id': val.bolsa_id,
            })
        amount=0
        acciones_nr = list(dict.fromkeys(acciones))
        for acci in acciones_nr:
            amount=0
            price=0
            bolsa_name=0;
            for val in transactions:
                if acci==val.idx_id:
                    price=val.value
                    bolsa_name = val.bolsa_id
                    if val.operation==1:
                        amount+=val.quantity
                    else:
                        amount-=val.quantity
            acciones_mias.append({
                'bolsa_id':bolsa_name,
                'name': acci,
                'amount': amount,
                'value':price,
            })
    avisos=[]
    avisos_db=Avisos.query.filter(Avisos.user_id == g.user.id).order_by(desc(Avisos.id)).all()
    for avi in avisos_db:
        valor_actual=0

        for acci in acciones_nr:
            if acci==avi.idx_id:
                valor_actual=avi.valor
        #valor_actual=250
        avisos.append({
                'id': avi.id,
                'valor': avi.valor,
                'idx_id': avi.idx_id,
                'user_id': avi.user_id,
                'aviso': avi.aviso,
                'valor_actual':valor_actual
            })






    if request.method == 'POST' and fav_id and user_id:
        return {'data':idxs_values}
    else:
        return render_template('profile.html',idxs_values=idxs_values, favourites=idxs_fav, user_id=g.user.id, transactions=trans_values, compras=compras, ventas=ventas, acciones=acciones_mias,avisos=avisos)

