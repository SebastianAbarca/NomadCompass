from app.util import util
import pandas as pd
import streamlit as st
import plotly.express as px
import numpy as np  # Import numpy for np.nan
from ..util import population_graphs, my_math
# Configuration and Constants
AVAILABLE_YEARS = [2022, 2020, 2015, 2010, 2000, 1990, 1980, 1970]
AVAILABLE_YEARS.sort()

# Load data once at the beginning to avoid re-loading on every Streamlit rerun
@st.cache_data
def load_population_data():
    return util.load_data('data/world_population_data.csv')
def preprocess_and_filter_population_data(df: pd.DataFrame, available_years: list, exclude_countries: list):
    df_filtered = df.copy()

    if exclude_countries:
        df_filtered = df_filtered[~df_filtered['Country/Territory'].isin(exclude_countries)]

    if 'Year' in df_filtered.columns:
        df_filtered = df_filtered[df_filtered['Year'].isin(available_years)]

    return df_filtered

df_population = load_population_data()


def population_page():
    st.header("World Population Overview")
    st.write("Explore various aspects of global population data.")

    # Load data
    df_population = load_population_data()

    if df_population.empty:
        st.error("Population data could not be loaded. Please check the data source and path.")
        return

    # Determine default selected year
    selected_year = AVAILABLE_YEARS[-1] if AVAILABLE_YEARS else 2022
    if not AVAILABLE_YEARS:
        st.error("Error: No available years defined for population data. Defaulting to 2022.")

    # --- GLOBAL FILTER FOR CHINA/INDIA ---
    st.subheader("Global Data Filters")
    exclude_countries_global = st.multiselect(
        "Exclude Countries from All Visualizations:",
        options=['China', 'India'],
        default=[],
        help="Select countries to exclude from all charts on this page. Useful for focusing on patterns without large outliers."
    )

    # Apply global filters
    df_population_filtered = preprocess_and_filter_population_data(
        df_population, AVAILABLE_YEARS, exclude_countries_global
    )

    if df_population_filtered.empty:
        st.warning(
            "No valid data remaining after applying global filters and filtering for available years. Please adjust your selections.")
        return

    exclusion_text = f" (Excluding {', '.join(exclude_countries_global)})" if exclude_countries_global else ""

    # --- GLOBAL YEAR SELECTION WITH ST.PILLS ---
    st.markdown("---")
    st.subheader("Select Year for All Single-Year Charts")

    pills_output = st.pills(
        label="Year",
        options=AVAILABLE_YEARS,
        default=selected_year,
        key="global_year_pills_selector",
    )

    if pills_output is not None:
        selected_year = pills_output

    st.write(f"All single-year charts are currently showing data for: **{int(selected_year)}**")
    st.markdown("---")
    # --- END GLOBAL YEAR SELECTION ---

    with st.expander("View Raw Population Data"):
        st.dataframe(df_population_filtered)
        st.write("Columns available for analysis:", df_population_filtered.columns.tolist())

    st.markdown("---")

    # --- Visualizations ---

    # 1. Population Trend Over Years for Selected Countries
    st.subheader(f"Population Trends by Country and Year{exclusion_text}")
    countries = sorted(df_population_filtered['Country/Territory'].unique())
    selected_countries_trend = st.multiselect(
        "Select Countries to Compare Population Trends:",
        options=countries,
        default=countries[:5] if len(countries) >= 5 else countries,
        key="trend_countries_selector"
    )
    population_graphs.plot_population_trend(df_population_filtered, selected_countries_trend, exclusion_text)

    st.markdown("---")

    # 2. Top N Countries by Population (Current Year)
    st.subheader(f"Top Countries by Population{exclusion_text}")
    st.write(f"Showing data for the selected year: **{int(selected_year)}**")
    df_for_top_n_slider = df_population_filtered[df_population_filtered['Year'] == selected_year]
    top_n = st.slider(
        "Select number of top countries:",
        min_value=1,
        max_value=min(50, len(df_for_top_n_slider)),
        value=min(10, len(df_for_top_n_slider))
    )
    population_graphs.plot_top_n_population(df_population_filtered, selected_year, top_n, exclusion_text)

    st.markdown("---")

    # 3. Population Density vs. Area (Scatter Plot)
    st.subheader(f"Population Density vs. Area ({selected_year}){exclusion_text}")
    st.write("Examine the relationship between a country's area and its population density.")
    population_graphs.plot_density_vs_area(df_population_filtered, selected_year, exclusion_text, remove_outliers=False)

    st.markdown("---")

    # 3b. Population Density vs. Area (Outliers Removed)
    st.subheader(f"Population Density vs. Area (Outliers Removed - {int(selected_year)}){exclusion_text}")
    st.write(
        "This plot allows you to exclude countries with the highest population density to better show patterns among others.")
    df_for_outlier_slider = df_population_filtered[df_population_filtered['Year'] == selected_year].dropna(
        subset=['Density (per km²)'])
    max_outliers = max(0, len(df_for_outlier_slider) - 1)  # Ensure at least one country remains
    n_outliers_to_remove = st.slider("Number of Outliers to remove", min_value=0,
                                     max_value=min(10, max_outliers),  # Cap at 10 or max_outliers
                                     value=min(5, max_outliers),  # Default to 5 or less if not enough data
                                     key="num_outliers_slider")
    if n_outliers_to_remove > 0:
        population_graphs.plot_density_vs_area(df_population_filtered, selected_year, exclusion_text, remove_outliers=True,
                             n_outliers_to_remove=n_outliers_to_remove)
    else:
        st.info("Adjust the slider to remove top density outliers and see the adjusted plot.")

    st.markdown("---")

    # 4. World Population Percentage (Pie Chart for a specific year)
    st.subheader(f"World Population Share by Country{exclusion_text}")
    population_graphs.plot_world_population_share(df_population_filtered, selected_year, exclusion_text)

    st.markdown("---")

    # 5. Population Growth Rate (Bar Chart)
    st.subheader(f"Population Growth Rate by Country{exclusion_text}")
    st.write(f"Visualize the population growth rates across different countries for {int(selected_year)}.")
    population_graphs.plot_population_growth_rate(df_population_filtered, selected_year, exclusion_text)

    st.markdown("---")

    # 6. Population vs. Density (Scatter Plot)
    st.subheader(f"Population vs. Density Scatter Plot{exclusion_text}")
    st.write("Explore the relationship between a country's total population and its density.")
    population_graphs.plot_population_vs_density_scatter(df_population_filtered, selected_year, exclusion_text)

    st.markdown("---")

    # 7. World Population Heatmap
    st.subheader(f"World Population Heatmap ({int(selected_year)}){exclusion_text}")
    st.write("Visualize global population distribution by country. Countries with missing data will be uncolored.")
    population_graphs.plot_population_heatmap(df_population_filtered, selected_year, exclusion_text)

    st.markdown("---")

    # 8. World Population Density Heatmap (Manually Log-Scaled)
    st.subheader(f"Population Projections and Backcasting{exclusion_text}")
    st.write(
        "Visualize future population estimates and backcasted populations based on mathematical projections from historical growth rates.")
    st.warning(
        "Note: These projections are based on a simple exponential growth model using recent historical growth rates. They are for illustrative purposes only and may not reflect real-world complexities. For robust projections, consult dedicated demographic datasets.")

    future_years_options = [2025, 2030, 2035, 2040, 2045, 2050, 2060, 2070, 2080, 2090, 2100]
    backcast_years_options = [1960, 1950, 1940, 1930, 1920, 1910, 1900]

    col1, col2 = st.columns(2)
    with col1:
        selected_future_years = st.multiselect(
            "Select Future Years for Projection:",
            options=future_years_options,
            default=[2030, 2050],
            help="Select years to project population forward."
        )
    with col2:
        selected_backcast_years = st.multiselect(
            "Select Past Years for Backcasting:",
            options=backcast_years_options,
            default=[1960],
            help="Select years to backcast population."
        )

    if not selected_future_years and not selected_backcast_years:
        st.info("Please select at least one year for future projection or backcasting to see the chart.")
        return

    # Call the population_projection function from the my_math module
    # Ensure df_historical is the correct DataFrame (df_population_filtered)
    df_projections_data = my_math.population_projection(
        df_population_filtered, selected_future_years, selected_backcast_years
    )

    if df_projections_data.empty:
        st.warning(
            "Could not generate population projections or backcasting data. This might be due to missing historical population or growth rate data for selected countries or no years selected.")
        return

    countries_for_projection = sorted(df_projections_data['Country/Territory'].unique())
    selected_countries_projection = st.multiselect(
        "Select Countries for Projections/Backcasting Visualization:",
        options=countries_for_projection,
        default=countries_for_projection[:5] if len(countries_for_projection) >= 5 else countries_for_projection,
        key="projection_countries_selector"
    )

    if selected_countries_projection:
        df_plot_projections = df_projections_data[
            df_projections_data['Country/Territory'].isin(selected_countries_projection)
        ].copy()

        # Call the plotting function from the population_graphs module
        population_graphs.plot_population_projections(df_plot_projections, exclusion_text)

        with st.expander("View Raw Projection Data Table"):
            st.dataframe(df_plot_projections.sort_values(by=['Country/Territory', 'Year']))
    else:
        st.info("Please select at least one country to view population projections.")

