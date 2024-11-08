import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.graph_objects as go
import plotly.express as px
import re

# Load and clean data
data = pd.read_excel(r"./data/TruEstimate Final Sheet Project (3).xlsx", header=1)
data['Launch Date'] = pd.to_datetime(data['Launch Date'], errors='coerce')
data['Handover date'] = pd.to_datetime(data['Handover date'], errors='coerce')
data['Developer Name'] = data['Developer Name'].str.strip()
data['Area'] = data['Area'].str.title()
filtered_data = data[(data['Launch Date'] > '2022-10-01') & data['Area'].notna() & data['Total no. of units'].notna()]
filtered_data['Handover Time (Months)'] = (filtered_data['Handover date'] - filtered_data['Launch Date']).dt.days // 30
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

    # Create a new BHK column with cleaned numeric values
    df.loc[:, 'BHK'] = df['BHK'].apply(extract_first_number)

    # Drop rows where BHK is None (invalid or missing entries)
    df = df.dropna(subset=['BHK']).copy()

    # Ensure all 'BHK' values are float type
    df.loc[:, 'BHK'] = df['BHK'].astype(float)

    return df

# Apply the cleaning function to your dataset
filtered_data = clean_bhk_column(filtered_data)
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
    # Asset Type by Area (Projects) - North, East, South, and West
    {'label': 'Asset Type by Area Over Time (Projects) - North', 'value': 'asset_type_north_projects'},
    {'label': 'Asset Type by Area Over Time (Projects) - East', 'value': 'asset_type_east_projects'},
    {'label': 'Asset Type by Area Over Time (Projects) - South', 'value': 'asset_type_south_projects'},
    {'label': 'Asset Type by Area Over Time (Projects) - West', 'value': 'asset_type_west_projects'},
    # Developer Dominance by Asset Type
    {'label': 'Developer Dominance (Total Units) - Apartment', 'value': 'developer_dominance_apartment'},
    {'label': 'Developer Dominance (Total Units) - Plot', 'value': 'developer_dominance_plot'},
    {'label': 'Famous Developer Quarterly Project Launches', 'value': 'famous_dev_quarterly_launches'},
    {'label': 'Developer Dominance (Total Units) - Villa', 'value': 'developer_dominance_villa'},
    # Apartment Configuration by Area
    {'label': 'Apartment Configuration by Area Over Time - North', 'value': 'config_north_apartment'},
    {'label': 'Apartment Configuration by Area Over Time - East', 'value': 'config_east_apartment'},
    {'label': 'Apartment Configuration by Area Over Time - South', 'value': 'config_south_apartment'},
    {'label': 'Apartment Configuration by Area Over Time - West', 'value': 'config_west_apartment'},
      # Configuration by Area for Apartments, Villas, and Plots
    {'label': 'Configuration by Area - Apartment', 'value': 'config_by_area_apartment'},
    {'label': 'Configuration by Area - Villa', 'value': 'config_by_area_villa'},
    {'label': 'Configuration by Area - Plot', 'value': 'config_by_area_plot'},
    
    # Handover by Area Over Time for Apartments, Villas, and Plots
    {'label': 'Handover by Area Over Time - Apartment', 'value': 'handover_by_area_apartment'},
    {'label': 'Handover by Area Over Time - Villa', 'value': 'handover_by_area_villa'},
    {'label': 'Handover by Area Over Time - Plot', 'value': 'handover_by_area_plot'},
]

# Layout
app.layout = html.Div([
    html.H1("TruEstate Bangalore Real Estate Market Dashboard"),
    dcc.Dropdown(id='graph-selector', options=graph_options, value='handover_area', multi=False),
    html.Div(id='graph-container')
])

