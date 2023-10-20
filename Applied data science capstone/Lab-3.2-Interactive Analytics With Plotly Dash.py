# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

print(max_payload, min_payload)
# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36',
                   'font-size': 40}),
    # TASK 1: Add a dropdown list to enable Launch Site selection
    # The default select value is for ALL sites
    # dcc.Dropdown(id='site-dropdown',...)
    dcc.Dropdown(id='site-dropdown',
                 options=[
                             {'label': 'All Sites', 'value': 'ALL'},
                         ] + [{'label': x, 'value': x} for x in spacex_df['Launch Site'].unique()],
                 value='ALL',
                 placeholder="Launch Sites",
                 searchable=True,
                 # style={'width': '80%', 'padding': '3px', 'font-size': '20px', 'text-align-last': 'center'}
                 ),
    html.Br(),

    # TASK 2: Add a pie chart to show the total successful launches count for all sites
    # If a specific launch site was selected, show the Success vs. Failed counts for the site
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):"),
    # TASK 3: Add a slider to select payload range
    # dcc.RangeSlider(id='payload-slider',...)
    dcc.RangeSlider(id='payload-slider',
                    min=0, max=10000, step=1000,
                    marks={0: '0',
                           10000: '10000'},
                    value=[min_payload, max_payload]),

    # TASK 4: Add a scatter chart to show the correlation between payload and launch success
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])


# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output

@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    filtered_df = spacex_df
    # print(entered_site)
    if entered_site == 'ALL':
        fig = px.pie(filtered_df, values='class',
                     names='Launch Site',
                     title='Each Launch Site Chart')
        return fig
    else:
        # return the outcomes piechart for a selected site
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site].value_counts().reset_index().rename(
            columns={'count': 'class_count'})
        # print(filtered_df['class'].value_counts())
        fig = px.pie(filtered_df, values='class_count',
                     names='class',
                     title=entered_site + ' Pie Chart')
        return fig


# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
              [Input(component_id='site-dropdown', component_property='value'), Input(component_id="payload-slider",
                                                                                      component_property="value")])
def get_scatter_plot(entered_site, slider_val):
    # print('input params', entered_site, slider_val)
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)']>=slider_val[0])&(spacex_df['Payload Mass (kg)']<=slider_val[1]) ]

    # filtered_df = spacex_df
    # print(entered_site)
    if entered_site == 'ALL':
        filtered_df = add_success_rate(filtered_df)
        print(filtered_df)
        fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class', color="Booster Version Category",
                         title='Correlation Between PayLoad and Success for all Sites')
        return fig
    else:
        # return the outcomes piechart for a selected site
        filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]
        # print(filtered_df['class'].value_counts())
        filtered_df = add_success_rate(filtered_df)
        print(filtered_df)
        fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class', color="Booster Version Category",
                         title='Correlation Between PayLoad and Success for ' + entered_site)
        return fig


def add_success_rate(fdata):
    group_df = pd.DataFrame(fdata.groupby('Booster Version Category')['class'].mean()).reset_index()
    launch_sites = {}
    for row in group_df.iterrows():
        launch_sites[row[1]['Booster Version Category']] = f"{row[1]['Booster Version Category']}-({round(row[1]['class']*100,1)}%)"
    fdata['Booster Version Category'] = fdata['Booster Version Category'].map(launch_sites)
    return fdata

# Run the app
if __name__ == '__main__':
    app.run_server()
