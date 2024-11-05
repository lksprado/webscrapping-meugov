import requests as r
from urllib.error import HTTPError
from urllib.error import URLError
import pandas as pd 
import time


class Crawler:
    data = None 
    
    def __init__(self, pagesize=200):
        self.pagesize = pagesize
        self.offset = 0
        self.max_retries = 5
        self.retry_delay = 3

    def connect(self):
        url = f"https://dados.gov.br/api/publico/conjuntos-dados/buscar?offset={self.offset}&tamanhoPagina={self.pagesize}"
        
        for attempt in range(self.max_retries):
            try:
                print(f"Fetching data from URL: {url}, Attempt: {attempt + 1}")
                con = r.get(url)
                con.raise_for_status()
                self.data = con.json()
                
                if "registros" in self.data:
                    print("Number of registers: ", len(self.data["registros"]))
                    return self.data
                else:
                    print("Unexpected response format:", self.data)
                    return None
                
            except (HTTPError, URLError) as e:
                print(f"Error fetching data: {e}")
            except r.exceptions.RequestException as e:
                print(f"Request failed: {e}")
            
            print(f"Retrying in {self.retry_delay} seconds...")
            time.sleep(self.retry_delay)
        
        print("Max retries reached. Skipping this offset.")
        return None  
    
    def get_result(self):
        result = self.data 
        variables = [] 
        for registro in result["registros"]:
            id = registro.get("id")
            name = registro.get("name")
            title = registro.get("title")
            temas = registro.get("temasAcessoRapido", [])
            tema = temas[0].get("title") if temas else None 
            organization_id = registro.get("organizationId")
            organization_name = registro.get("organizationName") 
            organization_uf = registro.get("organizationUf")
            organization_municipio = registro.get("organizationMunicipio")
            organization_title = registro.get("organizationTitle") 
            maintainer = registro.get("maintainer")
            data_criacao = registro.get("dataCriacao")
            data_atualizacao = registro.get("dataAtualizacao")
            periodicidade = registro.get("conjuntoDadosEdicao", {}).get("periodicidade")
            quantidade_recursos = registro.get("quantidadeRecursos")
            quantidade_downloads = registro.get("quantidadeDownloads")
            quantidade_seguidores = registro.get("quantidadeSeguidores")
            conjunto_validado = registro.get("conjuntoDadosValidado")
            conjunto_atualizado = registro.get("conjuntoDadosEstaAtualizado")
            descricao = registro.get("notes")
            url = f"https://dados.gov.br/dados/conjuntos-dados/{name}"
            
            variables.append({
                        "id": id,
                        "name": name,
                        "title": title,
                        "tema": tema,
                        "organization_id": organization_id,
                        "organization_name": organization_name,
                        "organization_uf": organization_uf,
                        "organization_municipio": organization_municipio,
                        "organization_title": organization_title,
                        "maintainer": maintainer,
                        "data_criacao": data_criacao,
                        "data_atualizacao": data_atualizacao,
                        "periodicidade": periodicidade,
                        "quantidade_recursos": quantidade_recursos,
                        "quantidade_downloads": quantidade_downloads,
                        "quantidade_seguidores": quantidade_seguidores,
                        "conjunto_validado": conjunto_validado,
                        "conjunto_atualizado": conjunto_atualizado,
                        "descricao": descricao,
                        "url": url
                    })
        return pd.DataFrame(variables) 
    

    def fetch_all_data(self):
        all_data = [] 
        while True:
            data = self.connect()
            if not data or "registros" not in data or len(data["registros"]) == 0:
                break 
            
            page_df = self.get_result()
            all_data.append(page_df)
            
            self.offset += self.pagesize

        print("Done")
        return pd.concat(all_data, ignore_index=True)