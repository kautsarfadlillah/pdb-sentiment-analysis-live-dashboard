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


client = MongoClient('localhost', 27017)
database = client['pdb']
table = database['sentiment']
table_pos = database['pos_word']

app_colors = {
    'background': '#0C0F0A',
    'text': '#FFFFFF',
    'sentiment-plot':'#41EAD4',
    'volume-bar':'#FBFC74',
    'someothercolor':'#FF206E',
}

app = dash.Dash(__name__)
app.layout = html.Div(
    [html.Div(className='row', children=[html.Div(id="recent-tweets-table", className='col s12 m6 16')]
    ),
    dcc.Interval(
        id='recent-table-update',
        interval= 2*1000
    )
    
    ]
)
@app.callback(Output('recent-tweets-table', 'children'),
[Input('recent-table-update', 'n_intervals')])
def update_recent_tweets(x):
    df = DataFrame(list(table_pos.find().sort('count', -1).limit(5)))
    df = df.drop(['_id'], axis=1)
    return generate_table(df)

def generate_table(df):
    return html.Table(className="responsive-table",
    children=[html.Thead(html.Tr(children=[
        html.Th(col.title()) for col in df.columns.values],
        style={'color':app_colors['text']}
        )
        ),
        html.Tbody(
            [
                html.Tr(children=[html.Td(data) for data in d
                ], style={'color':app_colors['text'],
                'background-color':app_colors['background']}
                )
                for d in df.values.tolist()])
                ]
    )


if __name__ == '__main__':
    app.run_server(debug=True)

