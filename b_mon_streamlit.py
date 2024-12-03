import pandas as pd 
import streamlit as st
import folium
import numpy as np
from streamlit_folium import folium_static
import plotly.express as px
from streamlit_folium import st_folium  # We gebruiken st_folium in plaats van folium_static

# Page config
st.set_page_config(layout="wide")

# Initialize session state
if 'selected_buurt' not in st.session_state:
    st.session_state.selected_buurt = None

# Load data
df = pd.read_csv('data/df_bevolking_z.csv')
df = df.drop(columns='Unnamed: 0')

st.title('Buurtmonitor Ermelo')

# Maak twee kolommen
col1, col2 = st.columns(2)

# Linker kolom voor de kaart
with col1:
    kolomlijst = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
    indicator = st.selectbox("Selecteer een indicator:", kolomlijst)
    
    # GeoJSON URL
    geo_json = 'https://cartomap.github.io/nl/wgs84/buurt_2023.geojson'
    
    # Maak een kaartobject aan
    m = folium.Map(location=[52.3017, 5.6203], zoom_start=12)
    
    # Maak de choropleth kaart
    choropleth = folium.Choropleth(
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
    
    # Toevoegen van interactieve GeoJSON laag
    geojson = folium.GeoJson(
        geo_json,
        style_function=lambda x: {'fillColor': 'transparent', 'color': 'black', 'weight':'1'},
        tooltip=folium.GeoJsonTooltip(
            fields=['statnaam'],
            localize=True
        ),
        highlight_function=lambda x: {'weight': 3, 'color': 'red'},
    ).add_to(m)
    
    # Laagcontroles toevoegen
    folium.LayerControl().add_to(m)
    
    # Display map en vang events op
    map_data = st_folium(m, width=800, height=500)
    
    # Update selected_buurt als er op de kaart wordt geklikt
    if map_data['last_clicked']:
        clicked_lat = map_data['last_clicked']['lat']
        clicked_lng = map_data['last_clicked']['lng']
        # Hier moet je logica toevoegen om de juiste buurt te vinden op basis van coordinaten
        # Dit hangt af van je GeoJSON structuur

# Rechter kolom voor de grafiek
with col2:
    buurten = df['WijkenEnBuurten'].to_list()
    buurt_selectie = st.selectbox(
        "Selecteer een specifieke buurt om de onderliggende scores op indicatoren te zien:",
        buurten,
        index=0 if st.session_state.selected_buurt is None 
        else buurten.index(st.session_state.selected_buurt)
    )
    
    # Update session state
    st.session_state.selected_buurt = buurt_selectie
    
    # Maak grafiek
    df_buurt = df.query("WijkenEnBuurten == @buurt_selectie")
    df_buurt = df_buurt.set_index('WijkenEnBuurten')
    df_buurt_transposed = df_buurt.T
    
    fig = px.bar(
        df_buurt_transposed,
        x=df_buurt_transposed[buurt_selectie],
        y=df_buurt_transposed.index,
        orientation='h',
        width=900,
        height=600
    )
    
    fig.update_layout(xaxis_range=[-4,4])
    st.plotly_chart(fig)
