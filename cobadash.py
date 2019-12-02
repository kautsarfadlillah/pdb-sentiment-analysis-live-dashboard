import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import dash.dependencies
from dash.dependencies import Input, Output, State
import plotly

from pymongo import MongoClient
import plotly.graph_objects as go
import pandas as pd

client = MongoClient('localhost', 27017)
database = client['pdb']
sentiment_table = database['sentiment']
positive_table = database['positive']
negative_table = database['negative']

# for obj in table.find():
#     print(obj)
app = dash.Dash(__name__)

df = pd.DataFrame(sentiment_table.find())
df_pos = pd.DataFrame(positive_table.find())
df_neg = pd.DataFrame(negative_table.find())
# df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/solar.csv')

df = df.drop(['_id'], axis=1)
df_pos = df_pos.drop(['_id'], axis=1)
df_neg = df_neg.drop(['_id'], axis=1)
# print(df.to_dict("rows")[0])

app.layout = html.Div([
	html.Div(
		className='row', 
		children=[ 
			# html.Div(id='recent-tweets-update', className='col s12 m6 l6', style={"word-wrap": "break-word"}),
			html.Div(
				id="recent-tweets-table", className='col s12 m6 l6')]
				),
			dcc.Interval(
				id='recent-tweets-update',
				interval=2*1000
			),
])
@app.callback(Output('recent-tweets-table', 'children'),
[Input('recent-tweets-update', 'n_intervals')])
def recent_tweets(a):
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
						} for i in ['date', 'sentiment']
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

# @app.callback(Output('df'))

if __name__ == '__main__':
	app.run_server(debug=True)