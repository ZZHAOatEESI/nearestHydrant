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
## new ##
from googlemaps_api import *
from NearestElement import *
app = dash.Dash()
## new ##


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

@app.callback(Output("map-graph", "figure"),
              [Input('my-slider', 'value')],
              [State('map-graph', 'relayoutData')])
def update_graph(slider_value, prevLayout):
    ## new ##
    zoom = 12.0
#    latInitial = 39.9
#    lonInitial = -75.1
    latInitial = 39.8682140
    lonInitial = -75.0434433
    bearing = 0
    mapControls = 'lock'
#    [latInitial, lonInitial] = get_Geocode('200 N White Horse Pike, Lawnside, NJ 08045, USA')
    output_pd = hydrants.get_nearest_fast_allinOne(lonInitial, latInitial, epsilon = 1, top = 3, metric = 'km', d_method = 'walking')
    output_pd.drop("OutOfService", 1, inplace=True)
    output_pd.drop("Critical", 1, inplace=True)
    output_pd.drop("CriticalNotes", 1, inplace=True)
    address = get_address([output_pd.iloc[0]['Lat'], output_pd.iloc[0]['Lon']])
    print(address)
    listStr = 'output_pd'
    ## new ##
#    latInitial = 39.8680
#    lonInitial = -75.0427
#    listStr = 'totalList'
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
    ## new ##
    global hydrants
    hydrants = data_generator('/Users/Joe/Desktop/phillyCODEFEST/hydrants.json')
    ## new ##

if __name__ == '__main__':
    app.run_server(debug=True)
