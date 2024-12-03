import pandas as pd 
import streamlit as st
import folium
import numpy as np
from streamlit_folium import folium_static
import plotly.express as px

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
    
    # Add click event handler
    for feature in geojson.data['features']:
        buurt_naam = feature['properties']['statnaam']
        if buurt_naam in df['WijkenEnBuurten'].values:
            feature['properties']['click_handler'] = f"""
                <script>
                    element.on('click', function() {{
                        parent.postMessage({{
                            'buurt': '{buurt_naam}'
                        }}, '*');
                    }});
                </script>
            """
    
    # Laagcontroles toevoegen
    folium.LayerControl().add_to(m)
    
    # Display map
    map_data = folium_static(m, width=800)
    
    # Handle map clicks
    if map_data:
        st.session_state.selected_buurt = map_data.get('buurt')

# Rechter kolom voor de grafiek
with col2:
    # Gebruik geselecteerde buurt van kaart of dropdown
    buurten = df['WijkenEnBuurten'].to_list()
    
    if st.session_state.selected_buurt:
        default_idx = buurten.index(st.session_state.selected_buurt)
    else:
        default_idx = 0
        
    buurt_selectie = st.selectbox(
        "Selecteer een specifieke buurt om de onderliggende scores op indicatoren te zien:",
        buurten,
        index=default_idx
    )
    
    # Update session state als selectbox verandert
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
