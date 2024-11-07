import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.graph_objects as go
import plotly.express as px

# Load and clean data
data = pd.read_excel(r"C:\Users\layek\Downloads\TruEstimate Final Sheet Project (2).xlsx", header=1)
data['Launch Date'] = pd.to_datetime(data['Launch Date'], errors='coerce')
data['Handover date'] = pd.to_datetime(data['Handover date'], errors='coerce')
data['Developer Name'] = data['Developer Name'].str.strip()  # Remove extra whitespace in developer names
data['Area'] = data['Area'].str.title()  # Normalize area names to title case
filtered_data = data[data['Launch Date'] > '2022-10-01']

# Calculate Time to Handover
# Calculate Time to Handover
filtered_data = filtered_data.copy()  # Create a copy to safely modify it
filtered_data['Handover Time (Months)'] = (filtered_data['Handover date'] - filtered_data['Launch Date']).dt.days // 30


# Initialize the Dash app
app = Dash(__name__)

# Define available graph options
graph_options = [
    {'label': 'Total Number of Units by Area Over Time', 'value': 'total_units_area'},
    {'label': 'Asset Type by Area Over Time', 'value': 'asset_type_area'},
    {'label': 'Number of Projects by Area Over Time', 'value': 'projects_area'},
    {'label': 'New Launches by Area Over Time', 'value': 'new_launches_area'},
    {'label': 'Handover by Area Over Time', 'value': 'handover_area'},
    {'label': 'Total Project Size Over Time', 'value': 'project_size'},
    {'label': 'Project Size Distribution Over Time', 'value': 'size_distribution'},
    {'label': 'Asset Type Distribution Over Time', 'value': 'asset_type_distribution'},
    {'label': 'Configuration by Area Over Time', 'value': 'configuration_area'},
    {'label': 'Famous Developer Quarterly Project Launches', 'value': 'famous_dev_quarterly'},
    {'label': 'Famous Developer Total Projects (Pie Chart)', 'value': 'famous_dev_pie'},
    {'label': 'Asset Type Distribution (Pie Chart)', 'value': 'asset_type_pie'},
    # New graphs based on additional insights
    {'label': 'Developer Dominance in Unit Volume', 'value': 'developer_unit_volume'},
    {'label': 'Project Size vs. Unit Count Scatter Plot', 'value': 'project_size_vs_unit_count'},
    {'label': 'Time to Handover by Developer', 'value': 'handover_time_developer'},
    {'label': 'Trend in Total Units by Asset Type', 'value': 'trend_total_units_asset_type'},
    {'label': 'Project Density by Area', 'value': 'project_density_area'}
]

# Layout of the dashboard
app.layout = html.Div([
    html.H1("TruEstate Bangalore Real Estate Market Dashboard"),
    
    # Dropdown for selecting graph types
    html.Label("Select Graphs to Display:"),
    dcc.Dropdown(
        id='graph-selector',
        options=graph_options,
        value=['developer_unit_volume'],  # Default selected graph
        multi=True
    ),

    # Placeholder for graphs
    html.Div(id='graph-container')
])

