import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.graph_objects as go
import plotly.express as px
import re

# Load and clean data
# Load and clean data using relative path
data = pd.read_excel(r"data/TruEstimate Final Sheet Project (3).xlsx", header=1)
data['Launch Date'] = pd.to_datetime(data['Launch Date'], errors='coerce')
data['Handover date'] = pd.to_datetime(data['Handover date'], errors='coerce')
data['Developer Name'] = data['Developer Name'].str.strip()
data['Area'] = data['Area'].str.title()
data['Asset Type'] = data['Asset Type'].str.strip().str.title()  # Ensure consistent formatting for Asset Type

# Replace 'Land' with 'Plot' to maintain consistency
data['Asset Type'] = data['Asset Type'].replace('Land', 'Plot')

filtered_data = data[(data['Launch Date'] > '2022-10-01') & data['Area'].notna() & data['Total no. of units'].notna()]
filtered_data = filtered_data.copy()  # Avoid SettingWithCopyWarning
filtered_data['Handover Time (Months)'] = (filtered_data['Handover date'] - filtered_data['Launch Date']).dt.days // 30

# Debugging: Check if all asset types are present in the filtered dataset


def clean_bhk_column(df):
    # Helper function to extract the first valid number from a string with multiple values
    def extract_first_number(value):
        if isinstance(value, (int, float)):
            return float(value)  # Already a number
        elif isinstance(value, str):
            # Use regex to find numbers (allowing decimals)
            numbers = re.findall(r'\d+\.?\d*', value)
            if numbers:
                return float(numbers[0])  # Return the first valid number
        return None  # Return None for non-numeric entries or unexpected types

    # Apply extraction only if the Asset Type is Apartment
    df.loc[df['Asset Type'] == 'Apartment', 'BHK'] = df[df['Asset Type'] == 'Apartment']['BHK'].apply(extract_first_number)

    # Drop rows where BHK is None only for Apartments, not for Villas or Plots
    apartment_filtered = df[df['Asset Type'] == 'Apartment'].dropna(subset=['BHK']).copy()
    non_apartment_filtered = df[df['Asset Type'] != 'Apartment'].copy()

    # Ensure all 'BHK' values are float type for Apartments
    if 'BHK' in apartment_filtered.columns:
        apartment_filtered['BHK'] = pd.to_numeric(apartment_filtered['BHK'], errors='coerce')

    # Concatenate back Apartments and non-Apartment types
    df = pd.concat([apartment_filtered, non_apartment_filtered], ignore_index=True)

    return df

# Apply the updated cleaning function to your dataset
filtered_data = clean_bhk_column(filtered_data)

# Debugging: Check filtered data after BHK cleaning


# Apply the cleaning function to your dataset
filtered_data = clean_bhk_column(filtered_data)

# Debugging: Check filtered data after BHK cleaning


# Initialize Dash app
app = Dash(__name__)