# Callback function
@app.callback(
    Output('graph-container', 'children'),
    [Input('graph-selector', 'value')]
)
def update_graph(selected_graph):
    # Handover by Area Over Time
    if selected_graph == 'handover_area':
        handover_by_area = filtered_data.groupby([filtered_data['Handover date'].dt.to_period('Q'), 'Area']).size().unstack()
        fig = go.Figure()
        for area in handover_by_area.columns:
            fig.add_trace(go.Scatter(x=handover_by_area.index.astype(str), y=handover_by_area[area], mode='lines+markers', name=area))
        fig.update_layout(title="Handover by Area Over Time", xaxis_title="Time", yaxis_title="Projects")
        return dcc.Graph(figure=fig)

    # New Launches by Area Over Time
    elif selected_graph == 'new_launches_area':
        new_launches = filtered_data.groupby([filtered_data['Launch Date'].dt.to_period('Q'), 'Area']).size().unstack()
        fig = go.Figure()
        for area in new_launches.columns:
            fig.add_trace(go.Scatter(x=new_launches.index.astype(str), y=new_launches[area], mode='lines+markers', name=area))
        fig.update_layout(title="New Launches by Area Over Time", xaxis_title="Time", yaxis_title="Projects")
        return dcc.Graph(figure=fig)

    # Total Project Size Over Time
    elif selected_graph == 'total_project_size':
        project_size_trend = filtered_data.groupby(filtered_data['Launch Date'].dt.to_period('Q'))['Project Area (Acres)'].sum()
        fig = go.Figure(go.Scatter(x=project_size_trend.index.astype(str), y=project_size_trend.values, mode='lines+markers'))
        fig.update_layout(title="Total Project Size Over Time", xaxis_title="Quarter", yaxis_title="Total Size (Acres)")
        return dcc.Graph(figure=fig)

    # Asset Type Distribution Over Time
    elif selected_graph == 'asset_type_distribution':
        asset_type_trend = filtered_data.groupby([filtered_data['Launch Date'].dt.to_period('Q'), 'Asset Type']).size().unstack()
        fig = go.Figure()
        for asset_type in asset_type_trend.columns:
            fig.add_trace(go.Scatter(x=asset_type_trend.index.astype(str), y=asset_type_trend[asset_type], mode='lines+markers', name=f'{asset_type} Projects'))
        fig.update_layout(title="Asset Type Distribution Over Time", xaxis_title="Quarter", yaxis_title="Projects")
        return dcc.Graph(figure=fig)

    # Number of Projects by Area Over Time (Cumulative)
    elif selected_graph == 'projects_area_cumulative':
        projects_trend = filtered_data.groupby([filtered_data['Launch Date'].dt.to_period('Q'), 'Area']).size().unstack().cumsum()
        fig = go.Figure()
        for area in projects_trend.columns:
            fig.add_trace(go.Scatter(x=projects_trend.index.astype(str), y=projects_trend[area], mode='lines+markers', name=f'Projects in {area}'))
        fig.update_layout(title="Number of Projects by Area Over Time (Cumulative)", xaxis_title="Quarter", yaxis_title="Cumulative Projects")
        return dcc.Graph(figure=fig)

    # Developer Dominance in Unit Volume (Vertical Bar Chart with Top Developers)
    elif selected_graph == 'developer_unit_volume':
        dev_unit_counts = filtered_data.groupby('Developer Name')['Total no. of units'].sum().sort_values(ascending=False).head(20)
        fig = px.bar(
            x=dev_unit_counts.index,
            y=dev_unit_counts.values,
            title="Developer Dominance in Unit Volume (Top 20 Developers)",
            labels={'x': 'Developer', 'y': 'Total Units'}
        )
        fig.update_layout(
            xaxis_tickangle=-45,  # Tilt x-axis labels for readability
            xaxis_title="Developer",
            yaxis_title="Total Units",
            showlegend=False
        )
        return dcc.Graph(figure=fig)
    
    if selected_graph == 'famous_dev_quarterly_launches':
        # List of famous developers
        famous_developers = ['Prestige', 'Brigade', 'Sobha', 'Assetz', 'Birla', 'Mahindra', 'Adarsh', 'Puravankara', 'Raheja']
        
        # Filter the data for these famous developers
        famous_data = filtered_data[filtered_data['Developer Name'].isin(famous_developers)]
        
        # Check if data is available
        if not famous_data.empty:
            # Group by quarter and developer, counting launches
            famous_data['Launch Quarter'] = famous_data['Launch Date'].dt.to_period('Q')
            quarterly_launches = famous_data.groupby(['Launch Quarter', 'Developer Name']).size().unstack(fill_value=0)
            
            # Plot
            fig = go.Figure()
            for developer in famous_developers:
                if developer in quarterly_launches.columns:
                    fig.add_trace(go.Bar(
                        x=quarterly_launches.index.astype(str),
                        y=quarterly_launches[developer],
                        name=developer
                    ))
            
            # Customize layout with labels
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
            # If no data is available, display a message
            fig = go.Figure().add_annotation(
                text="No data available for Famous Developers",
                xref="paper", yref="paper", showarrow=False
            )
            return dcc.Graph(figure=fig)
        
    # Time to Handover by Developer and Asset Type (Median)
    elif selected_graph == 'handover_time_developer':
        handover_median = filtered_data.groupby(['Developer Name', 'Asset Type'])['Handover Time (Months)'].median().unstack()
        fig = go.Figure()
        for asset_type in handover_median.columns:
            fig.add_trace(go.Bar(x=handover_median.index, y=handover_median[asset_type], name=asset_type))
        fig.update_layout(title="Time to Handover by Developer and Asset Type (Median)", xaxis_title="Developer", yaxis_title="Median Handover Time (Months)")
        return dcc.Graph(figure=fig)

    # Total Number of Units by Area Over Time
    elif selected_graph == 'total_units_area':
        units_by_area = filtered_data.groupby([filtered_data['Launch Date'].dt.to_period('Q'), 'Area'])['Total no. of units'].sum().unstack()
        fig = go.Figure()
        for area in units_by_area.columns:
            fig.add_trace(go.Scatter(x=units_by_area.index.astype(str), y=units_by_area[area], mode='lines+markers', name=area))
        fig.update_layout(title="Total Number of Units by Area Over Time", xaxis_title="Quarter", yaxis_title="Total Units")
        return dcc.Graph(figure=fig)
        # Asset Type by Area Over Time (Projects) - North
    elif selected_graph == 'asset_type_north_projects':
        north_data = filtered_data[filtered_data['Area'] == 'North']
        asset_type_north_projects = north_data.groupby([north_data['Launch Date'].dt.to_period('Q'), 'Asset Type']).size().unstack()
        fig = go.Figure()
        for asset_type in asset_type_north_projects.columns:
            fig.add_trace(go.Scatter(x=asset_type_north_projects.index.astype(str), y=asset_type_north_projects[asset_type], mode='lines+markers', name=asset_type))
        fig.update_layout(title="Asset Type by Area Over Time (Projects) - North", xaxis_title="Quarter", yaxis_title="Total Projects")
        return dcc.Graph(figure=fig)

    # Asset Type by Area Over Time (Projects) - East
    elif selected_graph == 'asset_type_east_projects':
        east_data = filtered_data[filtered_data['Area'] == 'East']
        asset_type_east_projects = east_data.groupby([east_data['Launch Date'].dt.to_period('Q'), 'Asset Type']).size().unstack()
        fig = go.Figure()
        for asset_type in asset_type_east_projects.columns:
            fig.add_trace(go.Scatter(x=asset_type_east_projects.index.astype(str), y=asset_type_east_projects[asset_type], mode='lines+markers', name=asset_type))
        fig.update_layout(title="Asset Type by Area Over Time (Projects) - East", xaxis_title="Quarter", yaxis_title="Total Projects")
        return dcc.Graph(figure=fig)

    # Asset Type by Area Over Time (Projects) - South
    elif selected_graph == 'asset_type_south_projects':
        south_data = filtered_data[filtered_data['Area'] == 'South']
        asset_type_south_projects = south_data.groupby([south_data['Launch Date'].dt.to_period('Q'), 'Asset Type']).size().unstack()
        fig = go.Figure()
        for asset_type in asset_type_south_projects.columns:
            fig.add_trace(go.Scatter(x=asset_type_south_projects.index.astype(str), y=asset_type_south_projects[asset_type], mode='lines+markers', name=asset_type))
        fig.update_layout(title="Asset Type by Area Over Time (Projects) - South", xaxis_title="Quarter", yaxis_title="Total Projects")
        return dcc.Graph(figure=fig)

    # Asset Type by Area Over Time (Projects) - West
    elif selected_graph == 'asset_type_west_projects':
        west_data = filtered_data[filtered_data['Area'] == 'West']
        asset_type_west_projects = west_data.groupby([west_data['Launch Date'].dt.to_period('Q'), 'Asset Type']).size().unstack()
        fig = go.Figure()
        for asset_type in asset_type_west_projects.columns:
            fig.add_trace(go.Scatter(x=asset_type_west_projects.index.astype(str), y=asset_type_west_projects[asset_type], mode='lines+markers', name=asset_type))
        fig.update_layout(title="Asset Type by Area Over Time (Projects) - West", xaxis_title="Quarter", yaxis_title="Total Projects")
        return dcc.Graph(figure=fig)

 
    if selected_graph == 'developer_dominance_apartment':
        # Developer Dominance - Apartment in North, East, South, and West with Data Checks
        area_data = {}
        for area in ['North', 'East', 'South', 'West']:
            area_apartment_data = filtered_data[(filtered_data['Area'] == area) & (filtered_data['Asset Type'] == 'Apartment')]
            if not area_apartment_data.empty:
                dev_area_apartment_units = area_apartment_data.groupby('Developer Name')['Total no. of units'].sum().sort_values(ascending=False).head(20)
                fig = px.bar(
                    x=dev_area_apartment_units.index,
                    y=dev_area_apartment_units.values,
                    title=f"Developer Dominance (Total Units) - Apartment in {area} (Top 20 Developers)",
                    labels={'x': 'Developer', 'y': 'Total Units'}
                )
                fig.update_layout(xaxis_tickangle=-45, xaxis_title="Developer", yaxis_title="Total Units", showlegend=False, template="plotly_white")
                area_data[area] = dcc.Graph(figure=fig)
            else:
                fig = go.Figure().add_annotation(text=f"No data available for Apartment in {area}", xref="paper", yref="paper", showarrow=False)
                area_data[area] = dcc.Graph(figure=fig)

        return html.Div([area_data['North'], area_data['East'], area_data['South'], area_data['West']])

    elif selected_graph == 'developer_dominance_villa':
        # Developer Dominance - Villa in North, East, South, and West with Data Checks
        area_data = {}
        for area in ['North', 'East', 'South', 'West']:
            area_villa_data = filtered_data[(filtered_data['Area'] == area) & (filtered_data['Asset Type'] == 'Villa')]
            if not area_villa_data.empty:
                dev_area_villa_units = area_villa_data.groupby('Developer Name')['Total no. of units'].sum().sort_values(ascending=False).head(20)
                fig = px.bar(
                    x=dev_area_villa_units.index,
                    y=dev_area_villa_units.values,
                    title=f"Developer Dominance (Total Units) - Villa in {area} (Top 20 Developers)",
                    labels={'x': 'Developer', 'y': 'Total Units'}
                )
                fig.update_layout(xaxis_tickangle=-45, xaxis_title="Developer", yaxis_title="Total Units", showlegend=False, template="plotly_white")
                area_data[area] = dcc.Graph(figure=fig)
            else:
                fig = go.Figure().add_annotation(text=f"No data available for Villa in {area}", xref="paper", yref="paper", showarrow=False)
                area_data[area] = dcc.Graph(figure=fig)

        return html.Div([area_data['North'], area_data['East'], area_data['South'], area_data['West']])

    elif selected_graph == 'developer_dominance_plot':
        # Developer Dominance - Plot in North, East, South, and West with Data Checks
        area_data = {}
        for area in ['North', 'East', 'South', 'West']:
            area_plot_data = filtered_data[(filtered_data['Area'] == area) & (filtered_data['Asset Type'] == 'Plot')]
            if not area_plot_data.empty:
                dev_area_plot_units = area_plot_data.groupby('Developer Name')['Total no. of units'].sum().sort_values(ascending=False).head(20)
                fig = px.bar(
                    x=dev_area_plot_units.index,
                    y=dev_area_plot_units.values,
                    title=f"Developer Dominance (Total Units) - Plot in {area} (Top 20 Developers)",
                    labels={'x': 'Developer', 'y': 'Total Units'}
                )
                fig.update_layout(xaxis_tickangle=-45, xaxis_title="Developer", yaxis_title="Total Units", showlegend=False, template="plotly_white")
                area_data[area] = dcc.Graph(figure=fig)
            else:
                fig = go.Figure().add_annotation(text=f"No data available for Plot in {area}", xref="paper", yref="paper", showarrow=False)
                area_data[area] = dcc.Graph(figure=fig)

        return html.Div([area_data['North'], area_data['East'], area_data['South'], area_data['West']])
   
    # Apartment Configuration by Area Over Time - North
    if selected_graph == 'config_north_apartment':
        north_apartment_data = filtered_data[(filtered_data['Area'] == 'North') & (filtered_data['Asset Type'] == 'Apartment')]
        if not north_apartment_data.empty:
            config_north_apartment = north_apartment_data.groupby([north_apartment_data['Launch Date'].dt.to_period('Q'), 'BHK']).size().unstack()
            fig = go.Figure()
            for bhk in config_north_apartment.columns:
                fig.add_trace(go.Scatter(x=config_north_apartment.index.astype(str), y=config_north_apartment[bhk], mode='lines+markers', name=f"{bhk} BHK"))
            fig.update_layout(title="Apartment Configuration by Area Over Time - North", xaxis_title="Quarter", yaxis_title="Total Units", template="plotly_white")
            return dcc.Graph(figure=fig)
        else:
            return html.Div("No data available for North - Apartment Configuration")

    # Apartment Configuration by Area Over Time - East
    elif selected_graph == 'config_east_apartment':
        east_apartment_data = filtered_data[(filtered_data['Area'] == 'East') & (filtered_data['Asset Type'] == 'Apartment')]
        if not east_apartment_data.empty:
            config_east_apartment = east_apartment_data.groupby([east_apartment_data['Launch Date'].dt.to_period('Q'), 'BHK']).size().unstack()
            fig = go.Figure()
            for bhk in config_east_apartment.columns:
                fig.add_trace(go.Scatter(x=config_east_apartment.index.astype(str), y=config_east_apartment[bhk], mode='lines+markers', name=f"{bhk} BHK"))
            fig.update_layout(title="Apartment Configuration by Area Over Time - East", xaxis_title="Quarter", yaxis_title="Total Units", template="plotly_white")
            return dcc.Graph(figure=fig)
        else:
            return html.Div("No data available for East - Apartment Configuration")

    # Apartment Configuration by Area Over Time - South
    elif selected_graph == 'config_south_apartment':
        south_apartment_data = filtered_data[(filtered_data['Area'] == 'South') & (filtered_data['Asset Type'] == 'Apartment')]
        if not south_apartment_data.empty:
            config_south_apartment = south_apartment_data.groupby([south_apartment_data['Launch Date'].dt.to_period('Q'), 'BHK']).size().unstack()
            fig = go.Figure()
            for bhk in config_south_apartment.columns:
                fig.add_trace(go.Scatter(x=config_south_apartment.index.astype(str), y=config_south_apartment[bhk], mode='lines+markers', name=f"{bhk} BHK"))
            fig.update_layout(title="Apartment Configuration by Area Over Time - South", xaxis_title="Quarter", yaxis_title="Total Units", template="plotly_white")
            return dcc.Graph(figure=fig)
        else:
            return html.Div("No data available for South - Apartment Configuration")

    # Apartment Configuration by Area Over Time - West
    elif selected_graph == 'config_west_apartment':
        west_apartment_data = filtered_data[(filtered_data['Area'] == 'West') & (filtered_data['Asset Type'] == 'Apartment')]
        if not west_apartment_data.empty:
            config_west_apartment = west_apartment_data.groupby([west_apartment_data['Launch Date'].dt.to_period('Q'), 'BHK']).size().unstack()
            fig = go.Figure()
            for bhk in config_west_apartment.columns:
                fig.add_trace(go.Scatter(x=config_west_apartment.index.astype(str), y=config_west_apartment[bhk], mode='lines+markers', name=f"{bhk} BHK"))
            fig.update_layout(title="Apartment Configuration by Area Over Time - West", xaxis_title="Quarter", yaxis_title="Total Units", template="plotly_white")
            return dcc.Graph(figure=fig)
        else:
            return html.Div("No data available for West - Apartment Configuration")
        
    if selected_graph == 'config_by_area_apartment':
        return generate_configuration_by_area_graph(asset_type='Apartment')
    elif selected_graph == 'config_by_area_villa':
        return generate_configuration_by_area_graph(asset_type='Villa')
    elif selected_graph == 'config_by_area_plot':
        return generate_configuration_by_area_graph(asset_type='Plot')

    # Handover by Area Over Time - Apartment, Villa, Plot
    elif selected_graph == 'handover_by_area_apartment':
        return generate_handover_by_area_graph(asset_type='Apartment')
    elif selected_graph == 'handover_by_area_villa':
        return generate_handover_by_area_graph(asset_type='Villa')
    elif selected_graph == 'handover_by_area_plot':
        return generate_handover_by_area_graph(asset_type='Plot')


