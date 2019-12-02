from pymongo import MongoClient
import dash
import datetime
import dash_table
from dash.dependencies import Output, Input
import dash_core_components as dcc
import dash_html_components as html
import plotly
import plotly.graph_objs as go
import sqlite3
import pandas as pd
from pandas import DataFrame
import numpy as np
import math

client = MongoClient('localhost', 27017)
database = client['pdb']
table = database['sentiment']
table_pos = database['positive_words']
table_neg = database['negative_words']

external_stylesheets = ['https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css']

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
    html.Div([
        dcc.Graph(id='live-update-graph'),
        dcc.Interval(
            id='interval-component',
            
            # Graph updated every 10 seconds
            interval=5*1000, # in milliseconds
            n_intervals=0
        )
    ]),
    html.Div(className='row', children=[html.Div(dcc.Graph(id='sentiment-pie', animate=False), className='col-6'),
    html.Div(id="recent-tweets-table", className='col-6')]
    ),
     dcc.Interval(
        id='sentiment-pie-update',
        interval= 5*1000
    ),
     dcc.Interval(
        id='recent-tweets-update',
        interval=5*1000
    ),
    html.Div(className='row', children=[html.Div(id="positive-table", className='col s12 m6 16')]
    ),
     dcc.Interval(
        id='recent-positive-words-update',
        interval=5*1000
    ),
    html.Div(className='row', children=[html.Div(id="negative-table", className='col s12 m6 16')]
    ),
     dcc.Interval(
        id='recent-negative-words-update',
        interval=5*1000
    ),
    ]
    )
@app.callback(Output('positive-table', 'children'),
[Input('recent-positive-words-update', 'n_intervals')])
def update_recent_tweets(x):
    df = DataFrame(list(table_pos.find().sort('count', -1).limit(5)))
    df = df.drop(['_id'], axis=1)
    return generate_table(df)

@app.callback(Output('negative-table', 'children'),
[Input('recent-negative-words-update', 'n_intervals')])
def update_recent_tweets(x):
    df = DataFrame(list(table_neg.find().sort('count', -1).limit(5)))
    df = df.drop(['_id'], axis=1)
    return generate_table(df)

def generate_table(df):
    positive_table = dash_table.DataTable(
        id='table_sentiment',
        columns=[{"name":i, "id":i} for i in df.columns],
        data=df.to_dict("rows"))
    return positive_table

@app.callback(Output('recent-tweets-table', 'children'),
[Input('recent-tweets-update', 'n_intervals')])
def recent_tweets(a):
    df = pd.DataFrame(list(table.find().sort('date', -1).limit(10)))
    df = df.drop(['_id'], axis=1)
    df = df[['date', 'tweet', 'sentiment']]
    df['date'] = df['date'].apply(lambda dt: dt.strftime("%d %b %Y, %H:%M:%S"))
    recent_table = dash_table.DataTable(
        id='table_sentiment',
        columns=[{"name":i, "id":i} for i in df.columns],
        data=df.to_dict("rows"),
        style_cell=
        {
            'textAlign': 'left',
            },
            style_data={
                'whiteSpace': 'normal',
                'height': 'auto',
                'minWidth': '0px',
                'maxWidth': '150px',
                },
                style_cell_conditional=[
                    {
                        'maxWidth': '10px'
                        }
                        for i in ['date', 'sentiment']
                        ],
                        style_data_conditional=[
                            {
                                "if" : {
                                    'filter_query': '{sentiment} < 0'
                                    },
                                    'backgroundColor' : '#FAD9D9',
                                    'color': 'black',
                                    },
                                    {
                                        "if" : {
                                            'filter_query': '{sentiment} > 0'
                                            },
                                            'backgroundColor' : '#C4F8C3',
                                            'color': 'black',
                                            },
                                            ]
                                            )
    return recent_table

@app.callback(Output('sentiment-pie', 'figure'),
[Input('sentiment-pie-update', 'n_intervals')])
def update_pie_chart(x):
    pos = 0
    neg = 0
    net = 0
    for obj in table.find():
        if obj['sentiment'] > 0.05 :
            pos+=1
        elif obj['sentiment'] <= 0.05 and obj['sentiment'] >= -0.05 :
            net+=1
        elif obj['sentiment'] < -0.05:
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

# Multiple components can update everytime interval gets fired.
@app.callback(Output('live-update-graph', 'figure'),
              [Input('interval-component', 'n_intervals')])
def update_graph_live(n):
    def roundup(x):
        return int(math.ceil(x / 20.0)) * 20
    data = {
        'time': [],
        'positive': [],
        'negative': [],
    }
    current_time = datetime.datetime.now().replace(microsecond=0)
    current_time = current_time + datetime.timedelta(seconds=roundup(current_time.second) - current_time.second)

    time_pointer = current_time - datetime.timedelta(hours=1)
    twitter_data = list(table.find({"date": {"$gt": time_pointer}}).sort('date', 1))

    tweet_index = 0
    while time_pointer < current_time:
        positive_count = 0
        negative_count = 0
        while tweet_index < len(twitter_data) and twitter_data[tweet_index]['date'] < time_pointer:
            if twitter_data[tweet_index]['sentiment'] > 0.05:
                positive_count += 1
            elif twitter_data[tweet_index]['sentiment'] < 0.05:
                negative_count += 1
            tweet_index += 1
        
        data['time'].append(time_pointer)
        data['positive'].append(positive_count)
        data['negative'].append(negative_count)
        time_pointer = time_pointer + datetime.timedelta(seconds=20)
    
    start_index = 0
    for i in range(len(data['positive'])):
        if data['positive'][i] > 0 or data['negative'][i] > 0:
            start_index = i
            break

    trace1 = go.Scatter (
        x=data['time'][start_index:][::-1],
        y=data['positive'][start_index:][::-1],
        name='Positive Sentiment'
    )

    trace2 = go.Scatter (
        x=data['time'][start_index:][::-1],
        y=data['negative'][start_index:][::-1],
        name='Negative Sentiment'
    )

    data = [trace1, trace2]
    layout = go.Layout(
        title=go.layout.Title(
            text='Live Sentiment for \'Gojek\'',
            xref='paper',
            x=0
        ),
        xaxis=go.layout.XAxis(
            title=go.layout.xaxis.Title(
                text='Time',
                font=dict(
                    family='Courier New, monospace',
                    size=18,
                    color='#7f7f7f'
                )
            )
        ),
        yaxis=go.layout.YAxis(
            title=go.layout.yaxis.Title(
                text='Sentiment Count',
                font=dict(
                    family='Courier New, monospace',
                    size=18,
                    color='#7f7f7f'
                )
            ),
            range=[0, 50]
        )
    )
    fig = go.Figure(data=data, layout=layout)
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)