# Define the dropdown options
graph_options = [
    {'label': 'Handover by Area Over Time', 'value': 'handover_area'},
    {'label': 'New Launches by Area Over Time', 'value': 'new_launches_area'},
    {'label': 'Total Project Size Over Time', 'value': 'total_project_size'},
    {'label': 'Asset Type Distribution Over Time', 'value': 'asset_type_distribution'},
    {'label': 'Number of Projects by Area Over Time (Cumulative)', 'value': 'projects_area_cumulative'},
    {'label': 'Developer Dominance in Unit Volume', 'value': 'developer_unit_volume'},
    {'label': 'Time to Handover by Developer and Asset Type (Median)', 'value': 'handover_time_developer'},
    {'label': 'Total Number of Units by Area Over Time', 'value': 'total_units_area'},
    {'label': 'Developer Dominance (Total Units) - Apartment', 'value': 'developer_dominance_apartment'},
    {'label': 'Developer Dominance (Total Units) - Plot', 'value': 'developer_dominance_plot'},
    {'label': 'Developer Dominance (Total Units) - Villa', 'value': 'developer_dominance_villa'},
    {'label': 'Famous Developer Quarterly Project Launches', 'value': 'famous_dev_quarterly_launches'},
    {'label': 'Configuration by Area - Apartment', 'value': 'config_by_area_apartment'},
    {'label': 'Configuration by Area - Villa', 'value': 'config_by_area_villa'},
    {'label': 'Configuration by Area - Plot', 'value': 'config_by_area_plot'},
    {'label': 'Handover by Area Over Time - Apartment', 'value': 'handover_by_area_apartment'},
    {'label': 'Handover by Area Over Time - Villa', 'value': 'handover_by_area_villa'},
    {'label': 'Handover by Area Over Time - Plot', 'value': 'handover_by_area_plot'},
    {'label': 'Asset Type by Area Over Time (Total Projects) - North', 'value': 'asset_type_projects_north'},
    {'label': 'Asset Type by Area Over Time (Total Projects) - East', 'value': 'asset_type_projects_east'},
    {'label': 'Asset Type by Area Over Time (Total Projects) - South', 'value': 'asset_type_projects_south'},
    {'label': 'Asset Type by Area Over Time (Total Projects) - West', 'value': 'asset_type_projects_west'},
    {'label': 'Asset Type by Area Over Time (Total Units) - North', 'value': 'asset_type_units_north'},
    {'label': 'Asset Type by Area Over Time (Total Units) - East', 'value': 'asset_type_units_east'},
    {'label': 'Asset Type by Area Over Time (Total Units) - South', 'value': 'asset_type_units_south'},
    {'label': 'Asset Type by Area Over Time (Total Units) - West', 'value': 'asset_type_units_west'},
]

# Layout
app.layout = html.Div([
    html.H1("TruEstate Bangalore Real Estate Market Dashboard"),
    dcc.Dropdown(id='graph-selector', options=graph_options, value='handover_area', multi=False),
    html.Div(id='graph-container')
])

@app.callback(
    Output('graph-container', 'children'),
    [Input('graph-selector', 'value')]
)
def update_graph(selected_graph):
    if selected_graph == 'handover_area':
        return generate_handover_by_area_graph()
    elif selected_graph == 'new_launches_area':
        return generate_new_launches_graph()
    elif selected_graph == 'total_project_size':
        return generate_total_project_size_graph()
    elif selected_graph == 'asset_type_distribution':
        return generate_asset_type_distribution_graph()
    elif selected_graph == 'projects_area_cumulative':
        return generate_projects_area_cumulative_graph()
    elif selected_graph == 'developer_unit_volume':
        return generate_developer_unit_volume_graph()
    elif selected_graph == 'famous_dev_quarterly_launches':
        return generate_famous_developer_quarterly_launches_graph()
    elif selected_graph == 'handover_time_developer':
        return generate_handover_time_developer_graph()
    elif selected_graph == 'total_units_area':
        return generate_total_units_area_graph()
    elif selected_graph == 'developer_dominance_apartment':
        return generate_developer_dominance_graph('Apartment')
    elif selected_graph == 'developer_dominance_villa':
        return generate_developer_dominance_graph('Villa')
    elif selected_graph == 'developer_dominance_plot':
        return generate_developer_dominance_graph('Plot')
    elif selected_graph == 'config_by_area_apartment':
        return generate_configuration_by_area_graph('Apartment')
    elif selected_graph == 'config_by_area_villa':
        return generate_configuration_by_area_graph('Villa')
    elif selected_graph == 'config_by_area_plot':
        return generate_configuration_by_area_graph('Plot')
    elif selected_graph == 'handover_by_area_apartment':
        return generate_handover_by_area_graph('Apartment')
    elif selected_graph == 'handover_by_area_villa':
        return generate_handover_by_area_graph('Villa')
    elif selected_graph == 'handover_by_area_plot':
        return generate_handover_by_area_graph('Plot')
    elif selected_graph == 'asset_type_projects_north':
        return generate_asset_type_projects_graph('North')
    elif selected_graph == 'asset_type_projects_east':
        return generate_asset_type_projects_graph('East')
    elif selected_graph == 'asset_type_projects_south':
        return generate_asset_type_projects_graph('South')
    elif selected_graph == 'asset_type_projects_west':
        return generate_asset_type_projects_graph('West')
    elif selected_graph == 'asset_type_units_north':
        return generate_asset_type_units_graph('North')
    elif selected_graph == 'asset_type_units_east':
        return generate_asset_type_units_graph('East')
    elif selected_graph == 'asset_type_units_south':
        return generate_asset_type_units_graph('South')
    elif selected_graph == 'asset_type_units_west':
        return generate_asset_type_units_graph('West')
    else:
        return html.Div("No graph selected")

