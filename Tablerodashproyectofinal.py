from Limpiezadatos import df_sin_nulos

import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

# Convertir columnas de puntajes a numéricas
puntaje_columnas = ['punt_ingles', 'punt_matematicas', 'punt_sociales_ciudadanas', 'punt_c_naturales', 'punt_lectura_critica']

# Inicializar la aplicación Dash
app = dash.Dash(__name__)

# Definir el layout de la aplicación
app.layout = html.Div([
    html.H1("Resultados Competencias Icfes 2019 por Colegio y Sede  "),

    html.Div([
        html.Label('Seleccione el Colegio:'),
        dcc.Dropdown(
            id='dropdown-colegio',
            options=[{'label': colegio, 'value': colegio} for colegio in df_sin_nulos['cole_nombre_establecimiento'].unique()],
            value=None
        ),
    ]),

    html.Div([
        html.Label('Seleccione la Sede:'),
        dcc.Dropdown(
            id='dropdown-sede',
            options=[],
            value=None
        ),
    ]),

    html.Div(id='info-colegio'),

    dcc.Graph(id='grafico-puntajes'),

    html.Div([
        html.H2("Influencia del estrato y personas en el hogar en los resultados por competencia"),
        html.Label('Seleccione la Competencia:'),
        dcc.Dropdown(
            id='dropdown-competencia',
            options=[{'label': columna, 'value': columna} for columna in puntaje_columnas],
            value=puntaje_columnas[0]
        ),
    ]),

    dcc.Graph(id='grafico-estrato'),
    dcc.Graph(id='grafico-personas-hogar'),
])

# Callback para actualizar las opciones de la sede
@app.callback(
    Output('dropdown-sede', 'options'),
    Input('dropdown-colegio', 'value')
)
def set_sede_options(selected_colegio):
    if selected_colegio:
        filtered_df = df_sin_nulos[df_sin_nulos['cole_nombre_establecimiento'] == selected_colegio]
        return [{'label': sede, 'value': sede} for sede in filtered_df['cole_nombre_sede'].unique()]
    return []

# Callback para mostrar la información del colegio y actualizar el gráfico
@app.callback(
    [Output('info-colegio', 'children'),
     Output('grafico-puntajes', 'figure'),
     Output('grafico-estrato', 'figure'),
     Output('grafico-personas-hogar', 'figure')],
    [Input('dropdown-colegio', 'value'),
     Input('dropdown-sede', 'value'),
     Input('dropdown-competencia', 'value')]
)
def update_output(selected_colegio, selected_sede, selected_competencia):
    if selected_colegio and selected_sede:
        filtered_df = df_sin_nulos[(df_sin_nulos['cole_nombre_establecimiento'] == selected_colegio) & (df_sin_nulos['cole_nombre_sede'] == selected_sede)]

        num_hombres = filtered_df[filtered_df['estu_genero'] == 'M'].shape[0]
        num_mujeres = filtered_df[filtered_df['estu_genero'] == 'F'].shape[0]
        bilingue = filtered_df['cole_bilingue'].iloc[0] if not filtered_df['cole_bilingue'].isnull().all() else 'N'
        calendario = filtered_df['cole_calendario'].iloc[0]
        area_ubicacion = filtered_df['cole_area_ubicacion'].iloc[0]
        sede_principal = filtered_df['cole_sede_principal'].iloc[0] if not filtered_df['cole_sede_principal'].isnull().all() else 'N'

        info = html.Div([
            html.P(f"Número de hombres: {num_hombres}"),
            html.P(f"Número de mujeres: {num_mujeres}"),
            html.P(f"Bilingüe: {'Sí' if bilingue == 'S' else 'No'}"),
            html.P(f"Calendario: {calendario}"),
            html.P(f"Área de ubicación: {area_ubicacion}"),
            html.P(f"Sede principal: {'Sí' if sede_principal == 'S' else 'No'}")
        ])

        # Calcular el promedio de los puntajes por materia
        promedio_puntajes = filtered_df[puntaje_columnas].mean().reset_index()
        promedio_puntajes.columns = ['Materia', 'Puntaje']

        # Crear gráfico de barras horizontales
        fig_barras = px.bar(
            promedio_puntajes,
            x='Puntaje',
            y='Materia',
            orientation='h',
            title='Promedio de Puntajes por Materia'
        )

        # Gráfica de línea para relación con estrato
        estrato_promedios = filtered_df.groupby('fami_estratovivienda')[selected_competencia].mean().reset_index()
        fig_estrato = px.line(estrato_promedios, x='fami_estratovivienda', y=selected_competencia, title=f'Relación entre {selected_competencia} y Estrato')

        # Gráfica de línea para relación con personas en el hogar
        personas_hogar_promedios = filtered_df.groupby('fami_personashogar')[selected_competencia].mean().reset_index()
        fig_personas_hogar = px.line(personas_hogar_promedios, x='fami_personashogar', y=selected_competencia, title=f'Relación entre {selected_competencia} y Personas en el Hogar')

        return info, fig_barras, fig_estrato, fig_personas_hogar
    return '', {}, {}, {}

# Ejecutar la aplicación
if __name__ == '__main__':
    app.run_server(debug=True, port=8050)
