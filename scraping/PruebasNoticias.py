import requests
import csv
from bs4 import BeautifulSoup
from datetime import datetime


url_page = 'https://es.investing.com/news/stock-market-news'

# tarda 480 milisegundos
page = requests.get(url_page).text 
soup = BeautifulSoup(page, "html5lib")

# Obtenemos la tabla por un ID específico
tabla = soup.find('section', attrs={'id': 'leftColumn'})#id seccion
#tabla = soup.find('section')#id seccion
print("Titulo: ", soup);
tabla_WhereNew = soup.find('article', attrs={'class': 'js-article-item articleItem'})#id noticia
name=""
price=""
nroFila=0