# Helper Function: Generate Handover by Area Graph
def generate_handover_by_area_graph(asset_type=None):
    handover_data = filtered_data if asset_type is None else filtered_data[filtered_data['Asset Type'] == asset_type]
    if not handover_data.empty:
        
        handover_data['Handover Quarter'] = handover_data['Handover date'].dt.to_period('Q')
        handover_by_area = handover_data.groupby(['Handover Quarter', 'Area']).size().unstack(fill_value=0)
        fig = go.Figure()
        for area in handover_by_area.columns:
            fig.add_trace(go.Scatter(
                x=handover_by_area.index.astype(str),
                y=handover_by_area[area],
                mode='lines+markers',
                name=area
            ))
        fig.update_layout(
            title=f"{asset_type if asset_type else 'Overall'} Handover by Area Over Time",
            xaxis_title="Quarter",
            yaxis_title="Number of Projects Handover",
            template="plotly_white",
            legend_title="Area"
        )
        return dcc.Graph(figure=fig)
    else:
        return html.Div(f"No data available for {asset_type} Handover by Area")

# Helper Function: Generate New Launches by Area Graph
def generate_new_launches_graph():
    new_launches = filtered_data.groupby([filtered_data['Launch Date'].dt.to_period('Q'), 'Area']).size().unstack(fill_value=0)
    fig = go.Figure()
    for area in new_launches.columns:
        fig.add_trace(go.Scatter(x=new_launches.index.astype(str), y=new_launches[area], mode='lines+markers', name=area))
    fig.update_layout(title="New Launches by Area Over Time", xaxis_title="Time", yaxis_title="Projects")
    return dcc.Graph(figure=fig)

# Helper Function: Generate Total Project Size Graph
def generate_total_project_size_graph():
    project_size_trend = filtered_data.groupby(filtered_data['Launch Date'].dt.to_period('Q'))['Project Area (Acres)'].sum()
    fig = go.Figure(go.Scatter(x=project_size_trend.index.astype(str), y=project_size_trend.values, mode='lines+markers'))
    fig.update_layout(title="Total Project Size Over Time", xaxis_title="Quarter", yaxis_title="Total Size (Acres)")
    return dcc.Graph(figure=fig)

# Helper Function: Generate Asset Type Distribution Graph
def generate_asset_type_distribution_graph():
    asset_type_trend = filtered_data.groupby([filtered_data['Launch Date'].dt.to_period('Q'), 'Asset Type']).size().unstack(fill_value=0)
    fig = go.Figure()
    for asset_type in asset_type_trend.columns:
        fig.add_trace(go.Scatter(x=asset_type_trend.index.astype(str), y=asset_type_trend[asset_type], mode='lines+markers', name=f'{asset_type} Projects'))
    fig.update_layout(title="Asset Type Distribution Over Time", xaxis_title="Quarter", yaxis_title="Projects")
    return dcc.Graph(figure=fig)

