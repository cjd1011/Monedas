import streamlit as st
import pandas as pd
import altair as alt
#from openpyxl import Workbook
import pip
pip.main(["install", "openpyxl"])# esta linea y la de arriba me ayudaron a poder ejecutarlo en streamlit, casi que no!

pip.main(["install", "plotly"])
import plotly.express as px #pip install plotly-express

import datetime

import pickle
from pathlib import Path

import altair as alt
#import plotly.graph_objects as go
#import streamlit_authenticator as stauth


n = 14

Activo = "USD-COP"

df = pd.read_excel("USD-COP.xlsx")

df['Var'] = df["Precio Cierre"].diff()

df['M. Ganancias'] = 0 # se crea la columna de M. Ganancias y se vuelve 0

df.loc[df['Var']<0,['M. Ganancias']] = 0  #Si var es menor a 0 entonces que me deje un 0
df.loc[df['Var']>0,['M. Ganancias']] = df['Var'] #si var es mayor a 0 entonces que me deje var

df['M. Perdidas'] = 0 #columna de perdidas

df.loc[df['Var']<0,['M. Perdidas']] = df['Var'] #Si var es menor a 0 entonces var sino 0
df.loc[df['Var']>0,['M. Perdidas']] = 0 # si var es mayor a 0 entonces 0

df['M. Perdidas'] = df['M. Perdidas'].abs() # valor absoluto en perdidas

EMA_M_GANANCIAS = df['M. Ganancias'].rolling(n).mean()
EMA_M_PERDIDAS = df['M. Perdidas'].rolling(n).mean()

rs = EMA_M_GANANCIAS/EMA_M_PERDIDAS

df['RSI'] = 100-(100/(1+rs))

df['SMA14'] = df['Precio Cierre'].rolling(14).mean()
df['SMA50'] = df['Precio Cierre'].rolling(50).mean()
df['SMA200'] = df['Precio Cierre'].rolling(200).mean()

df['EMA14'] = df['Precio Cierre'].ewm(span = 14,adjust = False).mean()
df['EMA50'] = df['Precio Cierre'].ewm(span = 50,adjust = False).mean()
df['EMA200'] = df['Precio Cierre'].ewm(span = 200,adjust = False).mean()

elegir_columnas = ['Nemotecnico','fecha','Precio Cierre','RSI','EMA14','EMA50','EMA200']

df1 = df[elegir_columnas]

#df['Cap. Bursatil'] = df['Precio Cierre']*df['No. Acciones']

#df.to_excel(Activo+" DONE"+".xlsx",index = False,sheet_name = "RESULTADO")

st.title('Análisis del :blue[USD/COP] :bar_chart:')

st.divider()

st.subheader('Realizado por: Camilo Diaz:briefcase:')

st.divider()

#st.slider("This is a slider", df['fecha'])

st.dataframe(df1)

st.divider()

#chart_data = pd.DataFrame(df1, columns = ['fecha','Precio Cierre'])
    
#st.line_chart(chart_data,x= 'fecha', y = 'Precio Cierre')

#line_chart = px.line(x ='fecha', y = 'Precio Cierre', data_frame = df1, title = 'Linea de tendencia', markers = False)
    
#st.write(line_chart)

df1.melt(id_vars=['Nemotecnico','fecha'], 
        var_name="Indicador", 
        value_name="valor")

#fig5 = px.line( x ='fecha', y = 'Precio Cierre', data_frame = df2, title = 'Linea de tendencia', color = 'Nemotecnico',markers = False)


st.write(df1)
