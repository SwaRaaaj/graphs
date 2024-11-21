import dash
from dash import html, dcc, Input, Output, dash_table, State
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots

# Load the data from the "Final" sheet
df = pd.read_excel(r"C:\Users\layek\Downloads\TruEstimate Final Sheet Project (5).xlsx", sheet_name='Final')

# Data Preprocessing
df['Launch Date'] = pd.to_datetime(df['Launch Date'], errors='coerce')
df = df[df['Launch Date'] > '2022-10-01']

df['Year'] = df['Launch Date'].dt.year
df['Quarter'] = df['Launch Date'].dt.quarter
df['YearQuarter'] = df['Year'].astype(str) + ' Q' + df['Quarter'].astype(str)

df['Area'] = df['Area'].astype(str).str.strip().str.title()
df['Developer Name'] = df['Developer Name'].astype(str).str.strip()
df = df[df['Area'].notna() & (df['Area'] != 'Unknown') & (df['Area'].str.lower() != 'nan') & (df['Area'] != '')]

# Standardize 'Area' names
df['Area'] = df['Area'].str.title()

# Standardize 'Asset Type' to include all variations
df['Asset Type'] = df['Asset Type'].astype(str).str.strip().str.title()
df['Asset Type'] = df['Asset Type'].replace({
    'Plot': 'Plot',
    'Land': 'Plot',
    'Plot/Land': 'Plot',
    'Plot Land': 'Plot',
    'Villa': 'Villa',
    'Apartment': 'Apartment',
    'Flat': 'Apartment'
})
df = df[df['Asset Type'].isin(['Apartment', 'Villa', 'Plot'])]

# Generate unique YearQuarter values for RangeSlider
year_quarters = df['YearQuarter'].unique()
year_quarters = sorted(year_quarters, key=lambda x: (int(x.split()[0]), int(x.split()[1][1])))

# Initialize the app with Bootstrap theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])

# Define layout
app.layout = dbc.Container([
    html.H1('Real Estate Project Dashboard', className='text-center text-primary mb-4'),

    dbc.Row([
        dbc.Col([
            html.Label('Select Graph View:', className='text-dark font-weight-bold'),
            dcc.Dropdown(
                id='graph-view-dropdown',
                options=[
                    {'label': 'Total Units by Quarter', 'value': 'QUARTERLY'},
                    {'label': 'Developer-wise Quarterly Launches', 'value': 'DEVELOPER'},
                    {'label': 'Units Launched in Area by Quarter', 'value': 'AREA_QUARTERLY'},
                    {'label': 'Asset Type Launched Year-wise', 'value': 'ASSET_YEARLY'}
                ],
                value='QUARTERLY',
                style={'width': '100%'}
            )
        ], md=3),

        dbc.Col([
            html.Label('Select Area:', className='text-dark font-weight-bold'),
            dcc.Dropdown(
                id='area-filter-dropdown',
                options=[{'label': area, 'value': area} for area in sorted(df['Area'].unique())],
                multi=True,
                placeholder='Filter by Area',
                style={'width': '100%'}
            )
        ], md=3),

        dbc.Col([
            html.Label('Select Developer:', className='text-dark font-weight-bold'),
            dcc.Dropdown(
                id='developer-filter-dropdown',
                options=[{'label': dev, 'value': dev} for dev in sorted(df['Developer Name'].unique())],
                multi=True,
                placeholder='Filter by Developer',
                style={'width': '100%'}
            )
        ], md=3),

        dbc.Col([
            html.Label('Select Asset Type:', className='text-dark font-weight-bold'),
            dcc.Dropdown(
                id='asset-type-dropdown',
                options=[{'label': asset, 'value': asset} for asset in ['Apartment', 'Villa', 'Plot']],
                multi=True,
                placeholder='Filter by Asset Type',
                style={'width': '100%'}
            )
        ], md=3),
    ], className='mb-4'),

    dbc.Row([
        dbc.Col([
            html.Label('Select Date Range:', className='text-dark font-weight-bold'),
            dcc.RangeSlider(
                id='date-range-slider',
                min=0,
                max=len(year_quarters) - 1,
                value=[0, len(year_quarters) - 1],
                marks={i: year_quarters[i] for i in range(len(year_quarters))},
                step=1
            )
        ], md=12),
    ], className='mb-4'),

    dbc.Row([
        dbc.Col([
            html.Div(id='display-container')
        ], md=12),
    ])
], fluid=True)

