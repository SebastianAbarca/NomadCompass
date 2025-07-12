import pandas as pd
import plotly.express as px
import streamlit as st
import numpy as np


def plot_population_trend(df: pd.DataFrame, selected_countries: list, exclusion_text: str):
    """
    Generates a line plot for population trends over years for selected countries.

    Args:
        df (pd.DataFrame): The filtered DataFrame containing population data.
        selected_countries (list): A list of countries to display.
        exclusion_text (str): Text indicating any globally excluded countries.
    """
    if selected_countries:
        df_plot = df[df['Country/Territory'].isin(selected_countries)].sort_values(by='Year')
        if not df_plot.empty:
            fig = px.line(
                df_plot,
                x='Year',
                y='Population',
                color='Country/Territory',
                title=f'Population Over Time for Selected Countries{exclusion_text}',
                labels={'Population': 'Population', 'Year': 'Year'},
                hover_data={'Population': ':,', 'Year': True}
            )
            fig.update_layout(hovermode="x unified")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available for the selected countries and years.")
    else:
        st.info("Please select at least one country to view population trends.")


def plot_top_n_population(df: pd.DataFrame, selected_year: int, top_n: int, exclusion_text: str):
    """
    Generates a bar chart for the top N countries by population for a specific year.

    Args:
        df (pd.DataFrame): The filtered DataFrame containing population data.
        selected_year (int): The year to display data for.
        top_n (int): The number of top countries to display.
        exclusion_text (str): Text indicating any globally excluded countries.
    """
    df_selected_year = df[df['Year'] == selected_year].sort_values(by='Population', ascending=False)
    if top_n == 0:
        st.info("Please select a number greater than 0 for top countries.")
    elif not df_selected_year.empty:
        fig = px.bar(
            df_selected_year.head(top_n),
            x='Country/Territory',
            y='Population',
            color='Population',
            title=f'Top {top_n} Countries by Population in {int(selected_year)}{exclusion_text}',
            labels={'Population': 'Population', 'Country/Territory': 'Country'},
            hover_data={'Population': ':,', 'Area (km²)': ':,', 'Density (per km²)': ':.2f'}
        )
        fig.update_layout(xaxis={'categoryorder': 'total descending'})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info(f"No population data found for the year {int(selected_year)} after filters.")


def plot_density_vs_area(df: pd.DataFrame, selected_year: int, exclusion_text: str, remove_outliers: bool = False,
                         n_outliers_to_remove: int = 5):
    """
    Generates a scatter plot for population density vs. area.

    Args:
        df (pd.DataFrame): The filtered DataFrame containing population data.
        selected_year (int): The year to display data for.
        exclusion_text (str): Text indicating any globally excluded countries.
        remove_outliers (bool): If True, removes the top N density outliers.
        n_outliers_to_remove (int): The number of top density outliers to remove if remove_outliers is True.
    """
    df_plot = df[df['Year'] == selected_year].copy()
    df_plot.dropna(subset=['Area (km²)', 'Density (per km²)', 'Population'], inplace=True)

    title_suffix = ""
    if remove_outliers and not df_plot.empty:
        if n_outliers_to_remove >= len(df_plot):
            st.info("Cannot remove more outliers than available data points. Try reducing the number of outliers.")
            return

        df_plot = df_plot.sort_values(by='Density (per km²)', ascending=False).iloc[n_outliers_to_remove:].copy()
        title_suffix = f" (Top {n_outliers_to_remove} Density Outliers Removed)"

    if not df_plot.empty:
        min_area = df_plot['Area (km²)'].min()
        max_area = df_plot['Area (km²)'].max()
        min_density = df_plot['Density (per km²)'].min()
        max_density = df_plot['Density (per km²)'].max()

        range_x_min_val = max(1.0, min_area * 0.9)
        range_x_max_val = max_area * 1.1
        range_y_min_val = max(0.1, min_density * 0.9)
        range_y_max_val = max_density * 1.1

        fig = px.scatter(
            df_plot,
            x='Area (km²)',
            range_x=[range_x_min_val, range_x_max_val],
            y='Density (per km²)',
            range_y=[range_y_min_val, range_y_max_val],
            size='Population',
            color='Country/Territory',
            hover_name='Country/Territory',
            log_x=True,
            title=f'Population Density vs. Area for {int(selected_year)}{exclusion_text}{title_suffix}',
            labels={
                'Area (km²)': 'Area (km²)',
                'Density (per km²)': 'Density (per km²)',
                'Population': 'Population'
            },
            hover_data={
                'Population': ':,',
                'Area (km²)': ':,',
                'Density (per km²)': ':.2f'
            }
        )
        fig.update_traces(marker=dict(sizemin=3))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info(f"No data available for Population Density vs. Area for the year {int(selected_year)}{exclusion_text}{title_suffix}.")


