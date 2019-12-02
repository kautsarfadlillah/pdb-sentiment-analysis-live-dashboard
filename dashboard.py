from pymongo import MongoClient
import dash
from dash.dependencies import Output, Input
import dash_core_components as dcc
import dash_html_components as html
import plotly
import plotly.graph_objs as go
import sqlite3
import pandas as pd
from pandas import DataFrame
import numpy as np

client = MongoClient('localhost', 27017)
database = client['pdb']
table = database['sentiment']
table_pos = database['pos_word']

app_colors = {
    'background': '#0C0F0A',
    'text': '#FFFFFF',
    'sentiment-plot':'#000000',
    'volume-bar':'#FBFC74',
    'someothercolor':'#FF206E',
}

app = dash.Dash(__name__)
app.layout = html.Div(
    [html.Div(className='container-fluid', 
    children=[html.H1('Gojek Live Sentiment Analysis on Twitter', style={'font-family':"verdana", 'color':"#000000"} ),
    html.P('ini oke banget loh!', style={'font-family':"verdana", 'color':"#000000"}), html.Hr()],
    style = {'text-align': 'center'} ),
    html.Div(className='container-fluid', 
    children=[html.Div(dcc.Graph(id='live-graph', animate=False))]),
    dcc.Interval(
        id='graph-update',
        interval= 2*1000
    )
    ]
    )

#@app.callback(Output('live-graph', 'figure'),
#[Input('graph-update', 'interval')])
def update_graph_scatter(x):
    #df = DataFrame(list(table_pos.find().sort('count', -1))
    #df = df.drop(['_id'], axis=1)
    X = np.arange(10)
    Y =X**2
    data = go.Scatter(
        x=X,
        y=Y,
        name='Sentiment',
        mode= 'lines',
        line = dict(color = (app_colors['sentiment-plot']),
        width = 4))
    return go.Figure(data).show()

if __name__ == '__main__':
    app.run_server(debug=True)