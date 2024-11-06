import openpyxl
import pandas as pd

# Carregar o DataFrame
df = pd.read_csv(
    "data/final_data_2024-11-05.csv", sep=";", encoding="utf-8", quotechar='"'
)
df = df[["organization_municipio"]]
df = df.drop_duplicates(subset=["organization_municipio"])
df = df.dropna(subset=["organization_municipio"])
df["organization_municipio"] = df["organization_municipio"].str.upper()

df2 = pd.read_excel(
    "data/anexo_16261_Coordenadas_Sedes_5565_Municípios_2010.xlsx",
    sheet_name="Municípios e Coord. Sedes 2013",
)

df3 = df.merge(
    df2[["NOME_MUNICIPIO", "LONGITUDE", "LATITUDE"]],
    left_on="organization_municipio",
    right_on="NOME_MUNICIPIO",
    how="left",
)

# Salvar o DataFrame com as coordenadas
df3.to_csv(
    "data/final_data_com_coordenadas.csv", sep=";", encoding="utf-8", index=False
)

print(
    "Coordenadas adicionadas ao DataFrame e salvas no arquivo 'final_data_com_coordenadas.csv'."
)
