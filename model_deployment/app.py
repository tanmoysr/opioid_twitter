
'''

'''
import base64
import json
from collections import OrderedDict
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html



external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
mapbox_access_token = 'pk.eyJ1IjoidGFubW95c3IiLCJhIjoiY2s5aDc2cjZoMHMzMTNscGhtcTA0MHZkOSJ9.ElGEgw3N2aEk1hFLjB7vng'

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

colors = {
    "graphBackground": "#F5F5F5",
    "background": "#ffffff",
    "text": "#000000"
}

app.layout = html.Div([
html.H3('Opioid Detection'),
html.H5('Jooyeon Jamie Lee (G01129351)'),
html.H5('Tanmoy Chowdhury (G01025893)'),
html.Div(children='''The misuse of opioid prescription pain relievers and opioid overdose deaths is a significant issue. Many people misusing prescription opioids get addicted to these drugs, and the consequences are sometimes fatal. We will build our model to answer the challenge presented in 2020 International Conference on Social Computing, Behavioral-Cultural Modeling, & Prediction and Behavior Representation in Modeling and Simulation (SBP-BRiMS 2020). We are going to use tweeter data and build a subgraph of people using overdose of opioids and validate our finding by comparing with the data set provided by Cincinnati EMS calls data'''),
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        # Allow multiple files to be uploaded
        multiple=False
    ),
    dcc.Graph(id='Mygraph'),

    html.Button('Run the Model', id='btn-nclicks-1', n_clicks=0,
                style={
                    'width': '100%',
                    'height': '60px',
                    'lineHeight': '60px',
                    'borderWidth': '1px',
                    'borderStyle': 'dashed',
                    'borderRadius': '5px',
                    'textAlign': 'center',
                    'margin': '10px'
                }
                ),
    html.Div(id='container')
])

def parse_data(contents, filename):
    data = {}
    data['lat'] = []
    data['long'] = []
    data['city'] = []
    data['state'] = []
    data['country'] = []
    if contents is not None:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string).decode("utf-8")
        objs = decoded.replace('}\n{', '}\t{')
        lines = objs.split('\t')
        for line in lines:
            line = line.strip()
            jo = json.loads(line, object_pairs_hook=OrderedDict)
            try:
                data['long'].append(jo['place']['bounding_box']['coordinates'][0][0][0])
                data['lat'].append(jo['place']['bounding_box']['coordinates'][0][0][1])
                data['city'].append(jo['place']['full_name'].split(',')[0])
                data['country'].append(jo['place']['country_code'])
            except TypeError:
                data['long'].append(None)
                data['lat'].append(None)
                data['city'].append(None)
                data['state'].append(None)
                data['country'].append(None)
    return data

@app.callback(Output('Mygraph', 'figure'),
            [
                Input('upload-data', 'contents'),
                Input('upload-data', 'filename')
            ])
def update_graph(contents, filename):

    data = parse_data(contents, filename)

    figure=dict(
        data=[dict(
            lat=data['lat'],
            lon=data['long'],
            type='scattermapbox',
            marker=[dict(size=5, color='green', opacity=0)]
        )],
        layout=dict(
            mapbox=dict(
                layers=[],
                accesstoken=mapbox_access_token,
                style='light',
                center=dict(
                    lat= 39.585376,
                    lon=-102.447762,
                ),
                pitch=0,
                zoom=2.5
            )
        )
    )
    return figure

@app.callback(Output('container', 'children'), [Input('btn-nclicks-1', 'n_clicks')])
def display_graphs(n_clicks):
    input_path = 'model_output.txt'
    data = {}
    data['lat'] = []
    data['long'] = []
    data['city'] = []
    data['state'] = []
    data['country'] = []
    with open(input_path, 'r') as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip()
            jo = json.loads(line, object_pairs_hook=OrderedDict)
            try:
                data['long'].append(jo['place']['bounding_box']['coordinates'][0][0][0])
                data['lat'].append(jo['place']['bounding_box']['coordinates'][0][0][1])
                data['city'].append(jo['place']['full_name'].split(',')[0])
                # data['state'].append(jo['place']['full_name'].split(',')[1])
                data['country'].append(jo['place']['country_code'])
            except TypeError:
                data['long'].append(None)
                data['lat'].append(None)
                data['city'].append(None)
                data['state'].append(None)
                data['country'].append(None)
    graphs = []
    for i in range(n_clicks):
        graphs.append(dcc.Graph(
            id='graph-{}'.format(i),
                    figure=dict(
            data=[dict(
                lat=data['lat'],
                lon=data['long'],
                type='scattermapbox',
                marker=[dict(size=5, color='green', opacity=0)]
            )],
            layout=dict(
                mapbox=dict(
                    layers=[],
                    accesstoken=mapbox_access_token,
                    style='light',
                    center=dict(
                        lat= 39.585376,
                        lon=-102.447762,
                    ),
                    pitch=0,
                    zoom=2.5
                )))))

    return html.Div(graphs)

if __name__ == '__main__':
    app.run_server(debug=True)