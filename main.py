# -*- coding: utf-8 -*-
"""
Created on Sun Jun  7 13:12:31 2020

@author: Adrian
"""

import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px

DATA_URL = ("Motor_Vehicle_Collisions_-_Crashes.csv")

#st.markdown("## Aquí estoy escribiendo markdown")

st.title("Colisiones de vehículos de motor en New York City")

st.markdown("Esta aplicación es un tablero Streamlit que se puede usar "
            "para analizar colisiones de vehículos de motor en NYC 🗽💥🚗")

#Cargamos los datos en el navegador
@st.cache(persist=True) #Para omitir calculos costosos
def load_data(nrows):
    #Cargamos el dataset
    data = pd.read_csv(DATA_URL, nrows = nrows, parse_dates = [['CRASH_DATE','CRASH_TIME']])
    #Eliminamos los valores faltantes para las columnas indicadas
    data.dropna(subset=['LATITUDE','LONGITUDE'], inplace = True)
    #Convertimos a minusculas
    lowercase = lambda x: str(x).lower()
    #Renombramos
    data.rename(lowercase, axis='columns',inplace=True)
    data.rename(columns = {'crash_date_crash_time': 'date/time'}, inplace=True)
    #Devolvemos los datos
    return data

#Se hace la llamada a la funcion que carga el dataset
data = load_data(100000)
#Ocurre la verificacion del un check para mostrar los datos.

original_data = data

#hacemos una nueva pregunta
st.header("¿Dónde está la mayoría de las personas heridas en NYC?")
#Creamos una variable para determinar el numero de heridos en un lugar
#para esto utilizamos un slider que controla desde 0 a 19
#(el 19 es justificado por el investigador del curso)

injured_people = st.slider("Número de personas heridas en colisiones de vehículos", 0, 19)
#filtramos los valores y lo mostramos en un
#mapa interactivo de acuerdo a las latitudes y longitudes
st.map(data.query("injured_persons > = @injured_people")[["latitude","longitude"]].dropna(how="any"))

st.header("¿Cuántas colisiones ocurren durante un tiempo determinado del día?")
#mostramos un seleccionador de horas para hacer la proyeccion
hour = st.slider("Hora del día", 0,23)
#hour = st.sidebar.slider("Hora de mirar", 0,23)
data = data[data['date/time'].dt.hour == hour]

#visualizamos informacion
st.markdown("Colisiones de vehículos entre %i:00 y %i:00"%(hour, (hour + 1) % 24))
#le damos estilo al mapa mostrado
midpoint = (np.average(data['latitude']), np.average(data['longitude']))
st.write(pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state={
        "latitude": midpoint[0],
        "longitude":midpoint[1],
        "zoom":11,
        "pitch": 50
    },
    layers = [
        pdk.Layer(
            "HexagonLayer",
            data=data[['date/time', 'latitude', 'longitude']],
            get_position = ['longitude', 'latitude'],
            radius = 100,
            extruded = True,
            pickable = True,
            elevation_scale = 4,
            elevation_range=[1,1000]
        ),
    ],

))
#Histogramas
st.subheader("Desglose por minuto entre %i:00 y %i:00" % (hour, (hour + 1)%24))
filtered = data[
    (data['date/time'].dt.hour >= hour) & (data['date/time'].dt.hour < (hour + 1))
]

hist = np.histogram(filtered['date/time'].dt.minute, bins=60, range=(0,60))[0]
chart_data = pd.DataFrame({'minute': range(60),'crashes':hist})
fig = px.bar(chart_data, x = 'minute', y='crashes', hover_data = ['minute', 'crashes'],height = 400)
st.write(fig)

st.header("Las 5 calles peligrosas para los afectados")
select = st.selectbox('Tipo de personas afectadas', ['Peatones', 'Ciclistas', 'Motoristas'])

if select == 'Peatones':
    st.write(original_data.query("injured_pedestrians >= 1")[["on_street_name", "injured_pedestrians"]].sort_values(by = ['injured_pedestrians'], ascending=False).dropna(how ='any')[:5])
elif select == 'Ciclistas':
    st.write(original_data.query("injured_cyclists >= 1")[["on_street_name", "injured_cyclists"]].sort_values(by = ['injured_cyclists'], ascending=False).dropna(how ='any')[:5])
else:
    st.write(original_data.query("injured_motorists >= 1")[["on_street_name", "injured_motorists"]].sort_values(by = ['injured_motorists'], ascending=False).dropna(how ='any')[:5])

if st.checkbox('Mostrar datos sin procesar', False):
    st.subheader('Datos sin procesar')
    st.write(data)
