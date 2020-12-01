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

query = "mysql> INSERT INTO Indexes (Name) Values "

json=list()
for fila in tabla.find_all("tr"):
    cell_num = 0
    name = None
    price = None
    timestamp = None

    for celda in fila.find_all('td'):
        if cell_num == 0:
            name = celda.text

        elif cell_num == 2:
            price=celda.text
            price=price.replace('.', '').replace(',', '.')
            price=float(price)

        elif cell_num == 6:
            timestamp = celda.text
            timestamp += ' '
        
        elif cell_num == 7:
            timestamp += celda.text

        cell_num += 1
    if name and price:
        try:
            query = query + "('"+name+"')"+ ","
            json.append({
                'name': name,
                'price': price,
                'timestamp': datetime.strptime(timestamp, r"%d/%m/%Y %H:%M:%S").strftime(r"%Y-%m-%d %H:%M:%S")
            })
        except ValueError:
            pass

#print(f"{json}")
query = query + ";"
print(query)