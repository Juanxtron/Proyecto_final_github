import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State, ALL
import plotly.graph_objs as go
import psycopg2
import pandas as pd

engine = psycopg2.connect(
    dbname="icfes",
    user="postgres",
    password="proyecto2",
    host="proyecto-2.cjgscwkesde4.us-east-1.rds.amazonaws.com",
    port="5432"
)

cursor = engine.cursor()

query = """
SELECT * 
FROM resultados 
WHERE (cole_depto_ubicacion = 'BOGOTÁ' AND periodo IN ('20194', '20191')) OR (cole_depto_ubicacion = 'BOGOTA' AND periodo IN ('20194', '20191'));"""

df = pd.read_sql_query(query, engine) 

import pandas as pd

# Suponiendo que df es tu DataFrame
# Reemplaza 'df' con el nombre real de tu DataFrame

# Eliminar todas las filas que contienen valores nulos
df_sin_nulos = df.dropna()

# Ahora df_sin_nulos contiene el DataFrame original sin filas que tengan valores nulos

# Listado de columnas a eliminar
columnas_a_eliminar = [
    'estu_tipodocumento',
    'estu_consecutivo',
    'cole_cod_dane_establecimiento',
    'cole_cod_dane_sede',
    'cole_cod_depto_ubicacion',
    'cole_cod_mcpio_ubicacion',
    'cole_codigo_icfes',
    'estu_cod_depto_presentacion',
    'estu_cod_mcpio_presentacion',
    'estu_cod_reside_depto',
    'estu_cod_reside_mcpio',
    'desemp_ingles',
    'cole_depto_ubicacion',
    "estu_privado_libertad",
    "estu_estudiante",
    "punt_global"
]

# Eliminación de las columnas
df_sin_nulos.drop(columns=columnas_a_eliminar, inplace=True)


puntaje_columnas = ['punt_ingles', 'punt_matematicas', 'punt_sociales_ciudadanas', 'punt_c_naturales', 'punt_lectura_critica']
for col in puntaje_columnas:
    df_sin_nulos[col] = pd.to_numeric(df_sin_nulos[col], errors='coerce')

# Eliminar las filas donde la columna "fami_estratovivienda" tiene el valor "Sin Estrato"
df_sin_nulos = df_sin_nulos[df_sin_nulos['fami_estratovivienda'] != "Sin Estrato"]
