url_page = 'https://datosmacro.expansion.com/bolsa'

# tarda 480 milisegundos
page = requests.get(url_page).text 
soup = BeautifulSoup(page, "html5lib")

# Obtenemos la tabla por un ID específico
tabla = soup.find('table', attrs={'id': 'tb1_1139'})#id tabla
tabla_WhereTr = soup.find('tbody')

query = "INSERT INTO Indexes (name, value, variation) VALUES "

json=list()
name=""
price=""
change=""
nroFila=0
for fila in tabla_WhereTr.find_all("tr"):
    nroCelda=0
    for celda in fila.find_all('td'):
        if nroCelda==0:
            name=celda.text
            name = name.rstrip(" [+]")
            print("Indice:", name)
        if nroCelda==2:
            price=celda.text
            price = price.replace(".", "")
            price = price.replace(",", ".")
            print("Valor:", price)
        if nroCelda==3:
            change=celda.text
            change = change.replace(",", ".")
            change = change.rstrip("%")
            print("%Change:", change)
        nroCelda=nroCelda+1
    
    
    if name and price:
        try:
            query = query + "('" +name+ "', " +price+ ", " +change+ "), "
            json.append({
                'Nombre': name,
                'Precio': price,
                'Porcentaje': change
            })
        except ValueError:
            pass
print(json) 
query = query + ";"
print(query) 
