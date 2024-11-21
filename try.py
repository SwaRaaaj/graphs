import dash
from dash import html, dcc, Input, Output, dash_table
import plotly.express as px
import plotly.graph_objs as go
import pandas as pd

# Load the data from the "Final" sheetdf = pd.read_excel("./data/TruEstimate Final Sheet Project (5).xlsx", sheet_name='final')
df = pd.read_excel("./data/TruEstimate Final Sheet Project (5).xlsx", sheet_name='Final')

# Convert 'Launch Date' to datetime type and filter projects after October 2022
df['Launch Date'] = pd.to_datetime(df['Launch Date'], errors='coerce')
df = df[df['Launch Date'] > '2022-10-01']

# Extract year and quarter from the 'Launch Date', and create a readable "Year Q" format
df['Year'] = df['Launch Date'].dt.year
df['Quarter'] = df['Launch Date'].dt.quarter
df['YearQuarter'] = df['Year'].astype(str) + ' Q' + df['Quarter'].astype(str)

# Handle mixed data types in 'Area' and 'Developer Name' columns by converting all values to strings
# Replace NaN values in 'Area' with a placeholder
df['Area'] = df['Area'].fillna('Unknown').astype(str)
df['Developer Name'] = df['Developer Name'].astype(str)

# Generate unique YearQuarter values for RangeSlider
year_quarters = df['YearQuarter'].unique()
year_quarters = sorted(year_quarters, key=lambda x: (int(x.split()[0]), int(x.split()[1][1])))

# Initialize the app
app = dash.Dash(__name__)

app.layout = html.Div(children=[
    html.H1(children='Real Estate Project Dashboard', style={'textAlign': 'center', 'padding': '20px', 'fontFamily': 'Arial', 'fontWeight': 'bold', 'fontSize': '36px', 'color': '#003366'}),

    html.Div([
        html.Div([
            html.Label('Select Graph View:', style={'fontSize': '16px', 'fontWeight': 'bold', 'color': '#003366', 'marginBottom': '5px'}),
            dcc.Dropdown(
                id='graph-view-dropdown',
                options=[
                    {'label': 'Total Units by Quarter', 'value': 'QUARTERLY'},
                    {'label': 'Developer-wise Quarterly Launches', 'value': 'DEVELOPER'},
                    {'label': 'Units Launched in Area by Quarter', 'value': 'AREA_QUARTERLY'},
                    {'label': 'Asset Type Launched Year-wise', 'value': 'ASSET_YEARLY'}
                ],
                value='QUARTERLY',
                style={'width': '100%', 'padding': '5px', 'fontSize': '14px', 'borderRadius': '5px', 'border': '1px solid #003366'}
            )
        ], style={'width': '23%', 'display': 'inline-block', 'paddingRight': '10px'}),

        html.Div([
            html.Label('Select Area:', style={'fontSize': '16px', 'fontWeight': 'bold', 'color': '#003366', 'marginBottom': '5px'}),
            dcc.Dropdown(
                id='area-filter-dropdown',
                options=[{'label': area, 'value': area} for area in sorted(df['Area'].unique())],
                multi=True,
                placeholder='Filter by Area',
                style={'width': '100%', 'padding': '5px', 'fontSize': '14px', 'borderRadius': '5px', 'border': '1px solid #003366'}
            )
        ], style={'width': '23%', 'display': 'inline-block', 'paddingRight': '10px'}),

        html.Div([
            html.Label('Select Developer:', style={'fontSize': '16px', 'fontWeight': 'bold', 'color': '#003366', 'marginBottom': '5px'}),
            dcc.Dropdown(
                id='developer-filter-dropdown',
                options=[{'label': dev, 'value': dev} for dev in sorted(df['Developer Name'].unique())],
                multi=True,
                placeholder='Filter by Developer',
                style={'width': '100%', 'padding': '5px', 'fontSize': '14px', 'borderRadius': '5px', 'border': '1px solid #003366'}
            )
        ], style={'width': '23%', 'display': 'inline-block', 'paddingRight': '10px'})
    ], style={'textAlign': 'center', 'marginBottom': '10px', 'display': 'flex', 'justifyContent': 'center', 'gap': '10px'}),

    html.Div([
        html.Div([
            html.Label('Select Date Range:', style={'fontSize': '16px', 'fontWeight': 'bold', 'color': '#003366', 'marginBottom': '5px'}),
            dcc.RangeSlider(
                id='date-range-slider',
                min=0,
                max=len(year_quarters) - 1,
                value=[0, len(year_quarters) - 1],
                marks={i: year_quarters[i] for i in range(len(year_quarters))},
                step=1
            )
        ], style={'width': '80%', 'display': 'inline-block'})
    ], style={'textAlign': 'center', 'marginBottom': '30px', 'display': 'flex', 'justifyContent': 'center'}),

    html.Div(id='display-container', style={'width': '90%', 'margin': '0 auto'})  # This div will update to display both the table and graphs based on selection
])

