import dash
from dash import Dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import requests
import json

import os
api_key = os.environ.get('API_KEY')


# Function to get live electricity consumption data
def get_electricity_data():
    url = "https://api.octopus.energy/v1/electricity-meter-points/1012404143579/meters/19L2399739/consumption/"
    
    response = requests.get(url, auth=(api_key, ''))
    return response.json()


# Function to get live gas consumption data
def get_gas_data():
    url = "https://api.octopus.energy/v1/gas-meter-points/3337591105/meters/E6S12894641961/consumption/"
   
    response = requests.get(url, auth=(api_key, ''))
    return response.json()


# Initialize the Dash app
app = Dash(__name__)
server = app.server
# Layout of the dashboard
app.layout = html.Div(children=[
    html.H1(children='Real-Time Energy Consumption Dashboard'),

    # Electricity Graph
    html.Div([
        html.H2(children='Electricity Consumption'),
        dcc.Graph(id='electricity-graph'),
    ]),

    # Gas Graph
    html.Div([
        html.H2(children='Gas Consumption'),
        dcc.Graph(id='gas-graph'),
    ]),

    # Interval component for updating the graphs every 10 seconds
    dcc.Interval(
        id='interval-component',
        interval=10 * 1000,  # Update every 10 seconds
        n_intervals=0
    )
])


# Callback to update both electricity and gas graphs
@app.callback(
    [Output('electricity-graph', 'figure'),
     Output('gas-graph', 'figure')],
    [Input('interval-component', 'n_intervals')]
)
def update_graphs(n):
    # Fetch electricity data
    electricity_data = get_electricity_data()
    electricity_timestamps = [entry['interval_start'] for entry in electricity_data['results']]
    electricity_consumption = [entry['consumption'] for entry in electricity_data['results']]

    # Fetch gas data
    gas_data = get_gas_data()
    gas_timestamps = [entry['interval_start'] for entry in gas_data['results']]
    gas_consumption = [entry['consumption'] for entry in gas_data['results']]

    # Electricity consumption graph
    electricity_figure = go.Figure(
        data=[go.Scatter(x=electricity_timestamps, y=electricity_consumption, mode='lines+markers')],
        layout=go.Layout(
            title='Live Electricity Consumption',
            xaxis_title='Timestamp',
            yaxis_title='Consumption (kWh)',
        )
    )

    # Gas consumption graph
    gas_figure = go.Figure(
        data=[go.Scatter(x=gas_timestamps, y=gas_consumption, mode='lines+markers')],
        layout=go.Layout(
            title='Live Gas Consumption',
            xaxis_title='Timestamp',
            yaxis_title='Consumption (kWh)',
        )
    )

    return electricity_figure, gas_figure


# Run the server
if __name__ == '__main__':
    app.run_server(debug=False)
