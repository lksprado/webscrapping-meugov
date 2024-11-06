import time
from urllib.error import HTTPError, URLError

import pandas as pd
import requests as r


class Crawler:
    data = None

    # DEFINIR QUAL EXTRAÇÃO FAZER MAIN OU PERIOD
    def __init__(self, which="main", pagesize=200):
        self.pagesize = pagesize
        self.offset = 0
        self.max_retries = 5
        self.retry_delay = 5
        self.base_url = "https://dados.gov.br/api/publico/conjuntos-dados/buscar?"
        self.periodicidade = 1
        self.which = which

    # FAZ CONEXÃO
    def connect(self):

        # MONTA URL CONFORME PARÂMETRO WHICH DA CLASSE
        url = f"{self.base_url}offset={self.offset}&tamanhoPagina={self.pagesize}"
        if self.which == "period":
            url += f"&periodicidade={self.periodicidade}"

        # GARANTE RETENTATIVAS EM CASO DE ERRO OU VAZIO
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

    # OBTEM VARIAVEIS
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
            periodicidade = registro.get("extras", {})
            periodicity = periodicidade.get("periodicidade") if periodicidade else None
            file_count = registro.get("quantidadeRecursos")
            download_count = registro.get("quantidadeDownloads")
            followers_count = registro.get("quantidadeSeguidores")
            description = registro.get("notes")
            url = f"https://dados.gov.br/dados/conjuntos-dados/{name}"

            variables.append(
                {
                    "id": id,
                    "name": name,
                    "title": title,
                    "theme": theme,
                    "organization_id": organization_id,
                    "organization_name": organization_name,
                    "organization_uf": organization_uf,
                    "organization_municipio": organization_municipio,
                    "organization_title": organization_title,
                    "maintainer": maintainer,
                    "periodicity": (
                        periodicity.lower()
                        if isinstance(periodicity, str)
                        else "indefinida"
                    ),
                    "created_date": created_date,
                    "update_date": update_date,
                    "count_files": file_count,
                    "count_downloads": download_count,
                    "count_seguidores": followers_count,
                    "description": description,
                    "url": url,
                }
            )
        return pd.DataFrame(variables)

    # DEFINE COMO OS LOOPS ACONTECEM
    def fetch_all_data(self):
        all_data = []
        if self.which == "main":
            while True:
                data = self.connect()
                if not data or "registros" not in data or len(data["registros"]) == 0:
                    break

                page_df = self.get_result()
                all_data.append(page_df)

                self.offset += self.pagesize

        else:
            for periodicidade in range(1, 10):
                self.periodicidade = periodicidade
                self.offset = 0
                while True:
                    data = self.connect()
                    if (
                        not data
                        or "registros" not in data
                        or len(data["registros"]) == 0
                    ):
                        break

                    page_df = self.get_result()
                    all_data.append(page_df)
                    self.offset += self.pagesize

        data = pd.concat(all_data, ignore_index=True)
        return data
