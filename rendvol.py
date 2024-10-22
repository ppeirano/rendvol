import yfinance as yf
import pandas as pd
import numpy as np
import streamlit as st
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

# Función para descargar los datos
def descargar_datos(activos, start, end):
    data = yf.download(activos, start=start, end=end)['Adj Close']
    return data

# Función para calcular el rendimiento del periodo y la volatilidad anualizada
def calcular_rendimiento_volatilidad(data):
    # Rendimiento del periodo
    rendimiento_periodo = (data.iloc[-1] / data.iloc[0]) - 1
    
    # Volatilidad anualizada
    log_returns = np.log(data / data.shift(1))
    volatilidad_anualizada = log_returns.std() * np.sqrt(252)
    
    return rendimiento_periodo, volatilidad_anualizada

# Función para determinar la fecha de inicio según el periodo seleccionado
def obtener_fecha_inicio(periodo):
    hoy = datetime.today()
    if periodo == 'Última semana':
        return hoy - timedelta(weeks=1)
    elif periodo == 'Último mes':
        return hoy - timedelta(days=30)
    elif periodo == 'Último trimestre':
        return hoy - timedelta(days=90)
    elif periodo == 'Último año':
        return hoy - timedelta(days=365)
    elif periodo == 'Últimos 2 años':
        return hoy - timedelta(days=365*2)
    elif periodo == 'Últimos 5 años':
        return hoy - timedelta(days=365*5)
    elif periodo == 'Últimos 10 años':
        return hoy - timedelta(days=365*10)
    else:
        return hoy - timedelta(days=365)  # Default to 1 year if none selected

# Configurar la aplicación Streamlit
st.title('Rendimiento y Volatilidad Anualizada')

# Entrada de los tickers (por defecto se incluyen los activos solicitados)
activos = st.text_input('Ingresa los tickers de los activos separados por comas', 
                        'SPY, QQQ, DIA, IWM, XLK, XLE, XLY, XLV, XLF, KO, MCD, PEP, MSFT, AAPL, VIST')

# Seleccionar el periodo de análisis
periodo = st.selectbox('Selecciona el periodo de tiempo', 
                       ['Última semana', 'Último mes', 'Último trimestre', 'Último año', 
                        'Últimos 2 años', 'Últimos 5 años', 'Últimos 10 años'])

# Obtener las fechas según el periodo seleccionado
start_date = obtener_fecha_inicio(periodo)
end_date = datetime.today()

# Botón para realizar el análisis
if st.button('Analizar'):
    activos_lista = [activo.strip() for activo in activos.split(',')]
    datos = descargar_datos(activos_lista, start_date, end_date)
    
    # Crear listas para almacenar los resultados
    rendimiento_periodo = []
    volatilidad_anualizada = []
    
    # Calcular rendimiento del periodo y volatilidad para cada activo
    for activo in activos_lista:
        data_activo = datos[activo]
        rendimiento, volatilidad = calcular_rendimiento_volatilidad(data_activo)
        rendimiento_periodo.append(rendimiento)
        volatilidad_anualizada.append(volatilidad)
    
    # Crear un DataFrame con los resultados
    resultados = pd.DataFrame({
        'Activos': activos_lista,
        'Rendimiento del Periodo': rendimiento_periodo,
        'Volatilidad Anualizada': volatilidad_anualizada
    })
    
    # Mostrar los resultados en la tabla
    st.write('Resultados del análisis:')
    st.dataframe(resultados)
    
    # Calcular la recta de regresión
    x = resultados['Volatilidad Anualizada']
    y = resultados['Rendimiento del Periodo']
    coef = np.polyfit(x, y, 1)
    regresion_linea = np.poly1d(coef)
    
    # Crear el scatter plot con Plotly
    fig = px.scatter(resultados, 
                     x='Volatilidad Anualizada', 
                     y='Rendimiento del Periodo',
                     text='Activos',
                     title=f'Rendimiento del Periodo vs. Volatilidad Anualizada ({periodo})',
                     labels={'Volatilidad Anualizada': 'Volatilidad Anualizada', 
                             'Rendimiento del Periodo': 'Rendimiento del Periodo'})
    
    # Agregar la recta de regresión al gráfico
    fig.add_trace(go.Scatter(x=x, y=regresion_linea(x), 
                             mode='lines', 
                             name='Recta de Regresión',
                             line=dict(color='red', dash='dash')))
    
    # Ajustar el tamaño del texto de las etiquetas
    fig.update_traces(textposition='top center', marker=dict(size=12, opacity=0.8))
    fig.update_layout(autosize=False, width=800, height=600)
    
    # Mostrar el gráfico en la aplicación
    st.plotly_chart(fig)