def plot_world_population_share(df: pd.DataFrame, selected_year: int, exclusion_text: str, threshold: float = 1.0):
    """
    Generates a pie chart for world population share for a specific year.
    Combines countries with a share below a certain threshold into "Other Countries".

    Args:
        df (pd.DataFrame): The filtered DataFrame containing population data.
        selected_year (int): The year to display data for.
        exclusion_text (str): Text indicating any globally excluded countries.
        threshold (float): The percentage threshold below which countries are grouped into "Other Countries".
    """
    df_plot = df[df['Year'] == selected_year].sort_values(by='World Population Percentage', ascending=False).copy()

    if not df_plot.empty:
        df_large_share = df_plot[df_plot['World Population Percentage'] >= threshold].copy()
        df_other = df_plot[df_plot['World Population Percentage'] < threshold].copy()

        if not df_other.empty:
            other_percentage = df_other['World Population Percentage'].sum()
            other_population = df_other['Population'].sum()
            new_row = {
                'Country/Territory': 'Other Countries',
                'World Population Percentage': other_percentage,
                'Population': other_population,
                'Year': selected_year,
                'CCA3': 'OTH',
                'Rank': np.nan, 'Area (km²)': np.nan, 'Density (per km²)': np.nan, 'Growth Rate': np.nan,
                'World Population Percentage Rank': np.nan
            }
            # Use pd.concat for adding a new row/DataFrame
            df_large_share = pd.concat([df_large_share, pd.DataFrame([new_row])], ignore_index=True)

        fig = px.pie(
            df_large_share,
            values='World Population Percentage',
            names='Country/Territory',
            title=f'World Population Share by Country in {int(selected_year)}{exclusion_text}',
            hover_data={'Population': ':,', 'World Population Percentage': ':.2f%'},
            labels={'World Population Percentage': 'Share (%)'}
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info(f"No data available for World Population Share for the year {int(selected_year)}{exclusion_text}.")


def plot_population_growth_rate(df: pd.DataFrame, selected_year: int, exclusion_text: str):
    """
    Generates a bar chart for population growth rates for a specific year.

    Args:
        df (pd.DataFrame): The filtered DataFrame containing population data.
        selected_year (int): The year to display data for.
        exclusion_text (str): Text indicating any globally excluded countries.
    """
    df_plot = df[df['Year'] == selected_year].copy()
    df_plot_cleaned = df_plot.dropna(subset=['Growth Rate'])

    if not df_plot_cleaned.empty:
        fig = px.bar(
            df_plot_cleaned.head(50),
            x='Country/Territory',
            y='Growth Rate',
            color='Growth Rate',
            title=f'Population Growth Rate by Country in {int(selected_year)}{exclusion_text}',
            labels={'Growth Rate': 'Growth Rate (%)'},
            hover_data={'Growth Rate': ':.2%', 'Population': ':,', 'Density (per km²)': ':.2f'}
        )
        fig.update_layout(xaxis={'categoryorder': 'total descending'})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info(f"No valid growth rate data available for the year {int(selected_year)}{exclusion_text}.")


def plot_population_vs_density_scatter(df: pd.DataFrame, selected_year: int, exclusion_text: str):
    """
    Generates a scatter plot for population vs. density for a specific year.

    Args:
        df (pd.DataFrame): The filtered DataFrame containing population data.
        selected_year (int): The year to display data for.
        exclusion_text (str): Text indicating any globally excluded countries.
    """
    df_plot = df[df['Year'] == selected_year].copy()
    df_plot.dropna(subset=['Population', 'Density (per km²)'], inplace=True)

    if not df_plot.empty:
        fig = px.scatter(
            df_plot,
            x='Population',
            y='Density (per km²)',
            size='Population',
            color='Country/Territory',
            hover_name='Country/Territory',
            log_x=True,
            log_y=True,
            title=f'Population vs. Density in {int(selected_year)}{exclusion_text}',
            labels={
                'Population': 'Population',
                'Density (per km²)': 'Density (per km²)'
            },
            hover_data={
                'Population': ':,',
                'Area (km²)': ':,',
                'Density (per km²)': ':.2f',
                'Growth Rate': ':.2%'
            }
        )
        fig.update_traces(marker=dict(sizemin=3))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info(f"No data available for Population vs. Density for the year {int(selected_year)}{exclusion_text}.")


def plot_population_heatmap(df: pd.DataFrame, selected_year: int, exclusion_text: str):
    """
    Generates a choropleth map for world population for a specific year.

    Args:
        df (pd.DataFrame): The filtered DataFrame containing population data.
        selected_year (int): The year to display data for.
        exclusion_text (str): Text indicating any globally excluded countries.
    """
    df_map = df[df['Year'] == selected_year].copy()

    if not df_map.empty and 'Population' in df_map.columns and 'CCA3' in df_map.columns:
        fig = px.choropleth(
            df_map,
            locations='CCA3',
            color='Population',
            hover_name='Country/Territory',
            color_continuous_scale=px.colors.sequential.Plasma,
            title=f'World Population Distribution in {int(selected_year)}{exclusion_text}',
            projection='natural earth',
            labels={'Population': 'Population'},
            hover_data={'Population': ':,', 'Area (km²)': ':,', 'Density (per km²)': ':.2f'}
        )
        fig.update_geos(
            showland=True, showocean=True, oceancolor="LightBlue",
            showlakes=True, lakecolor="Blue", showrivers=True, rivercolor="Blue"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info(f"No sufficient data available for World Population Heatmap for the year {int(selected_year)}{exclusion_text}.")


def plot_population_density_heatmap(df: pd.DataFrame, selected_year: int, exclusion_text: str):
    """
    Generates a choropleth map for world population density (log-scaled) for a specific year.

    Args:
        df (pd.DataFrame): The filtered DataFrame containing population data.
        selected_year (int): The year to display data for.
        exclusion_text (str): Text indicating any globally excluded countries.
    """
    df_map = df[df['Year'] == selected_year].copy()

    df_map['Density (per km²)'] = pd.to_numeric(df_map['Density (per km²)'], errors='coerce')
    df_map['Density_Log10'] = df_map['Density (per km²)'].apply(
        lambda x: np.log10(x) if x > 0 else np.nan
    )
    df_map.dropna(subset=['CCA3', 'Density_Log10'], inplace=True)

    if not df_map.empty:
        fig = px.choropleth(
            df_map,
            locations='CCA3',
            color='Density_Log10',
            hover_name='Country/Territory',
            color_continuous_scale=px.colors.sequential.Viridis,
            title=f'World Population Density Distribution in {int(selected_year)}{exclusion_text} (Logarithmic Scale)',
            projection='natural earth',
            labels={'Density_Log10': 'Density (log10)'},
            hover_data={
                'Population': ':,',
                'Area (km²)': ':,',
                'Density (per km²)': ':.2f',
                'Density_Log10': ':.2f'
            },
        )
        fig.update_geos(
            showland=True, showocean=True, oceancolor="LightBlue",
            showlakes=True, lakecolor="Blue", showrivers=True, rivercolor="Blue"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info(f"No sufficient data available for World Population Density Heatmap for the year {int(selected_year)}{exclusion_text}.")

def plot_population_projections(df_plot: pd.DataFrame, exclusion_text: str):
    """
    Generates a line plot showing historical, projected future, and backcasted population.

    Args:
        df_plot (pd.DataFrame): DataFrame containing historical and projected/backcasted data,
                                should have a 'Type' column ('Historical', 'Projected (Future)', 'Projected (Past)').
        exclusion_text (str): Text indicating any globally excluded countries.
    """
    if not df_plot.empty:
        fig = px.line(
            df_plot,
            x='Year',
            y='Population',
            color='Country/Territory',
            line_dash='Type',  # Use line_dash to distinguish historical/projected
            title=f'Population Projections and Backcasting for Selected Countries{exclusion_text}',
            labels={'Population': 'Population', 'Year': 'Year'},
            hover_data={'Population': ':,', 'Year': True, 'Type': True, 'Growth Rate': ':.2%'}
        )
        fig.update_layout(hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No projection data available for the selected countries.")