# Callback to update display
@app.callback(
    Output('display-container', 'children'),
    [Input('graph-view-dropdown', 'value'),
     Input('area-filter-dropdown', 'value'),
     Input('developer-filter-dropdown', 'value'),
     Input('asset-type-dropdown', 'value'),
     Input('date-range-slider', 'value')]
)
def update_display(view, selected_areas, selected_developers, selected_asset_types, date_range):
    filtered_df = df.copy()

    # Apply filters
    if selected_areas:
        filtered_df = filtered_df[filtered_df['Area'].isin(selected_areas)]
    if selected_developers:
        filtered_df = filtered_df[filtered_df['Developer Name'].isin(selected_developers)]
    if selected_asset_types:
        filtered_df = filtered_df[filtered_df['Asset Type'].isin(selected_asset_types)]

    selected_year_quarters = year_quarters[date_range[0]:date_range[1] + 1]
    filtered_df = filtered_df[filtered_df['YearQuarter'].isin(selected_year_quarters)]

    # Handle different views
    if view == 'QUARTERLY':
        total_units_df = filtered_df.groupby(['Year', 'Quarter']).agg({'Total no. of units': 'sum'}).reset_index()
        if total_units_df.empty:
            return html.Div('No data available for the selected filters.')

        total_units_df['Quarter'] = 'Q' + total_units_df['Quarter'].astype(str)
        total_units_df['YearQuarter'] = total_units_df['Year'].astype(str) + ' ' + total_units_df['Quarter']
        pivot_total_units_df = total_units_df.pivot(index='Year', columns='Quarter', values='Total no. of units').fillna(0).reset_index()

        # Create percentage table separately
        pivot_total_units_df_percentage = pivot_total_units_df.copy()
        total_per_year = pivot_total_units_df_percentage.iloc[:, 1:].sum(axis=1)
        pivot_total_units_df_percentage.iloc[:, 1:] = pivot_total_units_df_percentage.iloc[:, 1:].div(total_per_year, axis=0) * 100
        pivot_total_units_df_percentage = pivot_total_units_df_percentage.round(2)

        # Calculate summary statistics
        total_units = total_units_df['Total no. of units'].sum()
        avg_units_per_quarter = total_units_df['Total no. of units'].mean()
        max_units_row = total_units_df.loc[total_units_df['Total no. of units'].idxmax()]
        max_units_quarter = max_units_row['YearQuarter']
        max_units_value = max_units_row['Total no. of units']
        min_units_row = total_units_df.loc[total_units_df['Total no. of units'].idxmin()]
        min_units_quarter = min_units_row['YearQuarter']
        min_units_value = min_units_row['Total no. of units']

        summary_data = {
            'Metric': ['Total Units', 'Average Units per Quarter', 'Quarter with Max Units', 'Max Units', 'Quarter with Min Units', 'Min Units'],
            'Value': [total_units, round(avg_units_per_quarter, 2), max_units_quarter, max_units_value, min_units_quarter, min_units_value]
        }

        summary_df = pd.DataFrame(summary_data)

        # Generate the summary table
        summary_table = dash_table.DataTable(
            data=summary_df.to_dict('records'),
            columns=[{"name": i, "id": i} for i in summary_df.columns],
            style_table={'overflowX': 'auto', 'border': '1px solid #ccc', 'width': '50%'},
            style_cell={
                'textAlign': 'left',
                'padding': '10px',
                'fontSize': '14px',
                'fontFamily': 'Arial',
            },
            style_header={
                'backgroundColor': '#ffc107',
                'fontWeight': 'bold',
                'color': 'black',
                'textAlign': 'center'
            },
            fixed_rows={'headers': True},
            sort_action='native',
            page_action='none',
            editable=False
        )

        # Generate the main table
        main_table = dash_table.DataTable(
            data=pivot_total_units_df.to_dict('records'),
            columns=[{"name": str(i), "id": str(i)} for i in pivot_total_units_df.columns],
            style_table={'overflowX': 'auto', 'border': '1px solid #ccc', 'width': '100%'},
            style_cell={
                'textAlign': 'center',
                'padding': '10px',
                'fontSize': '14px',
                'fontFamily': 'Arial',
            },
            style_header={
                'backgroundColor': '#17a2b8',
                'fontWeight': 'bold',
                'color': 'white',
                'textAlign': 'center'
            },
            fixed_rows={'headers': True},
            sort_action='native',
            page_action='none',
            editable=False
        )

        # Generate the percentage table
        percentage_table = dash_table.DataTable(
            data=pivot_total_units_df_percentage.to_dict('records'),
            columns=[{"name": str(i), "id": str(i)} for i in pivot_total_units_df_percentage.columns],
            style_table={'overflowX': 'auto', 'border': '1px solid #ccc', 'width': '100%', 'marginTop': '20px'},
            style_cell={
                'textAlign': 'center',
                'padding': '10px',
                'fontSize': '14px',
                'fontFamily': 'Arial',
            },
            style_header={
                'backgroundColor': '#28a745',
                'fontWeight': 'bold',
                'color': 'white',
                'textAlign': 'center'
            },
            fixed_rows={'headers': True},
            sort_action='native',
            page_action='none',
            editable=False
        )

        # Update graphs for readability
        line_fig = px.line(total_units_df, x='YearQuarter', y='Total no. of units',
                           title='Total Units by Quarter (Line Chart)', markers=True)
        line_fig.update_layout(
            xaxis_tickangle=-45,
            xaxis_title='Year-Quarter',
            yaxis_title='Total Units',
            font=dict(size=12),
            height=400,
            margin=dict(l=40, r=40, t=40, b=120)
        )

        bar_fig = px.bar(total_units_df, x='YearQuarter', y='Total no. of units',
                         title='Total Units by Quarter (Bar Chart)')
        bar_fig.update_layout(
            xaxis_tickangle=-45,
            xaxis_title='Year-Quarter',
            yaxis_title='Total Units',
            font=dict(size=12),
            height=400,
            margin=dict(l=40, r=40, t=40, b=120)
        )

        heatmap_fig = px.imshow(pivot_total_units_df.set_index('Year'),
                                labels=dict(x="Quarter", y="Year", color="Total Units"),
                                x=pivot_total_units_df.columns[1:],
                                y=pivot_total_units_df['Year'],
                                title='Total Units by Quarter (Heatmap)')
        heatmap_fig.update_layout(
            font=dict(size=12),
            height=400,
            margin=dict(l=40, r=40, t=40, b=80)
        )

        return [
            dbc.Card(dbc.CardBody([
                html.H4("Data Summary", className='card-title'),
                summary_table,
            ]), className='mb-4'),
            dbc.Card(dbc.CardBody([
                html.H4("Total Units Table", className='card-title'),
                main_table,
                html.H4("Percentage Table", className='card-title mt-4'),
                percentage_table
            ]), className='mb-4'),
            dbc.Row([
                dbc.Col(dcc.Graph(figure=line_fig), md=6),
                dbc.Col(dcc.Graph(figure=bar_fig), md=6)
            ]),
            dbc.Row([
                dbc.Col(dcc.Graph(figure=heatmap_fig), md=12)
            ])
        ]

    elif view == 'DEVELOPER':
        dev_units_df = filtered_df.groupby(['Developer Name']).agg({'Total no. of units': 'sum'}).reset_index()
        if dev_units_df.empty:
            return html.Div('No data available for the selected filters.')

        total_units_dev = dev_units_df['Total no. of units'].sum()
        dev_units_df['Percentage'] = (dev_units_df['Total no. of units'] / total_units_dev * 100).round(2)
        # Sort developers by total units
        dev_units_df = dev_units_df.sort_values(by='Total no. of units', ascending=False)

        # Calculate summary statistics
        total_units = total_units_dev
        total_developers = dev_units_df.shape[0]
        max_units_row = dev_units_df.iloc[0]
        max_units_dev = max_units_row['Developer Name']
        max_units_value = max_units_row['Total no. of units']
        min_units_row = dev_units_df[dev_units_df['Total no. of units'] > 0].iloc[-1]
        min_units_dev = min_units_row['Developer Name']
        min_units_value = min_units_row['Total no. of units']

        summary_data = {
            'Metric': ['Total Units', 'Total Developers', 'Developer with Max Units', 'Max Units', 'Developer with Min Units', 'Min Units'],
            'Value': [total_units, total_developers, max_units_dev, max_units_value, min_units_dev, min_units_value]
        }

        summary_df = pd.DataFrame(summary_data)

        # Generate the summary table
        summary_table = dash_table.DataTable(
            data=summary_df.to_dict('records'),
            columns=[{"name": i, "id": i} for i in summary_df.columns],
            style_table={'overflowX': 'auto', 'border': '1px solid #ccc', 'width': '50%'},
            style_cell={
                'textAlign': 'left',
                'padding': '10px',
                'fontSize': '14px',
                'fontFamily': 'Arial',
            },
            style_header={
                'backgroundColor': '#ffc107',
                'fontWeight': 'bold',
                'color': 'black',
                'textAlign': 'center'
            },
            fixed_rows={'headers': True},
            sort_action='native',
            page_action='none',
            editable=False
        )

        # Generate the main table with all developers
        main_table = dash_table.DataTable(
            data=dev_units_df.to_dict('records'),
            columns=[{"name": i, "id": i} for i in dev_units_df.columns],
            style_table={'overflowX': 'auto', 'border': '1px solid #ccc', 'width': '100%'},
            style_cell={
                'textAlign': 'center',
                'padding': '10px',
                'fontSize': '12px',
                'fontFamily': 'Arial',
                'height': 'auto',
                'whiteSpace': 'normal',
            },
            style_header={
                'backgroundColor': '#17a2b8',
                'fontWeight': 'bold',
                'color': 'white',
                'textAlign': 'center'
            },
            sort_action='native',
            page_action='none',
            editable=False
        )

        # Create dual-axis chart for total units and percentage
        fig_dev = make_subplots(specs=[[{"secondary_y": True}]])

        fig_dev.add_trace(
            go.Bar(x=dev_units_df['Developer Name'], y=dev_units_df['Total no. of units'], name='Total Units'),
            secondary_y=False,
        )

        fig_dev.add_trace(
            go.Scatter(x=dev_units_df['Developer Name'], y=dev_units_df['Percentage'], name='Percentage (%)', mode='lines+markers'),
            secondary_y=True,
        )

        fig_dev.update_layout(
            title_text="Developers Total Units and Percentage",
            xaxis_tickangle=-45,
            xaxis_title='Developer Name',
            font=dict(size=12),
            height=600,
            margin=dict(l=40, r=40, t=40, b=200),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )

        fig_dev.update_yaxes(title_text='Total Units', secondary_y=False)
        fig_dev.update_yaxes(title_text='Percentage (%)', secondary_y=True)
        fig_dev.update_xaxes(tickangle=45)

        return [
            dbc.Card(dbc.CardBody([
                html.H4("Data Summary", className='card-title'),
                summary_table,
            ]), className='mb-4'),
            dbc.Card(dbc.CardBody([
                html.H4("Developers Total Units and Percentage", className='card-title'),
                main_table,
            ]), className='mb-4'),
            dbc.Row([
                dbc.Col(dcc.Graph(figure=fig_dev), md=12)
            ])
        ]

    elif view == 'AREA_QUARTERLY':
        area_units_df = filtered_df.groupby(['Area', 'YearQuarter']).agg({'Total no. of units': 'sum'}).reset_index()
        if area_units_df.empty:
            return html.Div('No data available for the selected filters.')

        # Pivot and calculate percentages
        pivot_area_df = area_units_df.pivot(index='Area', columns='YearQuarter', values='Total no. of units').fillna(0)
        total_per_area = pivot_area_df.sum(axis=1)
        pivot_area_df_percentage = pivot_area_df.div(total_per_area, axis=0) * 100
        pivot_area_df_percentage = pivot_area_df_percentage.round(2)

        # Calculate summary statistics
        total_units = area_units_df['Total no. of units'].sum()
        total_areas = pivot_area_df.shape[0]
        total_units_by_area = area_units_df.groupby('Area')['Total no. of units'].sum().reset_index()
        total_units_by_area = total_units_by_area.sort_values(by='Total no. of units', ascending=False)
        max_units_row = total_units_by_area.iloc[0]
        max_units_area = max_units_row['Area']
        max_units_value = max_units_row['Total no. of units']
        min_units_row = total_units_by_area[total_units_by_area['Total no. of units'] > 0].iloc[-1]
        min_units_area = min_units_row['Area']
        min_units_value = min_units_row['Total no. of units']

        summary_data = {
            'Metric': ['Total Units', 'Total Areas', 'Area with Max Units', 'Max Units', 'Area with Min Units', 'Min Units'],
            'Value': [total_units, total_areas, max_units_area, max_units_value, min_units_area, min_units_value]
        }

        summary_df = pd.DataFrame(summary_data)

        # Generate the summary table
        summary_table = dash_table.DataTable(
            data=summary_df.to_dict('records'),
            columns=[{"name": i, "id": i} for i in summary_df.columns],
            style_table={'overflowX': 'auto', 'border': '1px solid #ccc', 'width': '50%'},
            style_cell={
                'textAlign': 'left',
                'padding': '10px',
                'fontSize': '14px',
                'fontFamily': 'Arial',
            },
            style_header={
                'backgroundColor': '#ffc107',
                'fontWeight': 'bold',
                'color': 'black',
                'textAlign': 'center'
            },
            fixed_rows={'headers': True},
            sort_action='native',
            page_action='none',
            editable=False
        )

        # Generate the main table
        main_table = dash_table.DataTable(
            data=pivot_area_df.reset_index().to_dict('records'),
            columns=[{"name": i, "id": i} for i in ['Area'] + list(pivot_area_df.columns)],
            style_table={'overflowX': 'auto', 'border': '1px solid #ccc', 'width': '100%'},
            style_cell={
                'textAlign': 'center',
                'padding': '5px',
                'fontSize': '12px',
                'fontFamily': 'Arial',
                'height': 'auto',
                'whiteSpace': 'normal',
            },
            style_header={
                'backgroundColor': '#17a2b8',
                'fontWeight': 'bold',
                'color': 'white',
                'textAlign': 'center'
            },
            sort_action='native',
            page_action='none',
            editable=False
        )

        # Generate the percentage table
        percentage_table = dash_table.DataTable(
            data=pivot_area_df_percentage.reset_index().to_dict('records'),
            columns=[{"name": i, "id": i} for i in ['Area'] + list(pivot_area_df_percentage.columns)],
            style_table={'overflowX': 'auto', 'border': '1px solid #ccc', 'width': '100%', 'marginTop': '20px'},
            style_cell={
                'textAlign': 'center',
                'padding': '5px',
                'fontSize': '12px',
                'fontFamily': 'Arial',
                'height': 'auto',
                'whiteSpace': 'normal',
            },
            style_header={
                'backgroundColor': '#28a745',
                'fontWeight': 'bold',
                'color': 'white',
                'textAlign': 'center'
            },
            sort_action='native',
            page_action='none',
            editable=False
        )

        # Update graphs for readability
        bar_fig_area = px.bar(area_units_df, x='YearQuarter', y='Total no. of units', color='Area',
                              title='Units Launched in Area by Quarter (Stacked Bar)')
        bar_fig_area.update_layout(
            xaxis_tickangle=-45,
            xaxis_title='Year-Quarter',
            yaxis_title='Total Units',
            font=dict(size=12),
            height=500,
            margin=dict(l=40, r=40, t=40, b=120)
        )

        return [
            dbc.Card(dbc.CardBody([
                html.H4("Data Summary", className='card-title'),
                summary_table,
            ]), className='mb-4'),
            dbc.Card(dbc.CardBody([
                html.H4("Units Launched by Area", className='card-title'),
                main_table,
                html.H4("Percentage Contribution", className='card-title mt-4'),
                percentage_table
            ]), className='mb-4'),
            dbc.Row([
                dbc.Col(dcc.Graph(figure=bar_fig_area), md=12)
            ])
        ]

    elif view == 'ASSET_YEARLY':
        asset_units_df = filtered_df.groupby(['Asset Type', 'Year']).agg({'Total no. of units': 'sum'}).reset_index()
        if asset_units_df.empty:
            return html.Div('No data available for the selected filters.')

        # Pivot and calculate percentages
        pivot_asset_df = asset_units_df.pivot(index='Asset Type', columns='Year', values='Total no. of units').fillna(0)
        total_per_asset = pivot_asset_df.sum(axis=1)
        pivot_asset_df_percentage = pivot_asset_df.div(total_per_asset, axis=0) * 100
        pivot_asset_df_percentage = pivot_asset_df_percentage.round(2)

        # Calculate summary statistics
        total_units = asset_units_df['Total no. of units'].sum()
        total_asset_types = pivot_asset_df.shape[0]
        total_units_by_asset = asset_units_df.groupby('Asset Type')['Total no. of units'].sum().reset_index()
        total_units_by_asset = total_units_by_asset.sort_values(by='Total no. of units', ascending=False)
        max_units_row = total_units_by_asset.iloc[0]
        max_units_asset = max_units_row['Asset Type']
        max_units_value = max_units_row['Total no. of units']
        min_units_row = total_units_by_asset.iloc[-1]
        min_units_asset = min_units_row['Asset Type']
        min_units_value = min_units_row['Total no. of units']

        summary_data = {
            'Metric': ['Total Units', 'Total Asset Types', 'Asset Type with Max Units', 'Max Units', 'Asset Type with Min Units', 'Min Units'],
            'Value': [total_units, total_asset_types, max_units_asset, max_units_value, min_units_asset, min_units_value]
        }

        summary_df = pd.DataFrame(summary_data)

        # Generate the summary table
        summary_table = dash_table.DataTable(
            data=summary_df.to_dict('records'),
            columns=[{"name": i, "id": i} for i in summary_df.columns],
            style_table={'overflowX': 'auto', 'border': '1px solid #ccc', 'width': '50%'},
            style_cell={
                'textAlign': 'left',
                'padding': '10px',
                'fontSize': '14px',
                'fontFamily': 'Arial',
            },
            style_header={
                'backgroundColor': '#ffc107',
                'fontWeight': 'bold',
                'color': 'black',
                'textAlign': 'center'
            },
            fixed_rows={'headers': True},
            sort_action='native',
            page_action='none',
            editable=False
        )

        # Generate the main table
        main_table = dash_table.DataTable(
            data=pivot_asset_df.reset_index().to_dict('records'),
            columns=[{"name": str(i), "id": str(i)} for i in ['Asset Type'] + list(pivot_asset_df.columns)],
            style_table={'overflowX': 'auto', 'border': '1px solid #ccc', 'width': '100%'},
            style_cell={
                'textAlign': 'center',
                'padding': '5px',
                'fontSize': '12px',
                'fontFamily': 'Arial',
                'height': 'auto',
            },
            style_header={
                'backgroundColor': '#17a2b8',
                'fontWeight': 'bold',
                'color': 'white',
                'textAlign': 'center'
            },
            sort_action='native',
            page_action='none',
            editable=False
        )

        # Generate the percentage table
        percentage_table = dash_table.DataTable(
            data=pivot_asset_df_percentage.reset_index().to_dict('records'),
            columns=[{"name": str(i), "id": str(i)} for i in ['Asset Type'] + list(pivot_asset_df_percentage.columns)],
            style_table={'overflowX': 'auto', 'border': '1px solid #ccc', 'width': '100%', 'marginTop': '20px'},
            style_cell={
                'textAlign': 'center',
                'padding': '5px',
                'fontSize': '12px',
                'fontFamily': 'Arial',
                'height': 'auto',
            },
            style_header={
                'backgroundColor': '#28a745',
                'fontWeight': 'bold',
                'color': 'white',
                'textAlign': 'center'
            },
            sort_action='native',
            page_action='none',
            editable=False
        )

        # Update graphs for readability
        bar_fig_asset = px.bar(asset_units_df, x='Year', y='Total no. of units', color='Asset Type',
                               title='Asset Type Launched Year-wise (Stacked Bar)')
        bar_fig_asset.update_layout(
            xaxis_tickangle=-45,
            xaxis_title='Year',
            yaxis_title='Total Units',
            font=dict(size=12),
            height=500,
            margin=dict(l=40, r=40, t=40, b=80)
        )

        return [
            dbc.Card(dbc.CardBody([
                html.H4("Data Summary", className='card-title'),
                summary_table,
            ]), className='mb-4'),
            dbc.Card(dbc.CardBody([
                html.H4("Units Launched by Asset Type", className='card-title'),
                main_table,
                html.H4("Percentage Contribution", className='card-title mt-4'),
                percentage_table
            ]), className='mb-4'),
            dbc.Row([
                dbc.Col(dcc.Graph(figure=bar_fig_asset), md=12)
            ])
        ]

    else:
        return html.Div('Select a valid graph type')

# Run the app
if __name__ == "__main__":
    app.run_server(host='0.0.0.0', port=10000, debug=True)