import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.express as px
import utils.api as api

data = api.Data(r'data/deertrail_lab.csv')

app = dash.Dash(__name__, title='GPMR')
server = app.server


app.layout = html.Div([
    html.Nav([
        html.Div([
            html.Img(src=app.get_asset_url('logo.png'),
                     style={'height': '2rem'}),
            dcc.Link(
                html.H1('GPMR'), href='/', className='title')
        ], className='flex'),
        html.Div([
            html.Img(src=app.get_asset_url(
                'github-brands.svg'), className='icon'),
            html.A('Source', href='https://github.com/ItaiAxelrad/gpmr')
        ], className='flex')
    ]),
    html.Aside(children=[
        html.H2('Input'),
        html.Label('Monitoring Well'),
        dcc.Dropdown(id='location',
                     options=[
                         # api.get_locations(df)
                         {'label': loc, 'value': loc} for loc in data.locations
                     ],
                     multi=False,
                     placeholder='Select a well'
                     ),
        html.Label('Analyte'),
        dcc.Dropdown(id='parameter',
                     options=[
                         # api.get_parameters(df)
                         {'label': param, 'value': param} for param in data.parameters
                     ],
                     multi=False,
                     placeholder='Select a parameter'
                     ),
        html.Label('Y-Axis Type'),
        dcc.RadioItems(
            id='yaxis-type',
            options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
            value='Linear',
            labelStyle={'display': 'inline-block'}
        ),
        html.Div([html.H2('Output'),
                  dcc.Loading(type='circle', color='#4c72b0', children=[
                      html.Div(id='output_container',
                               className='output container', children=[])
                  ], className='wrapper')])], id='user_input', className='container'),
    html.Main(children=[html.H2('Display'),
                        dcc.Graph(id='linechart', responsive=True, figure=px.line(
                            None, template='seaborn'))], id='display', className='container')
], id='root')


# Connect the Plotly graphs with Dash Components
@ app.callback(
    Output('output_container', 'children'),
    Output('linechart', 'figure'),
    Input('location', 'value'),
    Input('parameter', 'value'),
    Input('yaxis-type', 'value'),
)
def update_graph(location, parameter, yaxis_type):
    if location and parameter:
        try:
            df = data.fill_na().get_data(location, parameter)
            if df.empty:
                print('DataFrame is empty!')
                return 'No data to display', px.line(None, template='seaborn')
            desc_list = api.get_description(df)
            summary = html.Ul(
                id='sum-list', children=[html.Li(f"{i[0]}: {i[1]}") for i in desc_list])

            # Plotly Express
            fig = px.line(
                df,
                x='datetime',
                y='value',
                title='Time vs Concentration',
                labels={
                    "datetime": "Date",
                    "value": f"Concentration ({df.unit[0]})"
                },
                template='seaborn',
                markers=True,
            )
            fig.update_yaxes(type='linear' if yaxis_type ==
                             'Linear' else 'log')
            fig.update_layout(transition_duration=250)
            return summary, fig

        except KeyError:
            return 'No data for selection', px.line(None, template='seaborn')

    else:
        return '', px.line(None, template='seaborn')


if __name__ == '__main__':
    app.run_server(debug=True)
