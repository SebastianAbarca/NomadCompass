import plotly.express as px
import plotly.graph_objects as go # Correct import for graph_objects
import pandas as pd
import numpy as np

# Corrected type hint: go.Figure instead of px.graph_objects.Figure
def plot_nha_line_chart(df: pd.DataFrame, indicator_name: str) -> go.Figure:
    """
    Generates a line chart showing the trend of a health indicator for selected countries.

    Args:
        df (pd.DataFrame): Filtered DataFrame containing 'Year', 'Value', and 'Countries'.
        indicator_name (str): The name of the indicator being plotted.

    Returns:
        go.Figure: A Plotly Express line chart figure.
    """
    fig = px.line(
        df,
        x='Year',
        y='Value',
        color='Countries',
        title=f'{indicator_name} Trend for Selected Countries',
        labels={'Value': indicator_name, 'Year': 'Year'},
        markers=True
    )
    return fig

# Corrected type hint
def plot_nha_animated_scatter(df: pd.DataFrame, x_indicator: str, y_indicator: str) -> go.Figure:
    """
    Generates an animated scatter plot showing the relationship between two health indicators over time.

    Args:
        df (pd.DataFrame): Merged and sorted DataFrame with 'Year', 'Countries', 'X_Value', 'Y_Value'.
        x_indicator (str): The name of the indicator on the X-axis.
        y_indicator (str): The name of the indicator on the Y-axis.

    Returns:
        go.Figure: A Plotly Express animated scatter plot figure.
    """
    fig = px.scatter(
        df,
        x='X_Value',
        y='Y_Value',
        animation_frame='Year',
        animation_group='Countries',
        color='Countries',
        size='X_Value', # Size points by X-axis value
        hover_name='Countries',
        color_discrete_sequence=px.colors.qualitative.Plotly,
        title=f'Relationship between {x_indicator} and {y_indicator} over Time',
        labels={'X_Value': x_indicator, 'Y_Value': y_indicator},
        range_x=[df['X_Value'].min() * 0.9, df['X_Value'].max() * 1.1],
        range_y=[df['Y_Value'].min() * 0.9, df['Y_Value'].max() * 1.1]
    )

    fig.layout.updatemenus[0].buttons[0].args[1]['frame']['duration'] = 1000
    fig.layout.updatemenus[0].buttons[0].args[1]['transition']['duration'] = 500
    fig.update_traces(
        mode='lines+markers',
        line=dict(width=2),
        marker=dict(size=8)
    )
    fig.layout.updatemenus[0].buttons[0].args[1]["frame"]["redraw"] = True
    return fig

# Corrected type hint
def plot_nha_bar_chart(df: pd.DataFrame, indicator_name: str, year: int) -> go.Figure:
    """
    Generates a bar chart showing a health indicator by country for a specific year.

    Args:
        df (pd.DataFrame): Filtered DataFrame containing 'Countries', 'Value'.
        indicator_name (str): The name of the indicator being plotted.
        year (int): The year for which data is plotted.

    Returns:
        go.Figure: A Plotly Express bar chart figure.
    """
    fig = px.bar(
        df,
        x='Countries',
        y='Value',
        title=f'{indicator_name} by Country in {year}',
        labels={'Value': indicator_name, 'Countries': 'Country'}
    )
    return fig

# Corrected type hint
def plot_nha_stacked_bar_chart(df: pd.DataFrame, country_name: str) -> go.Figure:
    """
    Generates a stacked bar chart showing the breakdown of health expenditure for a country over time.

    Args:
        df (pd.DataFrame): Filtered DataFrame containing 'Year', 'Value', and 'Indicators'.
        country_name (str): The name of the country being plotted.

    Returns:
        go.Figure: A Plotly Express stacked bar chart figure.
    """
    fig = px.bar(
        df,
        x='Year',
        y='Value',
        color='Indicators', # Color by Indicator to stack them
        title=f'Health Expenditure Breakdown for {country_name} Over Time',
        labels={'Value': 'Indicator Value', 'Year': 'Year', 'Indicators': 'Indicator'},
        hover_data={'Value': ':.2f'}
    )
    fig.update_layout(barmode='stack') # Explicitly ensure stacking
    return fig

def plot_nha_top_bottom_bar_chart(df: pd.DataFrame, indicator_name: str, year: int, chart_type: str) -> go.Figure:
    """
    Generates a bar chart showing the Top/Bottom N countries for a given indicator and year.

    Args:
        df (pd.DataFrame): Filtered and sorted DataFrame containing 'Countries' and 'Value'.
        indicator_name (str): The name of the indicator being plotted.
        year (int): The year for which data is plotted.
        chart_type (str): "Top" or "Bottom" indicating whether top or bottom countries are shown.

    Returns:
        go.Figure: A Plotly Express bar chart figure.
    """
    title_suffix = "highest" if chart_type == "Top" else "lowest"
    fig = px.bar(
        df,
        x='Countries',
        y='Value',
        title=f'{chart_type} Countries with the {title_suffix} {indicator_name} in {year}',
        labels={'Value': indicator_name, 'Countries': 'Country'},
        color='Value', # Color by value to show intensity
        color_continuous_scale=px.colors.sequential.Plasma if chart_type == "Top" else px.colors.sequential.Viridis_r # Different scales for top/bottom
    )
    fig.update_layout(xaxis={'categoryorder':'total ascending' if chart_type == "Bottom" else 'total descending'})
    return fig
