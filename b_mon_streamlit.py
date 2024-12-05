import pandas as pd 
import streamlit as st
import folium
import numpy as np
from streamlit_folium import st_folium
import plotly.express as px
import json

# Page config
st.set_page_config(layout="wide")

# Initialize session state
if 'selected_buurt' not in st.session_state:
    st.session_state.selected_buurt = None

# Load data
# Load data
try:
    df = pd.read_csv('data/data_bevolking_z-scores.xlsx')  # Ondanks .xlsx extensie als CSV inlezen
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()
st.title('Buurtmonitor Ermelo')

# Maak twee kolommen
col1, col2 = st.columns(2)

# Linker kolom voor de kaart
with col1:
    try:
        kolomlijst = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
        default_kolom = 'Totaalscore'
        default_index = kolomlijst.index(default_kolom) if default_kolom in kolomlijst else 0
        indicator = st.selectbox("Selecteer een indicator:", kolomlijst, index=default_index)

        # Debug informatie
        st.write("Eerste paar rijen van je DataFrame:")
        st.write(df[['PC5', indicator]].head())

        # GeoJSON 
        try:
            with open('data/PC_5_erm.geojson', 'r') as f:
                geo_data = json.load(f)
                st.write("Voorbeeld van postcode formaat in GeoJSON:")
                st.write(geo_data['features'][0]['properties']['postcode'])
        except FileNotFoundError:
            st.error("GeoJSON bestand niet gevonden")
            st.stop()

        # Controleer of PC5 in DataFrame aanwezig is
        if 'PC5' not in df.columns:
            st.error("PC5 kolom niet gevonden in de data")
            st.stop()

        # Maak een kaartobject aan
        m = folium.Map(
            location=[52.3017, 5.6203],
            zoom_start=12,
            tiles='CartoDB positron'
        )

        # Maak de choropleth kaart
        choropleth = folium.Choropleth(
            geo_data=geo_data,
            name='Choropleth',
            data=df,
            columns=['PC5', indicator],
            key_on='feature.properties.postcode',
            fill_color='YlOrRd',
            nan_fill_opacity=0.2,
            fill_opacity=0.7,
            line_color='black',
            line_weight=1,
            line_opacity=0.5,
            legend_name=f'{indicator} per postcode',
            highlight=True
        ).add_to(m)

        # Voeg hover toe voor debugging
        for key in choropleth._children:
            if key.startswith('color_map'):
                choropleth._children[key].add_to(m)

                # Toevoegen van interactieve GeoJSON laag met popup
                geojson = folium.GeoJson(
                    geo_data,
                    style_function=lambda x: {
                        'fillColor': 'transparent',
                        'color': 'black',
                        'weight': '1'
                    },
                    tooltip=folium.GeoJsonTooltip(
                        fields=['postcode'],
                        aliases=['Postcode'],
                        localize=True
                    ),
                    highlight_function=lambda x: {
                        'weight': 3,
                        'color': 'red'
                    },
                ).add_to(m)

        # Laagcontroles toevoegen
        folium.LayerControl().add_to(m)

        # Display map en vang events op
        map_data = st_folium(m, width=800, height=500)

        # Update selected_buurt als er op de kaart wordt geklikt
        if map_data.get('last_active_drawing'):
            clicked_feature = map_data['last_active_drawing']
            if 'properties' in clicked_feature and 'postcode' in clicked_feature['properties']:
                selected_buurt = clicked_feature['properties']['postcode']
                if selected_buurt in df['PC5'].values:
                    st.session_state.selected_buurt = selected_buurt

    except Exception as e:
        st.error(f"Error in kaart sectie: {e}")

# Rechter kolom voor de grafiek
with col2:
    try:
        if 'PC5' not in df.columns:
            st.error("PC5 kolom niet gevonden in de data")
            st.stop()

        buurten = df['PC5'].tolist()
        
        # Gebruik de geselecteerde buurt van de kaart als die er is
        default_index = (buurten.index(st.session_state.selected_buurt) 
                        if st.session_state.selected_buurt in buurten 
                        else 0)

        buurt_selectie = st.selectbox(
            "Selecteer een PC5:",
            buurten,
            index=default_index
        )

        # Maak grafiek
        df_buurt = df[df['PC5'] == buurt_selectie]
        df_buurt = df_buurt.select_dtypes(include=['float64', 'int64'])
        
        fig = px.bar(
            df_buurt.T,
            orientation='h',
            width=900,
            height=600,
            title=f'Scores voor {buurt_selectie}'
        )

        fig.update_layout(
            xaxis_range=[-4, 4],
            xaxis_title="Score",
            yaxis_title="Indicator",
            showlegend=False
        )
        
        st.plotly_chart(fig)

    except Exception as e:
        st.error(f"Error in grafiek sectie: {e}")