def update_graph(selected_graph):
    if selected_graph == 'config_by_area_apartment':
        return generate_configuration_by_area_graph(asset_type='Apartment')
    elif selected_graph == 'config_by_area_villa':
        return generate_configuration_by_area_graph(asset_type='Villa')
    elif selected_graph == 'config_by_area_plot':
        return generate_configuration_by_area_graph(asset_type='Plot')

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
    # Debugging: Check the data types and unique values in filtered_data
print("Unique BHK values after cleaning:")
print(filtered_data['BHK'].unique())


# Check for any non-numeric values in BHK after cleaning
print("Unique BHK values after cleaning:")
print(filtered_data['BHK'].unique())

# Display any non-numeric rows if still present (should be empty)
non_numeric_bhk = filtered_data[~filtered_data['BHK'].apply(lambda x: isinstance(x, (int, float)))]
print("\nRows with non-numeric BHK values after cleaning (should be empty):")
print(non_numeric_bhk)


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

# Helper Function: Generate Handover by Area Graph
def generate_handover_by_area_graph(asset_type):
    handover_data = filtered_data[(filtered_data['Asset Type'] == asset_type) & filtered_data['Handover date'].notna()]
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
            title=f"{asset_type} Handover by Area Over Time",
            xaxis_title="Quarter",
            yaxis_title="Number of Projects Handover",
            template="plotly_white",
            legend_title="Area"
        )
        return dcc.Graph(figure=fig)
    else:
        return html.Div(f"No data available for {asset_type} Handover by Area")

if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=10000, debug=True)
