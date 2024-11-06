import locale
from datetime import datetime as dt

import altair as alt
import pandas as pd
import streamlit as st


df = pd.read_csv("data/final_data_2024-11-05.csv", sep=";")

print(df.columns)

st.set_page_config(page_title="OPEN DATA GOVERNMENT CATALOG", layout="wide")
st.header("OPEN DATA GOVERNMENT CATALOG")
st.markdown("Analysis of **over 10.000 datasets** scrapped from dadosabertos.gov.br")
st.divider()

bn_datasets, bn_institutes, bn_files, bn_downloads, bn_followers = st.columns(5)

with bn_datasets:
    datasets = f"{df["id"].nunique():,}"
    st.metric("Bundle", datasets)

with bn_institutes:
    institutes = df["organization_id"].nunique()
    st.metric("Institutions", institutes)

with bn_files:
    files = f"{df["count_files"].sum():,}"
    st.metric("Files", files)

with bn_downloads:
    downloads = f"{df['count_downloads'].sum():,}"
    st.metric("Downloads", downloads)

with bn_followers:
    followers = df["count_followers"].sum()
    followers = locale.format_string("%d", followers, grouping=True)
    st.metric("Followers", followers)

st.divider()

df["created_date"] = pd.to_datetime(df["created_date"], format="%d/%m/%Y %H:%M:%S")
df["update_date"] = pd.to_datetime(df["update_date"], format="%d/%m/%Y %H:%M:%S")

graf_create, graf_update, graf_themes = st.columns(3, gap="medium")

with graf_create:
    st.subheader("DATASET CREATIONS OVER TIME")
    df_bar = (
        df.groupby(df["created_date"].dt.to_period("Q"))
        .agg(contagem_id=("id", "count"))
        .reset_index()
    )
    df_bar["created_date"] = df_bar["created_date"].dt.to_timestamp()

    bar_chart = (
        alt.Chart(df_bar)
        .mark_bar(color="#1e6091")
        .encode(
            x=alt.X(
                "created_date:T", title=None, axis=alt.Axis(format="%Y")
            ),  # Formata o eixo x para mostrar apenas o ano
            y=alt.Y("contagem_id:Q", title=None),
        )
        .properties(width=800, height=500)  # Ajusta o tamanho do gráfico
    )
    bar_chart = bar_chart.configure_axis(grid=False)
    st.altair_chart(bar_chart, use_container_width=True)

with graf_update:
    st.subheader("HOW LONG HAVE BEEN UPDATED COMPARED TO 2024-11-05")
    data_referencia = dt.today()
    df["updated_ago"] = (data_referencia - df["update_date"]).dt.days

    def categorizar_diferenca(dias):
        if dias <= 1:
            return "a day"
        elif dias <= 7:
            return "a week"
        elif dias <= 30:
            return "a month"
        elif dias <= 90:
            return "a quarter"
        elif dias <= 180:
            return "a semester"
        elif dias <= 365:
            return "a year"
        else:
            return "+1 year"

    order = [
        "a day",
        "a week",
        "a month",
        "a quarter",
        "a semester",
        "a year",
        "+1 year",
    ]
    # Aplicar a função de categorização
    df["updated_ago"] = df["updated_ago"].apply(categorizar_diferenca)
    df_update = (
        df[["updated_ago", "updated_ago"]]
        .groupby("updated_ago")
        .agg(sum=("updated_ago", "count"))
        .reset_index()
    )
    bar_chart = (
        alt.Chart(df_update)
        .mark_bar(color="#1e6091")
        .encode(
            x=alt.X(
                "sum:Q", title=None, axis=None
            ),  # Eixo x representa a contagem de registros
            y=alt.Y(
                "updated_ago:N",
                sort=order,
                title=None,
                axis=alt.Axis(labelAlign="left", labelPadding=70),
            ),  # Eixo y com ordenação personalizada
        )
        .properties(
            width=600,
            height=500,
        )
    )
    text = bar_chart.mark_text(
        align="center",
        baseline="middle",
        dx=20,
        color="#1e6091",
        fontWeight="bold",
        fontSize=15,
    ).encode(text=alt.Text("sum:Q", format=",.0f"))
    bar_chart = bar_chart + text
    bar_chart = bar_chart.configure_axis(grid=False)
    st.altair_chart(bar_chart, use_container_width=True)

with graf_themes:
    st.subheader("THEMES")
    df_themes = df.groupby(df["theme"]).agg(contagem_id=("id", "count")).reset_index()
    bar_chart2 = (
        alt.Chart(df_themes)
        .mark_bar(color="#1e6091")
        .encode(
            x=alt.X("contagem_id:Q", title=None, axis=None),
            y=alt.Y(
                "theme:N",
                title=None,
                sort=alt.SortField(field="contagem_id", order="descending"),
                axis=alt.Axis(
                    labelAlign="left",
                    labelLimit=190,
                    labelPadding=200,
                    labelOverlap=False,
                ),
            ),
        )
        .properties(
            width=600,
            height=500,
        )
    )
    text = bar_chart2.mark_text(
        align="center",
        baseline="middle",
        dx=20,
        color="#1e6091",
        fontWeight="bold",
        fontSize=15,
    ).encode(text=alt.Text("contagem_id:Q", format=".0f"))
    bar_chart2 = bar_chart2 + text
    bar_chart2 = bar_chart2.configure_axis(grid=False)
    st.altair_chart(bar_chart2, use_container_width=True)

institutions, institutions_pop, map = st.columns(3)


