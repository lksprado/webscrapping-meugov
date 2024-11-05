import time
from urllib.error import HTTPError, URLError

import pandas as pd
import requests as r


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
            theme = temas[0].get("title") if temas else None
            organization_id = registro.get("organizationId")
            organization_name = registro.get("organizationName")
            organization_uf = registro.get("organizationUf")
            organization_municipio = registro.get("organizationMunicipio")
            organization_title = registro.get("organizationTitle")
            maintainer = registro.get("maintainer")
            created_date = registro.get("dataCriacao")
            update_date = registro.get("dataAtualizacao")
            periodicity = registro.get("conjuntoDadosEdicao", {}).get("periodicidade")
            file_count = registro.get("quantidadeRecursos")
            download_count = registro.get("quantidadeDownloads")
            followers_count = registro.get("quantidadeSeguidores")
            is_validated = registro.get("conjuntoDadosValidado")
            is_updated = registro.get("conjuntoDadosEstaAtualizado")
            description = registro.get("notes")
            url = f"https://dados.gov.br/dados/conjuntos-dados/{name}"

            variables.append(
                {
                    "id": id,
                    "name": name,
                    "title": title,
                    "tema": theme,
                    "organization_id": organization_id,
                    "organization_name": organization_name,
                    "organization_uf": organization_uf,
                    "organization_municipio": organization_municipio,
                    "organization_title": organization_title,
                    "maintainer": maintainer,
                    "created_date": created_date,
                    "update_date": update_date,
                    "periodicidade": periodicity,
                    "quantidade_recursos": file_count,
                    "quantidade_downloads": download_count,
                    "quantidade_seguidores": followers_count,
                    "conjunto_validado": is_validated,
                    "conjunto_atualizado": is_updated,
                    "descricao": description,
                    "url": url,
                }
            )
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