@app.callback(
    Output('display-container', 'children'),
    [Input('graph-view-dropdown', 'value'),
     Input('area-filter-dropdown', 'value'),
     Input('developer-filter-dropdown', 'value'),
     Input('date-range-slider', 'value')]
)
def update_display(view, selected_areas, selected_developers, date_range):
    filtered_df = df.copy()

    # Apply filters if selected
    if selected_areas:
        filtered_df = filtered_df[filtered_df['Area'].isin(selected_areas)]
    if selected_developers:
        filtered_df = filtered_df[filtered_df['Developer Name'].isin(selected_developers)]

    # Apply date range filter
    selected_year_quarters = year_quarters[date_range[0]:date_range[1] + 1]
    filtered_df = filtered_df[filtered_df['YearQuarter'].isin(selected_year_quarters)]

    # Handle different views: QUARTERLY, DEVELOPER, AREA_QUARTERLY, ASSET_YEARLY
    if view == 'QUARTERLY':
        # Calculate total units by quarter
        total_units_df = filtered_df.groupby(['YearQuarter']).agg({'Total no. of units': 'sum'}).reset_index()
        
        # Create the line graph for Total Units by Quarter
        line_fig_quarter = px.line(total_units_df, x='YearQuarter', y='Total no. of units', 
                                   title='Total Units by Quarter (Line Chart)', markers=True)
        line_fig_quarter.update_layout(title={'font': {'size': 24}},
                                       xaxis={'title': {'font': {'size': 18}}},
                                       yaxis={'title': {'font': {'size': 18}}},
                                       height=500)
        
        # Create the bar graph for Total Units by Quarter
        bar_fig_quarter = px.bar(total_units_df, x='YearQuarter', y='Total no. of units', 
                                 title='Total Units by Quarter (Bar Chart)')
        bar_fig_quarter.update_layout(title={'font': {'size': 24}},
                                      xaxis={'title': {'font': {'size': 18}}},
                                      yaxis={'title': {'font': {'size': 18}}},
                                      height=500)

        # Set the data table for the quarterly view
        table_df = total_units_df

        # Generate the table dynamically
        table = dash_table.DataTable(
            data=table_df.to_dict('records'),
            columns=[{"name": i, "id": i} for i in table_df.columns],
            style_table={'height': '400px', 'overflowY': 'auto', 'border': '2px solid #003366', 'borderRadius': '5px'},
            style_cell={
                'textAlign': 'center',
                'padding': '10px',
                'whiteSpace': 'normal',
                'fontSize': '16px',
                'fontFamily': 'Arial'
            },
            style_header={
                'backgroundColor': '#003366',
                'fontWeight': 'bold',
                'color': 'white',
                'textAlign': 'center',
                'fontSize': '18px'
            },
            style_data_conditional=[
                {'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(248, 248, 248)'}
            ],
            fixed_rows={'headers': True, 'data': 0},
            sort_action='none',  # Sorting disabled
            page_action='none',
            editable=False
        )

        return [
            html.Div(table, style={'marginBottom': '20px'}),
            html.Div([dcc.Graph(figure=line_fig_quarter), dcc.Graph(figure=bar_fig_quarter)])
        ]
    elif view == 'DEVELOPER':
        # Calculate total units by developer and quarter
        dev_units_df = filtered_df.groupby(['YearQuarter', 'Developer Name']).agg({'Total no. of units': 'sum'}).reset_index()
        
        # Create the bar graph for Developer-wise Quarterly Launches
        bar_fig_dev = px.bar(dev_units_df, x='YearQuarter', y='Total no. of units', color='Developer Name',
                             title='Developer-wise Quarterly Launches (Stacked Bar)')
        bar_fig_dev.update_layout(title={'font': {'size': 24}},
                                  xaxis={'title': {'font': {'size': 18}}},
                                  yaxis={'title': {'font': {'size': 18}}},
                                  height=500)

        # Set the data table for the developer view
        table_df = dev_units_df

        # Generate the table dynamically
        table = dash_table.DataTable(
            data=table_df.to_dict('records'),
            columns=[{"name": i, "id": i} for i in table_df.columns],
            style_table={'height': '400px', 'overflowY': 'auto', 'border': '2px solid #003366', 'borderRadius': '5px'},
            style_cell={
                'textAlign': 'center',
                'padding': '10px',
                'whiteSpace': 'normal',
                'fontSize': '16px',
                'fontFamily': 'Arial'
            },
            style_header={
                'backgroundColor': '#003366',
                'fontWeight': 'bold',
                'color': 'white',
                'textAlign': 'center',
                'fontSize': '18px'
            },
            style_data_conditional=[
                {'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(248, 248, 248)'}
            ],
            fixed_rows={'headers': True, 'data': 0},
            sort_action='none',  # Sorting disabled
            page_action='none',
            editable=False
        )

        return [
            html.Div(table, style={'marginBottom': '20px'}),
            html.Div([dcc.Graph(figure=bar_fig_dev)])
        ]
    elif view == 'AREA_QUARTERLY':
        # Calculate total units launched in each area by quarter
        area_units_df = filtered_df.groupby(['YearQuarter', 'Area']).agg({'Total no. of units': 'sum'}).reset_index()

        # Create bar graph for Units Launched in Area by Quarter
        bar_fig_area = px.bar(area_units_df, x='YearQuarter', y='Total no. of units', color='Area',
                              title='Units Launched in Area by Quarter (Bar Chart)')
        bar_fig_area.update_layout(title={'font': {'size': 24}},
                                   xaxis={'title': {'font': {'size': 18}}},
                                   yaxis={'title': {'font': {'size': 18}}},
                                   height=500)

        # Set the data table for the area quarterly view
        table_df = area_units_df

        # Generate the table dynamically
        table = dash_table.DataTable(
            data=table_df.to_dict('records'),
            columns=[{"name": i, "id": i} for i in table_df.columns],
            style_table={'height': '400px', 'overflowY': 'auto', 'border': '2px solid #003366', 'borderRadius': '5px'},
            style_cell={
                'textAlign': 'center',
                'padding': '10px',
                'whiteSpace': 'normal',
                'fontSize': '16px',
                'fontFamily': 'Arial'
            },
            style_header={
                'backgroundColor': '#003366',
                'fontWeight': 'bold',
                'color': 'white',
                'textAlign': 'center',
                'fontSize': '18px'
            },
            style_data_conditional=[
                {'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(248, 248, 248)'}
            ],
            fixed_rows={'headers': True, 'data': 0},
            sort_action='none',  # Sorting disabled
            page_action='none',
            editable=False
        )

        return [
            html.Div(table, style={'marginBottom': '20px'}),
            html.Div([dcc.Graph(figure=bar_fig_area)])
        ]
    elif view == 'ASSET_YEARLY':
        # Calculate total units launched by asset type (Apartment, Villa, Plot) year-wise
        asset_units_df = filtered_df.groupby(['Year', 'Asset Type']).agg({'Total no. of units': 'sum'}).reset_index()
        
        # Create stacked bar chart for Asset Type launched Year-wise
        bar_fig_asset = px.bar(asset_units_df, x='Year', y='Total no. of units', color='Asset Type',
                               title='Asset Type Launched Year-wise (Stacked Bar)')
        bar_fig_asset.update_layout(title={'font': {'size': 24}},
                                    xaxis={'title': {'font': {'size': 18}}},
                                    yaxis={'title': {'font': {'size': 18}}},
                                    height=500)

        # Set the data table for the asset yearly view
        table_df = asset_units_df

        # Generate the table dynamically
        table = dash_table.DataTable(
            data=table_df.to_dict('records'),
            columns=[{"name": i, "id": i} for i in table_df.columns],
            style_table={'height': '400px', 'overflowY': 'auto', 'border': '2px solid #003366', 'borderRadius': '5px'},
            style_cell={
                'textAlign': 'center',
                'padding': '10px',
                'whiteSpace': 'normal',
                'fontSize': '16px',
                'fontFamily': 'Arial'
            },
            style_header={
                'backgroundColor': '#003366',
                'fontWeight': 'bold',
                'color': 'white',
                'textAlign': 'center',
                'fontSize': '18px'
            },
            style_data_conditional=[
                {'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(248, 248, 248)'}
            ],
            fixed_rows={'headers': True, 'data': 0},
            sort_action='none',  # Sorting disabled
            page_action='none',
            editable=False
        )

        return [
            html.Div(table, style={'marginBottom': '20px'}),
            html.Div([dcc.Graph(figure=bar_fig_asset)])
        ]
    else:
        return html.Div('Select a valid graph type')

# Run the app
if __name__ == "__main__":
    app.run_server(host='0.0.0.0', port=10000, debug=True)
