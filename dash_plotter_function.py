"""The module is responsible for graphical plotting with Dash."""

import threading
import datetime as dt
import re

import pandas as pd
import dash
from dash.dependencies import Output, Input
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

app = dash.Dash(__name__)


def initialize_layout(file_name, channels):
    data = pd.read_csv(file_name, header=None)
    data[3] /= 10

    colors = []


    
    curr_value = 0
    prev_value = 0
    for i in range(len(data[3])):
        curr_value = data[3][i]

        if (curr_value - 1 >= prev_value):
            colors.append(1)
        else:
            colors.append(0)
        prev_value = data[3][i]

    data_table = go.Table(
                    header=dict(values=channels),
                    cells=dict(values=[data[0], data[1], data[2], data[3], data[4]],
                                fill=dict(color=['rgb(245,245,245)',
                                                'rgb(245,245,245)',
                                                'rgb(245,245,245)',
                                                ['rgb(245,245,245)' if val == 0 else 'rgba(250,0,0, 0.8)' for val in colors],
                                                'rgb(245,245,245)']),           
                                                    )
                    )

    app.layout = html.Div([
        html.Div([
            html.H2('Drive Data',
                    style={'float': 'left',
                           }),
            ]),
        html.Div(children=dcc.Graph(
            id='drive data graph',
            figure={'data': [data_table],
                    'layout': go.Layout(showlegend=True,
                                        title='Drive Data',
                                        height=1000,
                                        width=1800,
                                        autosize=False)}
                )),
        ], className="container",style={'width':'98%','margin-left':10,'margin-right':10,'max-width':50000})

