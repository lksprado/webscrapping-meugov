import requests as r

url = f"https://dados.gov.br/api/publico/conjuntos-dados/buscar?offset=12500&tamanhoPagina=500"

con = r.get(url)
con = con.json()
print(len(con["registros"]))