# Helper Function: Generate Projects Area Cumulative Graph
def generate_projects_area_cumulative_graph():
    projects_trend = filtered_data.groupby([filtered_data['Launch Date'].dt.to_period('Q'), 'Area']).size().unstack().cumsum()
    fig = go.Figure()
    for area in projects_trend.columns:
        fig.add_trace(go.Scatter(x=projects_trend.index.astype(str), y=projects_trend[area], mode='lines+markers', name=f'Projects in {area}'))
    fig.update_layout(title="Number of Projects by Area Over Time (Cumulative)", xaxis_title="Quarter", yaxis_title="Cumulative Projects")
    return dcc.Graph(figure=fig)

# Helper Function: Generate Developer Unit Volume Graph
def generate_developer_unit_volume_graph():
    dev_unit_counts = filtered_data.groupby('Developer Name')['Total no. of units'].sum().sort_values(ascending=False).head(20)
    fig = px.bar(
        x=dev_unit_counts.index,
        y=dev_unit_counts.values,
        title="Developer Dominance in Unit Volume (Top 20 Developers)",
        labels={'x': 'Developer', 'y': 'Total Units'}
    )
    fig.update_layout(
        xaxis_tickangle=-45,
        xaxis_title="Developer",
        yaxis_title="Total Units",
        showlegend=False
    )
    return dcc.Graph(figure=fig)

# Helper Function: Generate Famous Developer Quarterly Launches Graph
def generate_famous_developer_quarterly_launches_graph():
    famous_developers = ['Prestige', 'Brigade', 'Sobha', 'Assetz', 'Birla', 'Mahindra', 'Adarsh', 'Puravankara', 'Raheja']
    famous_data = filtered_data[filtered_data['Developer Name'].isin(famous_developers)]
    if not famous_data.empty:
        famous_data['Launch Quarter'] = famous_data['Launch Date'].dt.to_period('Q')
        quarterly_launches = famous_data.groupby(['Launch Quarter', 'Developer Name']).size().unstack(fill_value=0)
        fig = go.Figure()
        for developer in famous_developers:
            if developer in quarterly_launches.columns:
                fig.add_trace(go.Bar(
                    x=quarterly_launches.index.astype(str),
                    y=quarterly_launches[developer],
                    name=developer
                ))
        fig.update_layout(
            title="Famous Developer Quarterly Project Launches",
            xaxis_title="Quarter",
            yaxis_title="Number of Projects Launched",
            barmode="stack",
            template="plotly_white",
            legend_title_text="Developers"
        )
        return dcc.Graph(figure=fig)
    else:
        fig = go.Figure().add_annotation(
            text="No data available for Famous Developers",
            xref="paper", yref="paper", showarrow=False
        )
        return dcc.Graph(figure=fig)

# Helper Function: Generate Handover Time Developer Graph
def generate_handover_time_developer_graph():
    handover_median = filtered_data.groupby(['Developer Name', 'Asset Type'])['Handover Time (Months)'].median().unstack(fill_value=0)
    fig = go.Figure()
    for asset_type in handover_median.columns:
        fig.add_trace(go.Bar(x=handover_median.index, y=handover_median[asset_type], name=asset_type))
    fig.update_layout(title="Time to Handover by Developer and Asset Type (Median)", xaxis_title="Developer", yaxis_title="Median Handover Time (Months)")
    return dcc.Graph(figure=fig)

# Helper Function: Generate Total Units by Area Graph
def generate_total_units_area_graph():
    units_by_area = filtered_data.groupby([filtered_data['Launch Date'].dt.to_period('Q'), 'Area'])['Total no. of units'].sum().unstack(fill_value=0)
    fig = go.Figure()
    for area in units_by_area.columns:
        fig.add_trace(go.Scatter(x=units_by_area.index.astype(str), y=units_by_area[area], mode='lines+markers', name=area))
    fig.update_layout(title="Total Number of Units by Area Over Time", xaxis_title="Quarter", yaxis_title="Total Units")
    return dcc.Graph(figure=fig)

