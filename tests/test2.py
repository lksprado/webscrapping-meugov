import pandas as pd 

df = pd.read_csv("data/meugov_extraction_2024-11-04.csv", sep=";")

print(df["id"].nunique())