pip install folium
import pandas as pd 
import streamlit as st
st.set_page_config(layout="wide")
import folium
import numpy as np
from streamlit_folium import folium_static

df = pd.read_csv('data\df_bevolking_z.csv')
df = df.drop(columns='Unnamed: 0')



st.title('Buurtmonitor Ermelo')


























# Maak twee kolommen
col1, col2 = st.columns(2)

# Linker kolom voor de kaart
with col1:
    kolomlijst = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
    indicator = st.selectbox("Selecteer een indicator:",kolomlijst)
   # GeoJSON URL
    geo_json = 'https://cartomap.github.io/nl/wgs84/buurt_2023.geojson'

    # Maak een kaartobject aan
    m = folium.Map(location=[52.3017, 5.6203], zoom_start=13)

    # Maak de choropleth kaart
    folium.Choropleth(
        geo_data=geo_json,
        name='Choropleth',
        data=df,
        columns=['WijkenEnBuurten', indicator],
        key_on='feature.properties.statnaam',
        fill_color='YlOrRd',
        nan_fill_opacity=0,
        fill_opacity=0.5,
        line_color='black',
        line_weight=0.00001,
        line_opacity=0.1,
        legend_name='Bevolkingsdichtheid per buurt'
    ).add_to(m)

    # Toevoegen van tooltips
    folium.GeoJson(
        geo_json,
        style_function=lambda x: {'fillColor': 'transparent', 'color': 'black', 'weight':'1'},
        tooltip=folium.GeoJsonTooltip(
            fields=['statnaam'],
            localize=True
        )
    ).add_to(m)



    # Laagcontroles toevoegen
    folium.LayerControl().add_to(m)
    folium_static(m)









# Rechter kolom voor de grafiek
with col2:
    buurten = df['WijkenEnBuurten'].to_list()
    buurt_selectie = st.selectbox("Selecteer een specifieke buurt om de onderliggende scores op indicatoren te zien:",buurten)
    df_buurt = df.query("WijkenEnBuurten == @buurt_selectie")
    df_buurt = df_buurt.set_index('WijkenEnBuurten')
    df_buurt_transposed = df_buurt.T


    import plotly.express as px

    fig = px.bar(
    df_buurt_transposed,
    x=df_buurt_transposed[buurt_selectie],  # Waarden
    y=df_buurt_transposed.index,  # Categorieën 
    orientation='h',
    width=900, 
    height=600)  # Horizontale bars
    
    

    fig.update_layout(xaxis_range=[-4,4])

    st.plotly_chart(fig)
