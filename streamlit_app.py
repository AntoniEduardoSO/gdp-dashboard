import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json

st.set_page_config(layout="wide")
st.title("Mapa Cloroplético com Valores e Estados Ausentes em Preto")

# --------------------------------------------------
# 1) Lista fixa de estados para garantir que todos entrem
# --------------------------------------------------
all_states = [
    "AC","AL","AM","AP","BA","CE","DF","ES","GO","MA",
    "MG","MS","MT","PA","PB","PE","PI","PR","RJ","RN",
    "RO","RR","RS","SC","SE","SP","TO"
]
# Se quiser, inclua também a "Regiao", mas para este exemplo usaremos só UF.

# --------------------------------------------------
# 2) Carregar o CSV de dados
#    Exemplo: colunas: UF;Municipio;Regiao;Sigla;Status Jurídico;Grau;Conceito;País
# --------------------------------------------------
df = pd.read_csv(
    "dados.csv",
    sep=";",
    encoding="utf-8"
)

# Garantir que "UF" exista e "Conceito" seja numérico
df["Conceito"] = pd.to_numeric(df["Conceito"], errors="coerce")

# Agrupar a soma do "Conceito" por UF
df_sum = df.groupby("UF", as_index=False)["Conceito"].sum()

# --------------------------------------------------
# 3) Criar um DataFrame com todas as UF (para merge)
# --------------------------------------------------
all_df = pd.DataFrame({"UF": all_states})
df_merged = pd.merge(all_df, df_sum, on="UF", how="left")
# Agora df_merged tem 27 linhas (uma para cada UF).
# Se algum estado não estava no CSV, "Conceito" será NaN.

# --------------------------------------------------
# 4) Ler o GeoJSON e definir 'id' = sigla.upper()
# --------------------------------------------------
with open("brazil_states.geojson", "r", encoding="utf-8") as f:
    brazil_states = json.load(f)

for feature in brazil_states["features"]:
    sigla = feature["properties"]["sigla"].upper()
    feature["id"] = sigla

# --------------------------------------------------
# 5) Montar o mapa coroplético
#    color = "Conceito"
#    color_continuous_na_color = "black" => estados sem dado ficam pretos
# --------------------------------------------------
fig = px.choropleth_mapbox(
    df_merged,
    locations="UF",
    geojson=brazil_states,
    color="Conceito",
    color_continuous_scale="Viridis",
    color_continuous_midpoint=df_merged["Conceito"].mean(skipna=True),  # opcional
    center={"lat": -14, "lon": -55},
    zoom=3,
    mapbox_style="carto-positron",
    hover_name="UF",
    hover_data={"Conceito": True},
    # Faz com que NaN seja plotado em preto
    # (funciona a partir de plotly.express 4.11+)
    # color_continuous_na_color="black",
)

fig.update_layout(
    margin=dict(r=0, t=0, l=0, b=0),
    title="Mapa do Brasil – Soma dos Conceitos (estados sem dados em preto)"
)

# --------------------------------------------------
# 6) Adicionar Scattermapbox com o texto dos valores
#    Precisamos lat/lon de cada estado
# --------------------------------------------------
coords = {
    "AC": (-8.77, -70.55),
    "AL": (-9.62, -36.82),
    "AM": (-3.47, -65.10),
    "AP": (1.41, -51.77),
    "BA": (-13.29, -41.71),
    "CE": (-5.20, -39.53),
    "DF": (-15.83, -47.86),
    "ES": (-19.19, -40.34),
    "GO": (-15.98, -49.86),
    "MA": (-5.42, -45.44),
    "MG": (-18.10, -44.38),
    "MS": (-19.45, -54.63),
    "MT": (-12.64, -55.42),
    "PA": (-3.79, -52.48),
    "PB": (-7.28, -36.72),
    "PE": (-8.38, -37.86),
    "PI": (-6.60, -42.28),
    "PR": (-24.89, -51.55),
    "RJ": (-22.25, -42.66),
    "RN": (-5.81, -36.59),
    "RO": (-10.83, -63.34),
    "RR": (1.99, -61.33),
    "RS": (-30.17, -53.50),
    "SC": (-27.45, -50.95),
    "SE": (-10.57, -37.45),
    "SP": (-22.19, -48.79),
    "TO": (-9.46, -48.26)
}

# Montar lista de lat/lon + texto = valor de Conceito (ou vazio se NaN)
text_lat = []
text_lon = []
text_val = []

for i, row in df_merged.iterrows():
    uf = row["UF"]
    val = row["Conceito"]
    lat, lon = coords[uf]

    # Se for NaN, pode mostrar " - " ou "0" ou outra string
    if pd.isna(val):
        label = "-"
    else:
        label = str(int(val))  # ou f"{val:.2f}" se quiser decimal

    text_lat.append(lat)
    text_lon.append(lon)
    text_val.append(label)

fig.add_trace(
    go.Scattermapbox(
        lat=text_lat,
        lon=text_lon,
        mode="text",
        text=text_val,
        textfont=dict(color="white", size=12),  # cor do texto
        textposition="middle center",
        showlegend=False
    )
)

# Ajustar zoom e centro novamente, para garantir que a camada do Scatter fique coerente
fig.update_layout(
    mapbox=dict(
        zoom=3,
        center=dict(lat=-14, lon=-55)
    )
)

# --------------------------------------------------
# 7) Renderizar no Streamlit
# --------------------------------------------------
st.plotly_chart(fig, use_container_width=True)
