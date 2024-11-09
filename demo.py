import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.graph_objects as go
import plotly.express as px

# Load and clean data
data = pd.read_excel('/mnt/data/TruEstimate Final Sheet Project (3).xlsx', header=1)
data['Launch Date'] = pd.to_datetime(data['Launch Date'], errors='coerce')
data['Handover date'] = pd.to_datetime(data['Handover date'], errors='coerce')
data['Developer Name'] = data['Developer Name'].str.strip()
data['Area'] = data['Area'].str.title()
filtered_data = data[data['Launch Date'] > '2022-10-01']

# Calculate time to handover
filtered_data['Handover Time (Months)'] = (filtered_data['Handover date'] - filtered_data['Launch Date']).dt.days // 30

# Initialize Dash app
app = Dash(__name__)

# Define graph options
graph_options = [
    {'label': 'Handover by Area Over Time', 'value': 'handover_area'},
    {'label': 'New Launches by Area Over Time', 'value': 'new_launches_area'},
    {'label': 'Total Project Size Over Time', 'value': 'total_project_size'},
    {'label': 'Asset Type Distribution Over Time', 'value': 'asset_type_distribution'},
    {'label': 'Number of Projects by Area Over Time (Cumulative)', 'value': 'projects_area_cumulative'},
    {'label': 'Developer Dominance in Unit Volume (Swapped Axes)', 'value': 'developer_unit_volume'},
    {'label': 'Time to Handover by Developer and Asset Type (Median)', 'value': 'handover_time_developer'},
    {'label': 'Total Number of Units by Area Over Time', 'value': 'total_units_area'},
    # More specific graphs for each area and configuration
    {'label': 'Asset Type by Area Over Time (Units) - North', 'value': 'asset_type_north_units'},
    {'label': 'Asset Type by Area Over Time (Units) - East', 'value': 'asset_type_east_units'},
    {'label': 'Asset Type by Area Over Time (Units) - South', 'value': 'asset_type_south_units'},
    {'label': 'Asset Type by Area Over Time (Units) - West', 'value': 'asset_type_west_units'},
    {'label': 'Asset Type by Area Over Time (Projects) - North', 'value': 'asset_type_north_projects'},
    {'label': 'Asset Type by Area Over Time (Projects) - East', 'value': 'asset_type_east_projects'},
    {'label': 'Asset Type by Area Over Time (Projects) - South', 'value': 'asset_type_south_projects'},
    {'label': 'Asset Type by Area Over Time (Projects) - West', 'value': 'asset_type_west_projects'},
    # Developer Dominance by Asset Type and Area
    {'label': 'Developer Dominance (Total Units) - Apartment', 'value': 'developer_dominance_apartment'},
    {'label': 'Developer Dominance (Total Units) - Plot', 'value': 'developer_dominance_plot'},
    {'label': 'Developer Dominance (Total Units) - Villa', 'value': 'developer_dominance_villa'},
    # Configuration breakdown by area over time
    {'label': 'Apartment Configuration by Area Over Time - North', 'value': 'config_north_apartment'},
    {'label': 'Apartment Configuration by Area Over Time - East', 'value': 'config_east_apartment'},
    {'label': 'Apartment Configuration by Area Over Time - South', 'value': 'config_south_apartment'},
    {'label': 'Apartment Configuration by Area Over Time - West', 'value': 'config_west_apartment'}
]

# Layout
app.layout = html.Div([
    html.H1("TruEstate Bangalore Real Estate Market Dashboard"),
    dcc.Dropdown(id='graph-selector', options=graph_options, value=['handover_area'], multi=True),
    html.Div(id='graph-container')
])

