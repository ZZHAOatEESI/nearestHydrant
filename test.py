import dash
from dash.dependencies import Input, Output, State, Event
import dash_core_components as dcc
import dash_html_components as html
import plotly.plotly as py
from plotly import graph_objs as go
from plotly.graph_objs import *
from flask import Flask
from flask_cors import CORS
import pandas as pd
import numpy as np
import os

app = dash.Dash('UberApp')
server = app.server


mapbox_access_token = 'pk.eyJ1IjoiYWxpc2hvYmVpcmkiLCJhIjoiY2ozYnM3YTUxMDAxeDMzcGNjbmZyMmplZiJ9.ZjmQ0C2MNs1AzEBC_Syadg'


def initialize():
    df = pd.read_csv('hydrant_loc.csv')
    df.drop("Unnamed: 0", 1, inplace=True)
    df.drop("OutOfService", 1, inplace=True)
    df.drop("Critical", 1, inplace=True)
    df.drop("CriticalNotes", 1, inplace=True)
    return df


app.layout = html.Div([
    html.Div([
        html.Div([
            
            html.Div([
                
               
                dcc.Graph(id='map-graph'),
                
                
            ], className="graph twelve coluns"),
        ], style={'margin': 'auto auto'}),
        
        dcc.Slider(
            id="my-slider",
            min=1,
            step=1,
            value=1
        ),
    ], className="graphSlider ten columns offset-by-one"),
], style={"padding-top": "20px"})

def getIndex(value):
    if(value==None):
        return 0
    val = {
        'Apr': 0,
        'May': 1,
        'June': 2,
        'July': 3,
        'Aug': 4,
        'Sept': 5
    }[value]
    return val

def getClickIndex(value):
    if(value==None):
        return 0
    return value['points'][0]['x']

def get_selection(value, slider_value, selection):
    xVal = []
    yVal = []
    xSelected = []

    colorVal = ["#F4EC15", "#DAF017", "#BBEC19", "#9DE81B", "#80E41D", "#66E01F",
                "#4CDC20", "#34D822", "#24D249", "#25D042", "#26CC58", "#28C86D",
                "#29C481", "#2AC093", "#2BBCA4", "#2BB5B8", "#2C99B4", "#2D7EB0",
                "#2D65AC", "#2E4EA4", "#2E38A4", "#3B2FA0", "#4E2F9C", "#603099"]

    if(selection is not None):
        for x in selection:
            xSelected.append(int(x))
    for i in range(0, 24, 1):
        if i in xSelected and len(xSelected) < 24:
            colorVal[i] = ('#FFFFFF')
        xVal.append(i)
        yVal.append(len(totalList[getIndex(value)][slider_value-1]
                    [totalList[getIndex(value)][slider_value-1].index.hour == i]))

    return [np.array(xVal), np.array(yVal), np.array(xSelected),
            np.array(colorVal)]


@app.callback(Output("map-graph", "figure"),
              [Input('my-slider', 'value')],
              [State('map-graph', 'relayoutData')])
def update_graph(slider_value, prevLayout):
    zoom = 12.0
    latInitial = 39.9
    lonInitial = -75.1
    bearing = 0
    mapControls = 'lock'
    listStr = 'totalList'

    if(prevLayout is not None and mapControls is not None and
       'lock' in mapControls):
        zoom = float(prevLayout['mapbox']['zoom'])
        latInitial = float(prevLayout['mapbox']['center']['lat'])
        lonInitial = float(prevLayout['mapbox']['center']['lon'])
        bearing = float(prevLayout['mapbox']['bearing'])
    return go.Figure(
        data=Data([
            Scattermapbox(
                lat=eval(listStr)['Lat'],
                lon=eval(listStr)['Lon'],
                mode='markers',
                hoverinfo="lat+lon",
#                 text=eval(listStr).index.hour,
                marker=Marker(
                    size=14
                ),
            ),
        ]),
        layout=Layout(
            autosize=True,
            height=750,
            margin=Margin(l=0, r=0, t=0, b=0),
            showlegend=False,
            mapbox=dict(
                accesstoken=mapbox_access_token,
                center=dict(
                    lat=latInitial, # 40.7272
                    lon=lonInitial # -73.991251
                ),
                style='dark',
                bearing=bearing,
                zoom=zoom
            ),
            updatemenus=[
                dict(
                    buttons=([
                        dict(
                            args=[{
                                    'mapbox.zoom': 12,
                                    'mapbox.center.lon': '-75.1',
                                    'mapbox.center.lat': '39.9',
                                    'mapbox.bearing': 0,
                                    'mapbox.style': 'dark'
                                }],
                            label='Reset Zoom',
                            method='relayout'
                        )
                    ]),
                    direction='left',
                    pad={'r': 0, 't': 0, 'b': 0, 'l': 0},
                    showactive=False,
                    type='buttons',
                    x=0.45,
                    xanchor='left',
                    yanchor='bottom',
                    bgcolor='#323130',
                    borderwidth=1,
                    bordercolor="#6d6d6d",
                    font=dict(
                        color="#FFFFFF"
                    ),
                    y=0.02
                ),
            ]
        )
    )

external_css = ["https://cdnjs.cloudflare.com/ajax/libs/skeleton/2.0.4/skeleton.min.css",
                "//fonts.googleapis.com/css?family=Raleway:400,300,600",
                "//fonts.googleapis.com/css?family=Dosis:Medium",
                "https://cdn.rawgit.com/plotly/dash-app-stylesheets/62f0eb4f1fadbefea64b2404493079bf848974e8/dash-uber-ride-demo.css",
                "https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css"]


for css in external_css:
    app.css.append_css({"external_url": css})


@app.server.before_first_request
def defineTotalList():
    global totalList
    totalList = initialize()


if __name__ == '__main__':
    app.run_server(debug=True)