# Callback to update graphs dynamically
@app.callback(
    Output('graph-container', 'children'),
    Input('graph-selector', 'value')
)
def update_graphs(selected_graphs):
    graphs = []

    # Developer Dominance in Unit Volume
    if 'developer_unit_volume' in selected_graphs:
        dev_unit_counts = filtered_data.groupby('Developer Name')['Total no. of units'].sum().sort_values()
        fig_dev_unit_volume = px.bar(
            x=dev_unit_counts.values,
            y=dev_unit_counts.index,
            orientation='h',
            title="Developer Dominance in Unit Volume",
            labels={'x': 'Total Units', 'y': 'Developer'}
        )
        graphs.append(dcc.Graph(figure=fig_dev_unit_volume))

    # Project Size vs. Unit Count Scatter Plot
    if 'project_size_vs_unit_count' in selected_graphs:
        fig_project_size_units = px.scatter(
            filtered_data,
            x='Project Area (Acres)',
            y='Total no. of units',
            color='Developer Name',
            title="Project Size vs. Unit Count by Developer",
            labels={'Project Area (Acres)': 'Project Size (Acres)', 'Total no. of units': 'Unit Count'}
        )
        graphs.append(dcc.Graph(figure=fig_project_size_units))

    # Time to Handover by Developer
    if 'handover_time_developer' in selected_graphs:
        fig_handover_time = px.box(
            filtered_data,
            x='Developer Name',
            y='Handover Time (Months)',
            title="Time to Handover by Developer",
            labels={'Handover Time (Months)': 'Handover Time (Months)', 'Developer Name': 'Developer'}
        )
        fig_handover_time.update_layout(xaxis={'categoryorder':'total descending'})
        graphs.append(dcc.Graph(figure=fig_handover_time))

    # Trend in Total Units by Asset Type
    if 'trend_total_units_asset_type' in selected_graphs:
        asset_type_trend = filtered_data.groupby([filtered_data['Launch Date'].dt.to_period('Q'), 'Asset Type'])['Total no. of units'].sum().unstack()
        fig_asset_trend = go.Figure()
        for asset_type in asset_type_trend.columns:
            fig_asset_trend.add_trace(go.Scatter(
                x=asset_type_trend.index.strftime("Q%q %Y"),
                y=asset_type_trend[asset_type],
                mode='lines+markers',
                name=f'{asset_type} Units'
            ))
        fig_asset_trend.update_layout(
            title="Trend in Total Units by Asset Type",
            xaxis_title="Quarter",
            yaxis_title="Total Units",
            template="plotly_white"
        )
        graphs.append(dcc.Graph(figure=fig_asset_trend))

    # Project Density by Area
    if 'project_density_area' in selected_graphs:
        area_density = filtered_data.groupby('Area').agg({
            'Total no. of units': 'sum',
            'Project Area (Acres)': 'mean'
        }).reset_index()
        fig_density_area = px.scatter(
            area_density,
            x='Area',
            y='Total no. of units',
            size='Project Area (Acres)',
            color='Area',
            title="Project Density by Area",
            labels={'Total no. of units': 'Total Units', 'Project Area (Acres)': 'Average Project Size (Acres)'}
        )
        graphs.append(dcc.Graph(figure=fig_density_area))

    # Asset Type Distribution (Pie Chart)
    if 'asset_type_pie' in selected_graphs:
        asset_type_counts = filtered_data['Asset Type'].value_counts()
        fig_asset_type_pie = px.pie(
            names=asset_type_counts.index,
            values=asset_type_counts.values,
            title="Asset Type Distribution",
            labels={'values': 'Units', 'names': 'Asset Type'}
        )
        fig_asset_type_pie.update_traces(textinfo='percent+label')
        graphs.append(dcc.Graph(figure=fig_asset_type_pie))

    # Famous Developer Total Projects (Pie Chart)
    if 'famous_dev_pie' in selected_graphs:
        famous_developers = ['Prestige', 'Brigade', 'Sobha', 'Assetz', 'Birla', 'Mahindra', 'Adarsh', 'Puravankara', 'Raheja']
        famous_dev_data = filtered_data[filtered_data['Developer Name'].isin(famous_developers)]
        dev_project_counts = famous_dev_data['Developer Name'].value_counts()

        fig_dev_pie = px.pie(
            names=dev_project_counts.index,
            values=dev_project_counts.values,
            title="Total Projects by Famous Developer",
            labels={'values': 'Project Count', 'names': 'Developer Name'}
        )
        fig_dev_pie.update_traces(textinfo='percent+label')
        graphs.append(dcc.Graph(figure=fig_dev_pie))

    # Number of Projects by Area Over Time
    if 'projects_area' in selected_graphs:
        projects_trend = filtered_data.groupby([filtered_data['Launch Date'].dt.to_period('Q'), 'Area']).size().unstack()
        
        fig_projects = go.Figure()
        for area in projects_trend.columns:
            fig_projects.add_trace(go.Scatter(
                x=projects_trend.index.strftime("Q%q %Y"),
                y=projects_trend[area],
                mode='lines+markers',
                name=f'Projects in {area}'
            ))
        fig_projects.update_layout(
            title="Number of Projects by Area Over Time",
            xaxis_title="Quarter",
            yaxis_title="Total Projects",
            template="plotly_white"
        )
        graphs.append(dcc.Graph(figure=fig_projects))

       # New Launches by Area Over Time
    if 'new_launches_area' in selected_graphs:
        new_launches = filtered_data.groupby([filtered_data['Launch Date'].dt.to_period('Q'), 'Area']).size().unstack()
        
        fig_launches = go.Figure()
        for area in new_launches.columns:
            fig_launches.add_trace(go.Scatter(
                x=new_launches.index.strftime("Q%q %Y"),
                y=new_launches[area],
                mode='lines+markers',
                name=f'New Launches in {area}'
            ))
        fig_launches.update_layout(
            title="New Launches by Area Over Time",
            xaxis_title="Quarter",
            yaxis_title="Number of New Projects",
            template="plotly_white"
        )
        graphs.append(dcc.Graph(figure=fig_launches))

    # Handover by Area Over Time
    if 'handover_area' in selected_graphs:
        handover_trend = filtered_data.groupby([filtered_data['Handover date'].dt.to_period('Q'), 'Area']).size().unstack()
        
        fig_handover = go.Figure()
        for area in handover_trend.columns:
            fig_handover.add_trace(go.Scatter(
                x=handover_trend.index.strftime("Q%q %Y"),
                y=handover_trend[area],
                mode='lines+markers',
                name=f'Handover in {area}'
            ))
        fig_handover.update_layout(
            title="Handover by Area Over Time",
            xaxis_title="Quarter",
            yaxis_title="Number of Projects",
            template="plotly_white"
        )
        graphs.append(dcc.Graph(figure=fig_handover))

    # Total Project Size Over Time
    if 'project_size' in selected_graphs:
        project_size_trend = filtered_data.groupby(filtered_data['Launch Date'].dt.to_period('Q'))['Project Area (Acres)'].sum()
        
        fig_project_size = go.Figure(go.Scatter(
            x=project_size_trend.index.strftime("Q%q %Y"),
            y=project_size_trend.values,
            mode='lines+markers',
            name='Total Project Size'
        ))
        fig_project_size.update_layout(
            title="Total Project Size Over Time",
            xaxis_title="Quarter",
            yaxis_title="Total Size (Acres)",
            template="plotly_white"
        )
        graphs.append(dcc.Graph(figure=fig_project_size))

    # Project Size Distribution Over Time
    if 'size_distribution' in selected_graphs:
        fig_size_distribution = px.violin(
            filtered_data,
            x=filtered_data['Launch Date'].dt.to_period('Q').astype(str),
            y='Project Area (Acres)',
            title="Project Size Distribution Over Time"
        )
        fig_size_distribution.update_layout(
            xaxis_title="Quarter",
            yaxis_title="Project Size (Acres)",
            template="plotly_white"
        )
        graphs.append(dcc.Graph(figure=fig_size_distribution))

    # Asset Type Distribution Over Time
    if 'asset_type_distribution' in selected_graphs:
        asset_type_trend = filtered_data.groupby([filtered_data['Launch Date'].dt.to_period('Q'), 'Asset Type'])['Total no. of units'].sum().unstack()
        
        fig_asset_type = go.Figure()
        for asset_type in asset_type_trend.columns:
            fig_asset_type.add_trace(go.Scatter(
                x=asset_type_trend.index.strftime("Q%q %Y"),
                y=asset_type_trend[asset_type],
                mode='lines+markers',
                name=f'{asset_type} Units'
            ))
        fig_asset_type.update_layout(
            title="Asset Type Distribution Over Time",
            xaxis_title="Quarter",
            yaxis_title="Total Units",
            template="plotly_white"
        )
        graphs.append(dcc.Graph(figure=fig_asset_type))

    # Configuration by Area Over Time
    if 'configuration_area' in selected_graphs:
        config_trend = filtered_data.groupby([filtered_data['Launch Date'].dt.to_period('Q'), 'Area', 'Asset Type']).size().unstack(level='Area')
        
        for area in config_trend.columns.levels[1]:  # Separate by each area
            fig_config = go.Figure()
            for asset_type in config_trend[area].columns:
                fig_config.add_trace(go.Scatter(
                    x=config_trend.index.get_level_values(0).strftime("Q%q %Y"),
                    y=config_trend[area][asset_type],
                    mode='lines+markers',
                    name=f'{asset_type}'
                ))
            fig_config.update_layout(
                title=f"Configuration Demand in {area} Over Time",
                xaxis_title="Quarter",
                yaxis_title="Total Units",
                template="plotly_white"
            )
            graphs.append(dcc.Graph(figure=fig_config))

    return graphs

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
