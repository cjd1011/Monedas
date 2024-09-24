import streamlit as st
import pandas as pd
import altair as alt
import openpyxl
from openpyxl import Workbook
import pip
import datetime
import plotly.express as px
import matplotlib.pyplot as plt
import pickle
from pathlib import Path
import plotly.graph_objs as go

import ssl
ssl._create_default_https_context = ssl._create_unverified_context

import altair as alt

n = 14

Activo = "USD-COP"

Base_Historica = pd.read_excel("USD-COP.xlsx")

Base_Historica['Var'] = Base_Historica["Precio Cierre"].diff()

ordenar_df = ['fecha', 'Precio Cierre']

Base_Historica1 = Base_Historica[ordenar_df]

datosgov = pd.read_csv('https://www.datos.gov.co/api/views/dit9-nnvp/rows.csv?accessType=DOWNLOAD&bom=true&format=true.csv')

datosgov.to_excel('datosgov.xlsx', index=False)

datosgov['FECHA'] = pd.to_datetime(datosgov['FECHA'], format='%d/%m/%Y')  # ordenar formato

datosgov.rename({'TRM': 'Precio Cierre', 'FECHA': 'fecha'}, axis=1, inplace=True)  # cambios los nombres de las columnas

concatenacion = pd.concat([Base_Historica1, datosgov], ignore_index=True)  # El ignore_index me sirve para que se resetee el index y no se me dañe desde el iloc

concatenacion['Nemotecnico'] = "USD/COP"

ordenar_concatenacion = ['Nemotecnico', 'fecha', 'Precio Cierre']

df = concatenacion[ordenar_concatenacion]

df['Var'] = df["Precio Cierre"].diff()

df['M. Ganancias'] = 0  # se crea la columna de M. Ganancias y se vuelve 0

df.loc[df['Var'] < 0, ['M. Ganancias']] = 0  # Si var es menor a 0 entonces que me deje un 0
df.loc[df['Var'] > 0, ['M. Ganancias']] = df['Var']  # si var es mayor a 0 entonces que me deje var

df['M. Perdidas'] = 0  # columna de perdidas

df.loc[df['Var'] < 0, ['M. Perdidas']] = df['Var']  # Si var es menor a 0 entonces var sino 0
df.loc[df['Var'] > 0, ['M. Perdidas']] = 0  # si var es mayor a 0 entonces 0

df['M. Perdidas'] = df['M. Perdidas'].abs()  # valor absoluto en perdidas

EMA_M_GANANCIAS = df['M. Ganancias'].rolling(n).mean()
EMA_M_PERDIDAS = df['M. Perdidas'].rolling(n).mean()

rs = EMA_M_GANANCIAS / EMA_M_PERDIDAS

df['RSI'] = 100 - (100 / (1 + rs))

df['SMA14'] = df['Precio Cierre'].rolling(14).mean()
df['SMA50'] = df['Precio Cierre'].rolling(50).mean()
df['SMA200'] = df['Precio Cierre'].rolling(200).mean()

df['EMA14'] = df['Precio Cierre'].ewm(span=14, adjust=False).mean()
df['EMA50'] = df['Precio Cierre'].ewm(span=50, adjust=False).mean()
df['EMA200'] = df['Precio Cierre'].ewm(span=200, adjust=False).mean()

#Vamos a usar los siguientes dos abajo para el MACD
df['EMA12'] = df['Precio Cierre'].ewm(span=12, adjust=False).mean() ##Para el MACD
df['EMA26'] = df['Precio Cierre'].ewm(span=26, adjust=False).mean() ##Para el MACD

#Crear la 'Linea MACD'

df['MACD_line'] = df['EMA12'] - df['EMA26']

# Calcular la Signal Line
df['Signal_Line'] = df['MACD_line'].ewm(span=9, adjust=False).mean()

# Calcular el Histograma
df['Histograma'] = df['MACD_line'] - df['Signal_Line']


# Crear la figura interactiva con Plotly
fig = go.Figure()

# Agregar la línea MACD
fig.add_trace(go.Scatter(x=df['fecha'], y=df['MACD_line'], mode='lines', name='MACD Line', line=dict(color='blue')))

# Agregar la Signal Line
fig.add_trace(go.Scatter(x=df['fecha'], y=df['Signal_Line'], mode='lines', name='Signal Line', line=dict(color='red')))

# Agregar el Histograma como barras
fig.add_trace(go.Bar(x=df['fecha'], y=df['Histograma'], name='Histograma', marker_color='grey', opacity=0.5))

# Configurar el diseño del gráfico

