import streamlit as st
import pandas as pd
import plotly.express as px
import json

st.set_page_config(layout="wide")  # Ajusta layout

st.title("Meu Mapa Coroplético em Streamlit")

# 1) Ler CSV (ajuste o caminho ou coloque no mesmo diretório)
df = pd.read_csv(
    'dados.csv',
    sep=';', 
    encoding='utf-8'
)

# 2) Agrupar soma de "Conceito" por UF
df_sum = df.groupby('UF', as_index=False)['Conceito'].sum()

# 3) Ler o GeoJSON
with open('brazil_states.geojson', 'r', encoding='utf-8') as f:
    brazil_states = json.load(f)

# Ajustar o 'id' para a sigla
for feature in brazil_states['features']:
    sigla = feature['properties']['sigla'].upper()
    feature['id'] = sigla

# 4) Criar o mapa com Plotly
fig = px.choropleth_mapbox(
    df_sum,
    locations='UF',
    geojson=brazil_states,
    color='Conceito',
    center={'lat': -14, 'lon': -55},
    zoom=3,
    mapbox_style='carto-positron',
    hover_name='UF',
    hover_data={'Conceito': True}
)

fig.update_layout(
    margin=dict(r=0, t=0, l=0, b=0),
    title="Mapa do Brasil – Soma dos Conceitos"
)

# 5) Exibir no Streamlit
st.plotly_chart(fig, use_container_width=True)
