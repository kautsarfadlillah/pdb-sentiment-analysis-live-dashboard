from pymongo import MongoClient
import dash
from dash.dependencies import Output, Input
import dash_core_components as dcc
import dash_html_components as html
import plotly
import plotly.graph_objs as go
import sqlite3

client = MongoClient('localhost', 27017)
database = client['pdb']
table = database['sentiment']

app_colors = {
    'background': '#0C0F0A',
    'text': '#FFFFFF',
    'sentiment-plot':'#41EAD4',
    'volume-bar':'#FBFC74',
    'someothercolor':'#FF206E',
}

app = dash.Dash(__name__)
app.layout = html.Div(
    [html.Div(className='row', children=[html.Div(id='sentiment-pie', animate=False), className='col s12 m6 16')]
    
    ),
    dcc.Interval(
        id='sentiment-pie-update',
        interval= 2*1000
    )
    
    ]
)
@app.callback(Output('sentiment-pie', 'figure'),
[Input('sentiment-pie-update', 'n_intervals')])
def update_pie_chart(x):
    pos = 0
    neg = 0
    net = 0
    for obj in table.find():
        if obj['sentiment'] > 0.2 :
            pos+=1
        elif obj['sentiment'] <= 0.2 and obj['sentiment'] >= -0.2 :
            net+=1
        elif obj['sentiment'] < -0.2:
            neg+=1
    labels = ['Positive','Negative', 'Neutral']
    values = [pos,neg,net]
    colors = ['#007F25', '#800000', '#41EAD4' ]

    trace = go.Pie(labels=labels, values=values,hoverinfo='label+percent', textinfo='value', 
    textfont=dict(size=20, color=app_colors['text']),marker=dict(colors=colors, 
    line=dict(color=app_colors['background'], width=2)))

    return {"data":[trace],'layout' : go.Layout(
        title='Positive vs Negative vs Netral sentiment for gojek',
        font={'color':app_colors['text']}, plot_bgcolor = app_colors['background'],
        paper_bgcolor = app_colors['background'], showlegend=True)}


if __name__ == '__main__':
    app.run_server(debug=True)