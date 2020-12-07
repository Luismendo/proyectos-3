import requests
import csv
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.request import Request, urlopen

r = Request('https://es.investing.com/news/stock-market-news', headers={"User-Agent": "Mozilla/5.0"})
c = urlopen(r).read()
soup = BeautifulSoup(c, "html5lib")


#url_page = 'https://es.investing.com/'

# tarda 480 milisegundos
#page = requests.get(url_page).text 
#soup = BeautifulSoup(page, "html5lib")
json=list()
# Obtenemos la tabla por un ID específico
tabla = soup.find('section', attrs={'id': 'leftColumn'})#id seccion
#tabla = soup.find('section')#id seccion
#print("Titulo: ", soup);
tabla_WhereNew = soup.find('article', attrs={'class': 'js-article-item articleItem'})#id noticia
name=""
price=""
nroFila=0
for fila in tabla.find_all("article"):
    nroCelda=0
    #lol = fila.get("class")[1]
    #print("hola ", lol)
    if fila.get("class")[1]!="dfp-native":
        name= fila.find('p')
        price= fila.find('a', attrs={'class': 'title'})
        #print("Titulo: ", price.text)
        #print("Cuerpo: ", name.text);
        if "https" in price.get("href") :
            #print("Direccion:",price.get("href"))
            json.append({
                'Titulo': price,
                'Cuerpo': name,
                'Direccion':price.get("href")
            })
        else :
            #print("Direccion: https://es.investing.com"+price.get("href"))
            json.append({
                'Titulo': price.text,
                'Cuerpo': name.text,
                'Direccion': "https://es.investing.com"+price.get("href")
            })   
print(json)
