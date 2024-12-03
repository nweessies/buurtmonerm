import pandas as pd 
import streamlit as st
import folium
import numpy as np
from streamlit_folium import st_folium
import plotly.express as px

# Cache de data loading
@st.cache_data
def load_data():
    df = pd.read_csv('data/df_bevolking_z.csv')
    return df.drop(columns='Unnamed: 0')

# Cache het GeoJSON laden
@st.cache_data
def load_geojson():
    return 'https://cartomap.github.io/nl/wgs84/buurt_2023.geojson'

# Page config
st.set_page_config(layout="wide")

# Initialize session state
if 'selected_buurt' not in st.session_state:
    st.session_state.selected_buurt = None

# Load data met caching
df = load_data()
geo_json = load_geojson()

st.title('Buurtmonitor Ermelo')

# Maak twee kolommen
col1, col2 = st.columns(2)

# Linker kolom voor de kaart
with col1:
    kolomlijst = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
    indicator = st.selectbox("Selecteer een indicator:", kolomlijst)
    
    # Maak een kaartobject aan - alleen als nodig
    if 'map' not in st.session_state:
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
        
        folium.LayerControl().add_to(m)
        st.session_state.map = m
    
    # Display map en vang events op
    map_data = st_folium(st.session_state.map, width=800, height=500)
    
    # Update selected_buurt alleen als er echt een nieuwe selectie is
    if map_data.get('last_active_drawing'):
        clicked_feature = map_data['last_active_drawing']
        if 'properties' in clicked_feature and 'statnaam' in clicked_feature['properties']:
            new_selection = clicked_feature['properties']['statnaam']
            if new_selection in df['WijkenEnBuurten'].values and new_selection != st.session_state.selected_buurt:
                st.session_state.selected_buurt = new_selection
                st.experimental_rerun()

# Rechter kolom voor de grafiek
with col2:
    buurten = df['WijkenEnBuurten'].tolist()  # Gebruik tolist() in plaats van unique()
    
    # Fix voor de index conversie
    if st.session_state.selected_buurt in buurten:
        default_index = buurten.index(st.session_state.selected_buurt)
    else:
        default_index = 0
    
    buurt_selectie = st.selectbox(
        "Selecteer een specifieke buurt om de onderliggende scores op indicatoren te zien:",
        buurten,
        index=default_index
    )
    
    # Optimaliseer de data transformatie
    df_buurt = df[df['WijkenEnBuurten'] == buurt_selectie].set_index('WijkenEnBuurten').T
    
    # Maak grafiek
    fig = px.bar(
        df_buurt,
        x=df_buurt[buurt_selectie],
        y=df_buurt.index,
        orientation='h'
    )
    
    fig.update_layout(
        xaxis_range=[-4,4],
        width=900,
        height=600
    )
    st.plotly_chart(fig, use_container_width=True)
