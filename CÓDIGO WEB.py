{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "613abdad",
   "metadata": {},
   "outputs": [],
   "source": [
    "import streamlit as st\n",
    "import pandas as pd\n",
    "import altair as alt\n",
    "#from openpyxl import Workbook\n",
    "import pip\n",
    "pip.main([\"install\", \"openpyxl\"])# esta linea y la de arriba me ayudaron a poder ejecutarlo en streamlit, casi que no!\n",
    "\n",
    "n = 14\n",
    "\n",
    "Activo = \"USD-COP\"\n",
    "\n",
    "df = pd.read_excel(Activo+\".xlsx\")\n",
    "\n",
    "df['Var'] = df[\"Precio Cierre\"].diff()\n",
    "\n",
    "df['M. Ganancias'] = 0 # se crea la columna de M. Ganancias y se vuelve 0\n",
    "\n",
    "df.loc[df['Var']<0,['M. Ganancias']] = 0  #Si var es menor a 0 entonces que me deje un 0\n",
    "df.loc[df['Var']>0,['M. Ganancias']] = df['Var'] #si var es mayor a 0 entonces que me deje var\n",
    "\n",
    "df['M. Perdidas'] = 0 #columna de perdidas\n",
    "\n",
    "df.loc[df['Var']<0,['M. Perdidas']] = df['Var'] #Si var es menor a 0 entonces var sino 0\n",
    "df.loc[df['Var']>0,['M. Perdidas']] = 0 # si var es mayor a 0 entonces 0\n",
    "\n",
    "df['M. Perdidas'] = df['M. Perdidas'].abs() # valor absoluto en perdidas\n",
    "\n",
    "EMA_M_GANANCIAS = df['M. Ganancias'].rolling(n).mean()\n",
    "EMA_M_PERDIDAS = df['M. Perdidas'].rolling(n).mean()\n",
    "\n",
    "rs = EMA_M_GANANCIAS/EMA_M_PERDIDAS\n",
    "\n",
    "df['RSI'] = 100-(100/(1+rs))\n",
    "\n",
    "df['SMA14'] = df['Precio Cierre'].rolling(14).mean()\n",
    "df['SMA50'] = df['Precio Cierre'].rolling(50).mean()\n",
    "df['SMA200'] = df['Precio Cierre'].rolling(200).mean()\n",
    "\n",
    "df['EMA14'] = df['Precio Cierre'].ewm(span = 14,adjust = False).mean()\n",
    "df['EMA50'] = df['Precio Cierre'].ewm(span = 50,adjust = False).mean()\n",
    "df['EMA200'] = df['Precio Cierre'].ewm(span = 200,adjust = False).mean()\n",
    "\n",
    "#df['Cap. Bursatil'] = df['Precio Cierre']*df['No. Acciones']\n",
    "\n",
    "#df.to_excel(Activo+\" DONE\"+\".xlsx\",index = False,sheet_name = \"RESULTADO\")\n",
    "\n",
    "#df.head(16)\n",
    "\n",
    "st.dataframe(df)"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3 (ipykernel)",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.9.12"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
