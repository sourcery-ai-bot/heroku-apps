from model import CustomOpTfPredictor as Model

import re
import pandas as pd
import plotly.express as px

import dash
import dash_table
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

# Load the Model
model_dir = 'models/1'
pred_model = Model(model_dir)

# Setup the Dash App
external_stylesheets = [dbc.themes.LITERA
                        ]  #'https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# Google Adsense
app.index_string = """
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        <script data-ad-client="ca-pub-3660120286814600" async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js"></script>
        {%favicon%}
        {%css%}
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
"""

# Server
server = app.server

# App Layout
app.layout = html.Table([
    html.Tr([
        html.H1(html.Center(html.B('Boy or Girl?'))),
        html.Br(),
        html.Div(
            dbc.Input(id='names',
                      placeholder='Enter names separated by space or comma',
                      style={'width': '700px'})),
        html.Br(),
        html.Center(
            dbc.Button(
                'Submit', id='submit-button', n_clicks=0, color='primary')),
        html.Br(),
        dcc.Loading(id='table-loading',
                    type='default',
                    children=html.Div(id='predictions',
                                      children=[],
                                      style={'width': '700px'})),
        dcc.Store(id='selected-names'),
        html.Br(),
        dcc.Loading(id='chart-loading',
                    type='default',
                    children=html.Div(id='bar-plot', children=[]))
    ])
],
                        style={
                            'marginLeft': 'auto',
                            'marginRight': 'auto'
                        })


# Callbacks
@app.callback(
    [Output('predictions', 'children'),
     Output('selected-names', 'data')], Input('submit-button', 'n_clicks'),
    State('names', 'value'))
def predict(n_clicks, value):
    # Split on all non-alphabet characters
    names = re.findall(r"\w+", value)

    # Restrict to first 10 names only
    names = names[:10]

    # Predictions
    pred_df = pd.DataFrame(pred_model.predict(names)).drop_duplicates()

    return [
        dash_table.DataTable(
            id='pred-table',
            columns=[{
                'name': col,
                'id': col,
            } for col in pred_df.columns],
            data=pred_df.to_dict('records'),
            filter_action="native",
            filter_options={"case": "insensitive"},
            sort_action="native",  # give user capability to sort columns
            sort_mode="single",  # sort across 'multi' or 'single' columns
            page_current=0,  # page number that user is on
            page_size=10,  # number of rows visible per page
            style_cell={
                'fontFamily': 'Open Sans',
                'textAlign': 'center',
                'padding': '10px',
                'backgroundColor': 'rgb(255, 255, 204)',
                'height': 'auto',
                'font-size': '16px'
            },
            style_header={
                'backgroundColor': 'rgb(0, 0, 255)',
                'color': 'white',
                'textAlign': 'center'
            },
            export_format='csv'
        )
    ], names


@app.callback(
    Output('bar-plot', 'children'),
    [Input('predictions', 'children'),
     Input('selected-names', 'data')])
def bar_plot(data, selected_names):
    # Bar Chart
    data = pd.DataFrame(data[0]['props']['data'])
    fig = px.bar(data,
                 x="Probability",
                 y="Name",
                 color='Boy or Girl?',
                 orientation='h',
                 color_discrete_map={
                     'Boy': 'dodgerblue',
                     'Girl': 'lightcoral'
                 })

    fig.update_layout(title={
        'text': 'Confidence in Prediction',
        'x': 0.5
    },
                      yaxis={
                          'categoryorder': 'array',
                          'categoryarray': selected_names,
                          'autorange': 'reversed',
                      },
                      xaxis={'range': [0, 1]},
                      font = {'size': 14},
                      width=700)

    return [dcc.Graph(figure=fig)]


if __name__ == '__main__':
    app.run_server(debug=True)