with institutions:
    st.subheader("TOP 10 INSTITUTIONS WITH THE MOST DATASETS")
    df_institutions = (
        df.groupby(df["organization_title"])
        .agg(contagem_id=("id", "count"))
        .reset_index()
    )
    df_institutions = df_institutions.sort_values(
        by="contagem_id", ascending=False
    ).head(10)
    bar_chart3 = (
        alt.Chart(df_institutions)
        .mark_bar(color="#1e6091")
        .encode(
            x=alt.X("contagem_id:Q", title=None, axis=None),
            y=alt.Y(
                "organization_title:N",
                title=None,
                sort=alt.SortField(field="contagem_id", order="descending"),
                axis=alt.Axis(
                    labelAlign="left",
                    labelLimit=260,
                    labelPadding=270,
                    labelOverlap=False,
                ),
            ),
        )
        .properties(
            width=600,
            height=500,
        )
    )
    text = bar_chart3.mark_text(
        align="center",
        baseline="middle",
        dx=20,
        color="#1e6091",
        fontWeight="bold",
        fontSize=15,
    ).encode(text=alt.Text("contagem_id:Q", format=",.0f"))
    bar_chart3 = bar_chart3 + text
    bar_chart3 = bar_chart3.configure_axis(grid=False)
    st.altair_chart(bar_chart3, use_container_width=True)

with institutions_pop:
    st.subheader("TOP 10 INSTITUTIONS WITH MOST DOWLOADS")
    df_institutions_pop = (
        df.groupby(df["organization_title"])
        .agg(sum=("count_downloads", "sum"))
        .reset_index()
    )
    df_institutions_pop = df_institutions_pop.sort_values(
        by="sum", ascending=False
    ).head(10)

    bar_chart4 = (
        alt.Chart(df_institutions_pop)
        .mark_bar(color="#1e6091")
        .encode(
            x=alt.X("sum:Q", title=None, axis=None),
            y=alt.Y(
                "organization_title:N",
                title=None,
                sort=alt.SortField(field="sum", order="descending"),
                axis=alt.Axis(
                    labelAlign="left",
                    labelLimit=260,
                    labelPadding=270,
                    labelOverlap=False,
                ),
            ),
        )
        .properties(
            width=600,
            height=500,
        )
    )
    text = bar_chart4.mark_text(
        align="center",
        baseline="middle",
        dx=25,
        color="#1e6091",
        fontWeight="bold",
        fontSize=15,
    ).encode(text=alt.Text("sum:Q", format=",.0f"))
    bar_chart4 = bar_chart4 + text
    bar_chart4 = bar_chart4.configure_axis(grid=False)
    st.altair_chart(bar_chart4, use_container_width=True)

with map:
    st.subheader("LOCATIONS")
    df_map = df.dropna(axis="index", how="all", subset=["LATITUDE"])
    st.map(
        data=df_map,
        latitude="LATITUDE",
        longitude="LONGITUDE",
        color="#1e6091",
        size=200,
        zoom=None,
        use_container_width=True,
        width=None,
        height=None,
    )

tab1, tab2, tab3 = st.tabs(
    ["Most downloaded", "Most followers", "Highest download rate per user"]
)

with tab1:
    dftop = df.sort_values(by="count_downloads", ascending=False).head(10)
    dftop = dftop[["title",'theme','organization_title', "update_date", "count_downloads",'count_files', "url"]]
    st.dataframe(dftop, hide_index=True, width=3000)

with tab2:
    dftop = df.sort_values(by="count_followers", ascending=False).head(10)
    dftop = dftop[["title",'theme','organization_title',"update_date", "count_followers", 'count_files',"url"]]
    st.dataframe(dftop, hide_index=True, width=3000)

with tab3:
    dftop["dw/users"] = (
        (df["count_downloads"] / df["count_followers"])
        .replace([float("inf"), -float("inf")], 0)
        .fillna(0)
        .astype(int)
    )
    dftop = dftop.sort_values(by="dw/users", ascending=False).head(10)
    dftop = dftop[["title",'theme','organization_title',"update_date", "dw/users", 'count_files',"url"]]
    st.dataframe(dftop, hide_index=True, width=3000)

updated_ago_options = list(df['updated_ago'].dropna().unique()) + ['all']
theme_options = list(df['theme'].dropna().unique()) + ['all']
organization_options = list(df['organization_title'].dropna().unique()) + ['all']

default_cat = updated_ago_options.index('all')
default_thm = theme_options.index('all')
default_org = organization_options.index('all')

st.subheader("FULL DATASET SEARCH")
sel1, sel2, sel3 = st.columns(3) 
with sel1:
    filtro_categoria = st.selectbox('Updated ago', updated_ago_options, index=default_cat)
    
with sel2:
    filtro_theme = st.selectbox('Theme', theme_options, index= default_thm)

with sel3:
    filtro_organization = st.selectbox('Institution', organization_options, index=default_org)



if filtro_categoria != 'all':
    df_filtrado = df[df['updated_ago'] == filtro_categoria]
else:
    df_filtrado = df
if filtro_categoria != 'all':
    df_filtrado = df[df['updated_ago'] == filtro_theme]
else:
    df_filtrado = df
if filtro_categoria != 'all':
    df_filtrado = df[df['updated_ago'] == filtro_organization]
else:
    df_filtrado = df


df_filtrado = df_filtrado[['title','organization_title','theme','periodicity','created_date','update_date','count_downloads','description','url','updated_ago']]
st.dataframe(df_filtrado, width=3000, hide_index=True)