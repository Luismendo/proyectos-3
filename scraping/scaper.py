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

name=""
price=""
nroFila=0
for fila in tabla.find_all("tr"):
    nroCelda=0
    for celda in fila.find_all('td'):
        if nroCelda==0:
            name=celda.text
            print("Indice:", name)
        if nroCelda==2:
            price=celda.text
            print("Valor:", price)
        nroCelda=nroCelda+1