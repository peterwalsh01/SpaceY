print("Starting updated SpaceX Dash App...")
# Import required libraries 
import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

# Read the SpaceX launch data into a pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout with:
# - A header
# - A dropdown to select the launch site (Task 1)
# - A pie chart to show success counts (Task 2)
# - A payload range slider (Task 3)
# - A scatter chart to show the correlation between payload and launch success (Task 4)
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    
    # TASK 1: Launch Site Dropdown Component
    dcc.Dropdown(
        id='site-dropdown',
        options=[
            {'label': 'All Sites', 'value': 'ALL'},
            {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
            {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
            {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
            {'label': 'Vandenberg SLC-4E', 'value': 'Vandenberg SLC-4E'},
        ],
        value='ALL',  # Default selection
        placeholder="Select a Launch Site here",
        searchable=True
    ),
    html.Br(),

    # TASK 2: Pie Chart for Launch Successes
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):"),
    
    # TASK 3: Payload Range Slider
    dcc.RangeSlider(
        id='payload-slider',
        min=min_payload,
        max=max_payload,
        step=1000,
        value=[min_payload, max_payload],
        marks={int(i): str(int(i)) for i in range(int(min_payload), int(max_payload) + 1, 2000)}
    ),
    html.Br(),

    # TASK 4: Scatter Chart for Payload vs. Launch Success
    html.Div(dcc.Graph(id='success-payload-scatter-chart'))
])

# TASK 2: Callback to update the pie chart based on the selected launch site
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def update_pie_chart(selected_site):
    if selected_site == 'ALL':
        # For all sites, show the total successful launches count by launch site.
        fig = px.pie(
            spacex_df, 
            names='Launch Site', 
            values='class', 
            title='Total Success Launches by Site'
        )
    else:
        # For a specific site, filter the dataframe and display the success vs. failure counts.
        filtered_df = spacex_df[spacex_df['Launch Site'] == selected_site]
        # Count the number of success (class=1) and failure (class=0) for that site
        success_failure_counts = filtered_df['class'].value_counts().reset_index()
        success_failure_counts.columns = ['class', 'count']
        # Replace numeric class values with descriptive labels
        success_failure_counts['class'] = success_failure_counts['class'].replace({1: 'Success', 0: 'Failure'})
        fig = px.pie(
            success_failure_counts,
            names='class',
            values='count',
            title=f'Total Success vs. Failure Launches for site {selected_site}'
        )
    return fig

# TASK 4: Callback to update the scatter chart based on selected launch site and payload range
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def update_scatter_chart(selected_site, payload_range):
    low, high = payload_range
    # Filter data based on payload range
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= low) & (spacex_df['Payload Mass (kg)'] <= high)]
    if selected_site != 'ALL':
        filtered_df = filtered_df[filtered_df['Launch Site'] == selected_site]
    
    # Create scatter plot: x axis is payload mass, y axis is launch outcome (class)
    fig = px.scatter(
        filtered_df, 
        x='Payload Mass (kg)', 
        y='class', 
        color='Launch Site',
        title='Correlation between Payload and Success for ' + (selected_site if selected_site != 'ALL' else 'all sites'),
        labels={'class': 'Launch Outcome'}
    )
    return fig

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