# Helper Function: Generate Developer Dominance Graph
def generate_developer_dominance_graph(asset_type):
    dev_data = filtered_data[filtered_data['Asset Type'] == asset_type]
   
       
    if not dev_data.empty:
        dev_counts = dev_data.groupby('Developer Name')['Total no. of units'].sum().sort_values(ascending=False).head(20)
        fig = px.bar(
            x=dev_counts.index,
            y=dev_counts.values,
            title=f"Developer Dominance (Total Units) - {asset_type}",
            labels={'x': 'Developer', 'y': 'Total Units'}
        )
        fig.update_layout(
            xaxis_tickangle=-45,
            xaxis_title="Developer",
            yaxis_title="Total Units",
            showlegend=False
        )
        return dcc.Graph(figure=fig)
    else:
        return html.Div(f"No data available for Developer Dominance - {asset_type}")

# Helper Function: Generate Configuration by Area Graph
def generate_configuration_by_area_graph(asset_type):
    config_data = filtered_data[filtered_data['Asset Type'] == asset_type]
    
    if not config_data.empty:
        config_by_area = config_data.groupby(['Area', 'BHK']).size().unstack(fill_value=0)
        fig = go.Figure()
        for bhk in config_by_area.columns:
            fig.add_trace(go.Bar(
                x=config_by_area.index,
                y=config_by_area[bhk],
                name=f"{bhk} BHK"
            ))
        fig.update_layout(
            title=f"{asset_type} Configuration by Area",
            xaxis_title="Area",
            yaxis_title="Total Units",
            barmode="stack",
            template="plotly_white",
            legend_title="Configuration (BHK)"
        )
        return dcc.Graph(figure=fig)
    else:
        return html.Div(f"No data available for {asset_type} Configuration by Area")

# Helper Function: Generate Asset Type Projects Graph
def generate_asset_type_projects_graph(area):
    area_data = filtered_data[filtered_data['Area'] == area]
    
    if not area_data.empty:
        asset_type_projects = area_data.groupby([area_data['Launch Date'].dt.to_period('Q'), 'Asset Type']).size().unstack(fill_value=0)
        fig = go.Figure()
        for asset_type in asset_type_projects.columns:
            fig.add_trace(go.Scatter(x=asset_type_projects.index.astype(str), y=asset_type_projects[asset_type], mode='lines+markers', name=asset_type))
        fig.update_layout(
            title=f"Asset Type Distribution Over Time (Total Projects) - {area}",
            xaxis_title="Quarter",
            yaxis_title="Total Projects",
            template="plotly_white"
        )
        return dcc.Graph(figure=fig)
    else:
        return html.Div(f"No data available for {area} - Asset Type Projects Over Time")

# Helper Function: Generate Asset Type Units Graph
def generate_asset_type_units_graph(area):
    area_data = filtered_data[filtered_data['Area'] == area]
    if not area_data.empty:
        asset_type_units = area_data.groupby([area_data['Launch Date'].dt.to_period('Q'), 'Asset Type'])['Total no. of units'].sum().unstack(fill_value=0)
        fig = go.Figure()
        for asset_type in asset_type_units.columns:
            fig.add_trace(go.Scatter(x=asset_type_units.index.astype(str), y=asset_type_units[asset_type], mode='lines+markers', name=asset_type))
        fig.update_layout(
            title=f"Asset Type Distribution Over Time (Total Units) - {area}",
            xaxis_title="Quarter",
            yaxis_title="Total Units",
            template="plotly_white"
        )
        return dcc.Graph(figure=fig)
    else:
        return html.Div(f"No data available for {area} - Asset Type Units Over Time")

# Run the app
# Run the app
if __name__ == "__main__":
    app.run_server(host='0.0.0.0', port=10000, debug=True)