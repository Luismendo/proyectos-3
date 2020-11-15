import requests
import csv
from bs4 import BeautifulSoup
from datetime import datetime

# indicar la ruta
url_page = 'http://www.bolsamadrid.es/esp/aspx/Indices/Resumen.aspx'

# tarda 480 milisegundos
page = requests.get(url_page).text 
soup = BeautifulSoup(page, "html5lib")

# Obtenemos la tabla por un ID específico
tabla = soup.find('table', attrs={'id': 'ctl00_Contenido_tblÍndices'})

json=list()
for fila in tabla.find_all("tr"):
    nroCelda=0
    name = None
    price = None

    for celda in fila.find_all('td'):
        if nroCelda==0:
            name=celda.text
        elif nroCelda==2:
            price=celda.text
            price=price.replace('.', '').replace(',', '.')
            price=float(price)
        nroCelda=nroCelda+1
    
    if name and price:
        json.append({
            'name': name,
            'price': price
        })

print(f"{json}")