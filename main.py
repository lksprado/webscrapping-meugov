from datetime import datetime as dt

import pandas as pd

from src.scrapper import Crawler

pd.set_option("display.max_columns", None)


# ESCOLHER ENTRE "MAIN" E "PERIOD"
def main(which):
    crawler = Crawler(which)
    df = crawler.fetch_all_data()

    # Verificar se o DataFrame não está vazio antes de tentar salvá-lo
    if not df.empty:
        today = dt.today().strftime("%Y-%m-%d")
        df.to_csv(
            f"data/meugov_{which}_extraction_{today}.csv",
            index=False,
            sep=";",
            encoding="utf-8",
            quotechar='"',
        )
        print(f"Data saved to data/meugov_{which}_extraction_{today}.csv")
    else:
        print("No data fetched. The CSV file will not be created.")


def normalize(df1, df2):
    df1 = pd.read_csv(df1, sep=";", quotechar='"')
    df2 = pd.read_csv(df2, sep=";", quotechar='"')
    merged_df = df1.merge(
        df2[["id", "periodicity"]], on="id", how="left", suffixes=("", "_df2")
    )
    merged_df["periodicity"] = merged_df.apply(
        lambda row: (
            row["periodicity_df2"]
            if row["periodicity"] == "indefinida"
            else row["periodicity"]
        ),
        axis=1,
    )
    exclusive_df2 = df2[~df2["id"].isin(df1["id"])]

    final_df = pd.concat([merged_df, exclusive_df2], ignore_index=True)
    final_df.drop(columns="periodicity_df2", inplace=True)
    return final_df


if __name__ == "__main__":
    today = dt.today().strftime("%Y-%m-%d")

    # main("period")
    df1 = "data/meugov_main_extraction_2024-11-05.csv"
    df2 = "data/meugov_period_extraction_2024-11-05.csv"
    df3 = "data/final_data_com_coordenadas.csv"

    df3 = pd.read_csv(df3, sep=";", encoding="utf-8")
    df = normalize(df1, df2)
    df["organization_municipio"] = df["organization_municipio"].str.upper()

    df4 = df.merge(
        df3[["organization_municipio", "LONGITUDE", "LATITUDE"]],
        left_on="organization_municipio",
        right_on="organization_municipio",
        how="left",
    )

    df4.to_csv(
        f"data/final_data_{today}.csv",
        sep=";",
        quotechar='"',
        encoding="utf-8",
        index=False,
    )