# Callback for rendering
@app.callback(Output('graph-container', 'children'), [Input('graph-selector', 'value')])
def update_graphs(selected_graphs):
    graphs = []

    # Handover by Area Over Time
    if 'handover_area' in selected_graphs:
        handover_by_area = filtered_data.groupby([filtered_data['Handover date'].dt.to_period('Q'), 'Area']).size().unstack()
        fig_handover_area = go.Figure()
        for area in handover_by_area.columns:
            fig_handover_area.add_trace(go.Scatter(
                x=handover_by_area.index.astype(str),
                y=handover_by_area[area],
                mode='lines+markers',
                name=area
            ))
        fig_handover_area.update_layout(title="Handover by Area Over Time", xaxis_title="Time", yaxis_title="Projects")
        graphs.append(dcc.Graph(figure=fig_handover_area))
    
    # New Launches by Area Over Time
    if 'new_launches_area' in selected_graphs:
        new_launches = filtered_data.groupby([filtered_data['Launch Date'].dt.to_period('Q'), 'Area']).size().unstack()
        fig_new_launches = go.Figure()
        for area in new_launches.columns:
            fig_new_launches.add_trace(go.Scatter(
                x=new_launches.index.astype(str),
                y=new_launches[area],
                mode='lines+markers',
                name=area
            ))
        fig_new_launches.update_layout(title="New Launches by Area Over Time", xaxis_title="Time", yaxis_title="Projects")
        graphs.append(dcc.Graph(figure=fig_new_launches))

    # Total Project Size Over Time
    if 'total_project_size' in selected_graphs:
        project_size_trend = filtered_data.groupby(filtered_data['Launch Date'].dt.to_period('Q'))['Project Area (Acres)'].sum()
        fig_project_size = go.Figure(go.Scatter(
            x=project_size_trend.index.astype(str),
            y=project_size_trend.values,
            mode='lines+markers',
            name='Total Project Size'
        ))
        fig_project_size.update_layout(title="Total Project Size Over Time", xaxis_title="Quarter", yaxis_title="Total Size (Acres)")
        graphs.append(dcc.Graph(figure=fig_project_size))

    # Asset Type Distribution Over Time
    if 'asset_type_distribution' in selected_graphs:
        asset_type_trend = filtered_data.groupby([filtered_data['Launch Date'].dt.to_period('Q'), 'Asset Type']).size().unstack()
        fig_asset_type = go.Figure()
        for asset_type in asset_type_trend.columns:
            fig_asset_type.add_trace(go.Scatter(
                x=asset_type_trend.index.astype(str),
                y=asset_type_trend[asset_type],
                mode='lines+markers',
                name=f'{asset_type} Projects'
            ))
        fig_asset_type.update_layout(title="Asset Type Distribution Over Time", xaxis_title="Quarter", yaxis_title="Projects")
        graphs.append(dcc.Graph(figure=fig_asset_type))

    # Number of Projects by Area Over Time (Cumulative)
    if 'projects_area_cumulative' in selected_graphs:
        projects_trend = filtered_data.groupby([filtered_data['Launch Date'].dt.to_period('Q'), 'Area']).size().unstack().cumsum()
        fig_projects_cumulative = go.Figure()
        for area in projects_trend.columns:
            fig_projects_cumulative.add_trace(go.Scatter(
                x=projects_trend.index.astype(str),
                y=projects_trend[area],
                mode='lines+markers',
                name=f'Projects in {area}'
            ))
        fig_projects_cumulative.update_layout(title="Number of Projects by Area Over Time (Cumulative)", xaxis_title="Quarter", yaxis_title="Cumulative Projects")
        graphs.append(dcc.Graph(figure=fig_projects_cumulative))

    # Developer Dominance in Unit Volume (Swapped Axes)
    if 'developer_unit_volume' in selected_graphs:
        dev_unit_counts = filtered_data.groupby('Developer Name')['Total no. of units'].sum().sort_values()
        fig_dev_unit_volume = px.bar(
            x=dev_unit_counts.values,
            y=dev_unit_counts.index,
            orientation='h',
            title="Developer Dominance in Unit Volume (Swapped Axes)",
            labels={'x': 'Total Units', 'y': 'Developer'}
        )
        graphs.append(dcc.Graph(figure=fig_dev_unit_volume))

    # Time to Handover by Developer and Asset Type (Median)
    if 'handover_time_developer' in selected_graphs:
        handover_median = filtered_data.groupby(['Developer Name', 'Asset Type'])['Handover Time (Months)'].median().unstack()
        fig_handover_time = go.Figure()
        for asset_type in handover_median.columns:
            fig_handover_time.add_trace(go.Bar(
                x=handover_median.index,
                y=handover_median[asset_type],
                name=asset_type
            ))
        fig_handover_time.update_layout(title="Time to Handover by Developer and Asset Type (Median)", xaxis_title="Developer", yaxis_title="Median Handover Time (Months)")
        graphs.append(dcc.Graph(figure=fig_handover_time))
    
    # Repeat similar setup for each specific graph option
    # Asset Type by Area Over Time (Units) - East
    if 'asset_type_east_units' in selected_graphs:
        east_data = filtered_data[filtered_data['Area'] == 'East']
        asset_type_east_units = east_data.groupby([east_data['Launch Date'].dt.to_period('Q'), 'Asset Type'])['Total no. of units'].sum().unstack()
        fig_asset_type_east_units = go.Figure()
        for asset_type in asset_type_east_units.columns:
            fig_asset_type_east_units.add_trace(go.Scatter(
                x=asset_type_east_units.index.astype(str),
                y=asset_type_east_units[asset_type],
                mode='lines+markers',
                name=asset_type
            ))
        fig_asset_type_east_units.update_layout(title="Asset Type by Area Over Time (Units) - East", xaxis_title="Quarter", yaxis_title="Total Units")
        graphs.append(dcc.Graph(figure=fig_asset_type_east_units))

    # Asset Type by Area Over Time (Units) - South
    if 'asset_type_south_units' in selected_graphs:
        south_data = filtered_data[filtered_data['Area'] == 'South']
        asset_type_south_units = south_data.groupby([south_data['Launch Date'].dt.to_period('Q'), 'Asset Type'])['Total no. of units'].sum().unstack()
        fig_asset_type_south_units = go.Figure()
        for asset_type in asset_type_south_units.columns:
            fig_asset_type_south_units.add_trace(go.Scatter(
                x=asset_type_south_units.index.astype(str),
                y=asset_type_south_units[asset_type],
                mode='lines+markers',
                name=asset_type
            ))
        fig_asset_type_south_units.update_layout(title="Asset Type by Area Over Time (Units) - South", xaxis_title="Quarter", yaxis_title="Total Units")
        graphs.append(dcc.Graph(figure=fig_asset_type_south_units))

    # Asset Type by Area Over Time (Units) - West
    if 'asset_type_west_units' in selected_graphs:
        west_data = filtered_data[filtered_data['Area'] == 'West']
        asset_type_west_units = west_data.groupby([west_data['Launch Date'].dt.to_period('Q'), 'Asset Type'])['Total no. of units'].sum().unstack()
        fig_asset_type_west_units = go.Figure()
        for asset_type in asset_type_west_units.columns:
            fig_asset_type_west_units.add_trace(go.Scatter(
                x=asset_type_west_units.index.astype(str),
                y=asset_type_west_units[asset_type],
                mode='lines+markers',
                name=asset_type
            ))
        fig_asset_type_west_units.update_layout(title="Asset Type by Area Over Time (Units) - West", xaxis_title="Quarter", yaxis_title="Total Units")
        graphs.append(dcc.Graph(figure=fig_asset_type_west_units))

    # Developer Dominance (Total Units) - Apartment
    if 'developer_dominance_apartment' in selected_graphs:
        apartment_data = filtered_data[filtered_data['Asset Type'] == 'Apartment']
        dev_apartment_units = apartment_data.groupby('Developer Name')['Total no. of units'].sum().sort_values()
        fig_dev_apartment_units = px.bar(
            x=dev_apartment_units.values,
            y=dev_apartment_units.index,
            orientation='h',
            title="Developer Dominance (Total Units) - Apartment",
            labels={'x': 'Total Units', 'y': 'Developer'}
        )
        graphs.append(dcc.Graph(figure=fig_dev_apartment_units))

    # Developer Dominance (Total Units) - Plot
    if 'developer_dominance_plot' in selected_graphs:
        plot_data = filtered_data[filtered_data['Asset Type'] == 'Plot']
        dev_plot_units = plot_data.groupby('Developer Name')['Total no. of units'].sum().sort_values()
        fig_dev_plot_units = px.bar(
            x=dev_plot_units.values,
            y=dev_plot_units.index,
            orientation='h',
            title="Developer Dominance (Total Units) - Plot",
            labels={'x': 'Total Units', 'y': 'Developer'}
        )
        graphs.append(dcc.Graph(figure=fig_dev_plot_units))

    # Developer Dominance (Total Units) - Villa
    if 'developer_dominance_villa' in selected_graphs:
        villa_data = filtered_data[filtered_data['Asset Type'] == 'Villa']
        dev_villa_units = villa_data.groupby('Developer Name')['Total no. of units'].sum().sort_values()
        fig_dev_villa_units = px.bar(
            x=dev_villa_units.values,
            y=dev_villa_units.index,
            orientation='h',
            title="Developer Dominance (Total Units) - Villa",
            labels={'x': 'Total Units', 'y': 'Developer'}
        )
        graphs.append(dcc.Graph(figure=fig_dev_villa_units))

    # Apartment Configuration by Area Over Time - North
    if 'config_north_apartment' in selected_graphs:
        north_data = filtered_data[(filtered_data['Area'] == 'North') & (filtered_data['Asset Type'] == 'Apartment')]
        config_north_apartment = north_data.groupby([north_data['Launch Date'].dt.to_period('Q'), 'Configuration']).size().unstack()
        fig_config_north_apartment = go.Figure()
        for config in config_north_apartment.columns:
            fig_config_north_apartment.add_trace(go.Scatter(
                x=config_north_apartment.index.astype(str),
                y=config_north_apartment[config],
                mode='lines+markers',
                name=config
            ))
        fig_config_north_apartment.update_layout(title="Apartment Configuration by Area Over Time - North", xaxis_title="Quarter", yaxis_title="Total Units")
        graphs.append(dcc.Graph(figure=fig_config_north_apartment))

    # Apartment Configuration by Area Over Time - East
    if 'config_east_apartment' in selected_graphs:
        east_data = filtered_data[(filtered_data['Area'] == 'East') & (filtered_data['Asset Type'] == 'Apartment')]
        config_east_apartment = east_data.groupby([east_data['Launch Date'].dt.to_period('Q'), 'Configuration']).size().unstack()
        fig_config_east_apartment = go.Figure()
        for config in config_east_apartment.columns:
            fig_config_east_apartment.add_trace(go.Scatter(
                x=config_east_apartment.index.astype(str),
                y=config_east_apartment[config],
                mode='lines+markers',
                name=config
            ))
        fig_config_east_apartment.update_layout(title="Apartment Configuration by Area Over Time - East", xaxis_title="Quarter", yaxis_title="Total Units")
        graphs.append(dcc.Graph(figure=fig_config_east_apartment))

    # Apartment Configuration by Area Over Time - South
    if 'config_south_apartment' in selected_graphs:
        south_data = filtered_data[(filtered_data['Area'] == 'South') & (filtered_data['Asset Type'] == 'Apartment')]
        config_south_apartment = south_data.groupby([south_data['Launch Date'].dt.to_period('Q'), 'Configuration']).size().unstack()
        fig_config_south_apartment = go.Figure()
        for config in config_south_apartment.columns:
            fig_config_south_apartment.add_trace(go.Scatter(
                x=config_south_apartment.index.astype(str),
                y=config_south_apartment[config],
                mode='lines+markers',
                name=config
            ))
        fig_config_south_apartment.update_layout(title="Apartment Configuration by Area Over Time - South", xaxis_title="Quarter", yaxis_title="Total Units")
        graphs.append(dcc.Graph(figure=fig_config_south_apartment))

    # Apartment Configuration by Area Over Time - West
    if 'config_west_apartment' in selected_graphs:
        west_data = filtered_data[(filtered_data['Area'] == 'West') & (filtered_data['Asset Type'] == 'Apartment')]
        config_west_apartment = west_data.groupby([west_data['Launch Date'].dt.to_period('Q'), 'Configuration']).size().unstack()
        fig_config_west_apartment = go.Figure()
        for config in config_west_apartment.columns:
            fig_config_west_apartment.add_trace(go.Scatter(
                x=config_west_apartment.index.astype(str),
                y=config_west_apartment[config],
                mode='lines+markers',
                name=config
            ))
        fig_config_west_apartment.update_layout(title="Apartment Configuration by Area Over Time - West", xaxis_title="Quarter", yaxis_title="Total Units")
        graphs.append(dcc.Graph(figure=fig_config_west_apartment))

    return graphs
