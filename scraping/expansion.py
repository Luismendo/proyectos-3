import requests
import csv
from bs4 import BeautifulSoup
from datetime import datetime

url_page = 'https://datosmacro.expansion.com/bolsa'

# tarda 480 milisegundos
page = requests.get(url_page).text 
soup = BeautifulSoup(page, "html5lib")

# Obtenemos la tabla por un ID específico
tabla = soup.find('table', attrs={'id': 'tb1_1139'})#id tabla
tabla_WhereTr = soup.find('tbody')

for fila in tabla_WhereTr.find_all("tr"):
    nroCelda=0
    name = None
    price = None
    change = None

    for celda in fila.find_all('td'):
        if nroCelda==0:
            name=celda.text
        if nroCelda==2:
            price=celda.text
        if nroCelda==3:
            change=celda.text
        nroCelda=nroCelda+1
    
    if name and price and change:
        json.append({
            'name': name,
            'price': price,
            'change': change
        })

print(f"{json}")