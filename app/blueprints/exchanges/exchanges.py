import json
import config
import urllib
from database import Index
from datetime import datetime, timedelta
from flask import (
    g,
    Blueprint,
    redirect,
    jsonify,
    request,
    url_for,
    render_template
)
from werkzeug.exceptions import NotFound
from ..base import exchanges

@exchanges.route('/')
def list():
    return render_template('exchanges_list.html')

@exchanges.route('/<mic>')
def list_tickers(mic):
    return render_template('exchange_tickers.html', mic=mic)

@exchanges.route('/<mic>/symbols/<symbol>')
def list_symbol_values(mic, symbol):

    transactions = Transactions.query.filter(Transactions.user_id == g.user.id, Transactions.idx_id==symbol, Transactions.bolsa_id==mic).order_by(desc(Transactions.fecha)).all() #,Transactions.idx_id == index
    trans_values = []
    if len(transactions) > 0:
        for val in transactions:
            trans_values.append({
                'id': val.id,
                'amount': val.amount,
                'idx_id': val.idx_id,
                'user_id': val.user_id,
                'value': val.value,
                'quantity': val.quantity,
                'fecha': val.fecha,
                'operation': val.operation,
                'bolsa_id': val.bolsa_id
            })

    return render_template('exchange_ticker.html', mic=mic, symbol=symbol, transactions=trans_values)

###########################################################

from sqlalchemy import func, desc
from database import db, Opinion, Value, Index, Transactions, User
from flask import (
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
    flash
)
@exchanges.route('/buy', methods=['POST'])
def buy():
    num_value = request.form['num_value']
    actual_value = request.form['actual_value']
    bolsa_id = request.form['bolsa_id']
    idx_id = request.form['idx_id']
    id_user = g.user.id

    money = User.query.filter(User.id == id_user).first()
    amount=float(num_value)*float(actual_value)
    if float(money.money) >= amount:
        try:
            new_trans = Transactions(amount=amount, idx_id=idx_id, user_id=id_user, value=actual_value, quantity=num_value, operation=1, bolsa_id=bolsa_id)
            db.session.add(new_trans)
            money.money=float(money.money)-amount
            db.session.commit()
            flash('Compra realizada con éxito.')
        except Exception:
            flash('Error.')
    else:
        flash('No tienes saldo suficiente.')
    return redirect(url_for("exchanges.list_symbol_values", mic=bolsa_id, symbol=idx_id))



@exchanges.route('/sell', methods=['POST'])
def sell():
    num_value = request.form['num_value']
    actual_value = request.form['actual_value']
    bolsa_id = request.form['bolsa_id']
    idx_id = request.form['idx_id']
    id_user = g.user.id

    money = User.query.filter(User.id == id_user).first()
    amount=float(num_value)*float(actual_value)
    id_index=idx_id
    transactions = Transactions.query.filter(Transactions.user_id == g.user.id, Transactions.idx_id == id_index, Transactions.bolsa_id==bolsa_id).all()
    actual_actions=0
    for trans in transactions:
        if trans.operation==1:
            actual_actions=actual_actions+trans.quantity
        else:
            actual_actions=actual_actions-trans.quantity

    if float(actual_actions) >= float(num_value):
        try:
            new_trans = Transactions(amount=amount, idx_id=idx_id, user_id=id_user, value=actual_value, quantity=num_value, operation=0, bolsa_id=bolsa_id)
            db.session.add(new_trans)
            money.money=float(money.money)+amount
            db.session.commit()
            flash('Venta realizada con éxito.')
        except Exception:
            flash('Error.')
    else:
        flash('No tienes acciones suficientes.')
    return redirect(url_for("exchanges.list_symbol_values", mic=bolsa_id, symbol=idx_id))



