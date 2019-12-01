import datetime

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly
from dash.dependencies import Input, Output
import plotly.graph_objs as go

from pymongo import MongoClient
mongo_db_table = MongoClient('localhost', 27017)['pdb']['sentiment']

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = html.Div(
    html.Div([
        html.Div(id='live-update-text'),
        dcc.Graph(id='live-update-graph'),
        dcc.Interval(
            id='interval-component',
            
            # Graph updated every 10 seconds
            interval=10*1000, # in milliseconds
            n_intervals=0
        )
    ])
)


@app.callback(Output('live-update-text', 'children'),
              [Input('interval-component', 'n_intervals')])
def update_metrics(n):
    positive = 0
    negative = 0
    neutral = 0

    twitter_data = mongo_db_table.find()
    for tweet in twitter_data:
        if tweet['sentiment'] > 0.0:
            positive += 1
        elif tweet['sentiment'] < 0.0:
            negative += 1
        else:
            neutral += 1

    style = {'padding': '5px', 'fontSize': '16px'}

    return [
        html.Span('Positive: {}, Negative: {}, NTRL: {}'.format(positive, negative, neutral), style=style)
    ]


# Multiple components can update everytime interval gets fired.
@app.callback(Output('live-update-graph', 'figure'),
              [Input('interval-component', 'n_intervals')])
def update_graph_live(n):
    data = {
        'time': [],
        'Altitude': [],
        'Sentiment': [],
    }

    twitter_data = list(mongo_db_table.find())
    twitter_data_reversed = twitter_data[::-1]

    # arr_of_pos_sentiment = []
    # arr_of_neg_sentiment = []

    for i in range(len(twitter_data_reversed)):
        time = datetime.datetime.now() - datetime.timedelta(seconds=i*20)

        data['time'].append(time)

        # Sentiment attr in mongodb should be Double
        if twitter_data_reversed[i]['sentiment'] > 0.0:        
            data['Sentiment'].append(twitter_data_reversed[i]['sentiment'])
        elif twitter_data_reversed[i]['sentiment'] < 0.0:
            data['Altitude'].append(twitter_data_reversed[i]['sentiment'])
    
    trace1 = go.Scatter (
        x=data['time'],
        y=data['Sentiment'],
        name='Positive Sentiment'
    )

    trace2 = go.Scatter (
        x=data['time'],
        y=data['Altitude'],
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
                text='Sentiment',
                font=dict(
                    family='Courier New, monospace',
                    size=18,
                    color='#7f7f7f'
                )
            )
        )
    )
    fig = go.Figure(data=data, layout=layout)
    return fig

if __name__ == '__main__':
    app.run_server(debug=False)