fig.update_layout(
    title='MACD con Signal Line y Histograma (USD/COP)',
    xaxis_title='Fecha',
    yaxis_title='Valor MACD',
    showlegend=True,
    template='plotly_white',
    height=600,
    xaxis=dict(
        rangeslider=dict(visible=True),
        type='date'  # Asegúrate de que el eje x sea de tipo fecha
    )
)


fig.add_shape(
    type="line",
    x0=df['fecha'].min(),
    y0=0,
    x1=df['fecha'].max(),
    y1=0,
    line=dict(color="black", width=1)
)





elegir_columnas = ['Nemotecnico', 'fecha', 'Precio Cierre', 'RSI', 'EMA14', 'EMA50', 'EMA200']

df1 = df[elegir_columnas].sort_values(by=['fecha'], ascending=False)
df1['Mes'] = df1['fecha'].dt.month.astype(int)  # Crear columna nombre mes
df1['Año'] = df1['fecha'].dt.year  # Crear columna año
Year_1 = df1['Año'].unique().tolist()

Meses_1 = df1['Mes'].unique().tolist()

st.title('Análisis del :blue[USD/COP] :bar_chart:')

st.subheader('Realizado por: Camilo Diaz:briefcase:')

year_selector = st.slider('Años a filtrar:',
                          min_value=min(Year_1),
                          max_value=max(Year_1),
                          value=(min(Year_1), max(Year_1)))

meses_selector = st.slider('Meses:',
                           min_value=min(Meses_1),
                           max_value=max(Meses_1),
                           value=(min(Meses_1), max(Meses_1)))

izquierda, centro, derecha = st.columns(3)  # cuantas columnas para los datos relevantes (minimo, maximo, promedio)

# Filtrar los datos según la selección del usuario
mask = (df1['Año'].between(*year_selector) & df1['Mes'].between(*meses_selector))
df_filtrado = df1[mask]

with izquierda:
    precio_minimo = df_filtrado['Precio Cierre'].min()  # precio minimo del usd/cop
    st.metric("Valor Mínimo Histórico", precio_minimo)  # Graficarlo

with centro:
    precio_promedio = df_filtrado['Precio Cierre'].mean()
    precio_promedio_r = round(precio_promedio, 2)  # solo dos decimales...
    st.metric("Valor Promedio Histórico", precio_promedio_r)

with derecha:
    precio_maximo = df_filtrado['Precio Cierre'].max()
    st.metric("Valor Máximo Histórico", precio_maximo)  # Graficarlo

# Remover las columnas 'Mes' y 'Año' antes de mostrar el DataFrame
df_filtrado = df_filtrado.drop(columns=['Mes', 'Año'])

st.dataframe(df_filtrado, hide_index=True)

@st.cache
def convert_df(df_filtrado):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df_filtrado.to_csv().encode('utf-8')

csv = convert_df(df_filtrado)

st.download_button(
    label="Download data as CSV",
    data=csv,
    file_name='usdcop_df.csv',
    mime='text/csv',
)

df2 = df_filtrado.melt(id_vars=['Nemotecnico', 'fecha'],
                       var_name="Indicador",
                       value_name="valor")

Activo = st.multiselect(
    "Seleccione el Activo:",
    options=df2['Indicador'].unique(),
    default=["Precio Cierre", "EMA14", "EMA50", "EMA200"]  # Por default, seleccionamos todas las medias móviles y el precio
)

df_seleccion = df2.query("Indicador == @Activo")  # el primero es la columna y el segundo es el selector

fig1 = px.line(x='fecha', y='valor', title='Gráfica USD/COP', data_frame=df_seleccion, color='Indicador')

st.write(fig1, use_container_width=True)

# Gráfico de RSI separado
#df_rsi = df_filtrado[['fecha', 'RSI']]

#fig2 = px.line(df_rsi, x='fecha', y='RSI', title='RSI')

#st.write(fig2, use_container_width=True)

# Mostrar la gráfica del MACD en Streamlit
st.plotly_chart(fig)

# Sección interactiva para la conversión de divisas
st.subheader('Convertidor de divisas:')

conversion_type = st.radio(
    "Selecciona el tipo de conversión:",
    ('De Pesos Colombianos a Dólares', 'De Dólares a Pesos Colombianos')
)

latest_price = df1['Precio Cierre'].iloc[0]

if conversion_type == 'De Pesos Colombianos a Dólares':
    amount = st.number_input('Ingrese la cantidad en Pesos Colombianos:')
    converted_amount = amount / latest_price
    st.write(f'El monto en dólares es: {converted_amount:,.2f} USD')
else:
    amount = st.number_input('Ingrese la cantidad en Dólares:')
    converted_amount = amount * latest_price
    st.write(f'El monto en Pesos Colombianos es: {converted_amount:,.2f} COP')
