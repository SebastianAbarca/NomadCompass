import streamlit as st
import pandas as pd
from app.util import util, my_math, data_processing
from app.util import aggregate_cpi_graphs



st.header("Aggregate CPI Data")

# --- Data Loading and Initial Preprocessing ---
df_cpi = data_processing.load_and_preprocess_cpi_data()
df_population = data_processing.load_and_preprocess_population_data()

if df_cpi.empty:
    st.info("No CPI data available to display the Aggregate CPI page.")


# --- CPI Over Time Visualization ---
st.subheader("CPI Over Time by Country")
countries = df_cpi['COUNTRY_NAME'].unique()
selected_countries = st.multiselect(
    "Select one or more countries to visualize CPI over time:",
    options=sorted(countries),
    default=['Aruba']
)

if selected_countries:
    aggregate_cpi_graphs.plot_cpi_over_time(df_cpi, selected_countries)
else:
    st.info("Please select at least one country to display the CPI over time chart.")

st.markdown("---")

# --- CPI Stability Analysis ---
st.subheader("Top 10 Most Stable Countries (Lowest CPI Volatility)")

# Call the new data_processing function to merge CPI with population for filtering
df_cpi_with_population_for_stability = data_processing.merge_cpi_with_population_for_filtering(
    df_cpi, df_population
)

# Initialize filtered_cpi_df from the merged DataFrame
filtered_cpi_df = df_cpi_with_population_for_stability.copy()

# --- Population Filtering for Stability Analysis UI (THIS IS THE CORRECT BLOCK) ---
if 'Population' in filtered_cpi_df.columns and not filtered_cpi_df['Population'].isnull().all():
    min_pop_val = filtered_cpi_df['Population'].min()
    max_pop_val = filtered_cpi_df['Population'].max()

    # Convert to millions for slider readability
    min_pop_M = int(min_pop_val // 1_000_000)
    max_pop_M = int((max_pop_val + 999_999) // 1_000_000)

    # Handle edge case where min and max population are very close or identical
    if min_pop_M >= max_pop_M:
        population_range_M = (min_pop_M, min_pop_M + 1) if min_pop_M != 0 else (0, 1)
        st.info(
            f"Limited effective population range for slider: {population_range_M[0]}M to {population_range_M[1]}M.")
    else:
        population_range_M = st.slider(
            'Select Population Range (in millions) for Stability Analysis:',
            min_value=min_pop_M,
            max_value=max_pop_M,
            value=(min_pop_M, max_pop_M),
            step=max(1, (max_pop_M - min_pop_M) // 100),
            format='%dM'
        )

    # Apply population filter
    filtered_cpi_df = filtered_cpi_df[
        (filtered_cpi_df['Population'] >= population_range_M[0] * 1_000_000) &
        (filtered_cpi_df['Population'] <= population_range_M[1] * 1_000_000)
        ].copy()
    st.info(f"Filtering countries with population between {population_range_M[0]}M and {population_range_M[1]}M.")
else:
    st.info(
        "Population data not available or incomplete for filtering. Stability analysis will proceed without population filtering.")

# --- Calculate Stability ---
stability_df = data_processing.calculate_cpi_stability(filtered_cpi_df)

# --- Display Stability Results ---
if not stability_df.empty:
    top_stable = stability_df.head(10)

    col1, col2 = st.columns([4, 3])
    with col1:
        aggregate_cpi_graphs.plot_cpi_stability_bar(top_stable)
    with col2:
        st.write("### Stability Data Table")
        st.dataframe(top_stable.set_index('COUNTRY_NAME').round(2), use_container_width=True)
else:
    st.info("Not enough data to calculate CPI stability for the selected population range.")

st.markdown("---")

# --- CPI by Population Scatter Plot ---
st.subheader("CPI by Population Scatter Plot")
st.write(
    "Explore the relationship between a country's CPI and its population, including historical and projected population data.")

# Prepare data for scatter plot using data_processing function
df_cpi_pop_merged_initial = data_processing.prepare_cpi_population_scatter_data(df_cpi, df_population)

# --- Outlier Filtering Section for Scatter Plot UI (now calls my_math) ---
df_cpi_pop_merged_filtered = df_cpi_pop_merged_initial.copy()  # Initialize with unfiltered data

if not df_cpi_pop_merged_initial.empty:
    st.markdown("##### Scatter Plot Outlier Filtering")
    enable_outlier_filter = st.checkbox("Enable Outlier Filtering for Scatter Plot", value=True,
                                        key="scatter_outlier_toggle")

    if enable_outlier_filter:
        iqr_multiplier = st.slider(
            "IQR Multiplier (determines outlier sensitivity):",
            min_value=0.0,
            max_value=15.0,
            value=5.0,
            step=1.0,
            help="Values outside Q1 - (Multiplier * IQR) and Q3 + (Multiplier * IQR) are considered outliers."
        )

        columns_to_filter = ['Population', 'Avg_Annual_CPI_Value'] # Corrected column name

        # Call the outlier function from my_math.py
        df_cpi_pop_merged_filtered, removed_rows = my_math.apply_iqr_outlier_filter(
            df_cpi_pop_merged_initial, columns_to_filter, iqr_multiplier
        )

        if removed_rows > 0:
            st.info(
                f"Removed {removed_rows} outlier rows ({removed_rows / len(df_cpi_pop_merged_initial):.1%}) from the scatter plot data using IQR filtering (Multiplier: {iqr_multiplier}).")
        else:
            st.info("No outliers detected or removed with the current settings.")
    else:
        st.info("Outlier filtering is disabled. All available data will be plotted.")
else:
    st.warning("No sufficient combined CPI and Population data available to apply outlier filtering.")

# --- Scatter Plot Display ---
if not df_cpi_pop_merged_filtered.empty:
    min_plot_year = int(df_cpi_pop_merged_filtered['Year'].min())
    max_plot_year = int(df_cpi_pop_merged_filtered['Year'].max())

    # Determine a sensible default year for the slider
    default_plot_year = min(max_plot_year, 2022)
    if default_plot_year < min_plot_year:
        default_plot_year = max_plot_year

    selected_plot_year = st.slider(
        "Select Year for CPI vs. Population Scatter Plot:",
        min_value=min_plot_year,
        max_value=max_plot_year,
        value=default_plot_year,
        step=1,
        format="%d",
        key="cpi_pop_scatter_slider"
    )

    df_plot_cpi_pop = df_cpi_pop_merged_filtered[df_cpi_pop_merged_filtered['Year'] == selected_plot_year].copy()

    if not df_plot_cpi_pop.empty:
        aggregate_cpi_graphs.plot_cpi_population_scatter(df_plot_cpi_pop, selected_plot_year)
    else:
        st.info(
            f"No combined CPI and Population data available for {selected_plot_year} for the scatter plot after filtering. Try selecting another year or adjusting filter settings.")
else:
    st.warning(
        "No sufficient combined CPI and Population data to generate the scatter plot after filtering. This might be due to all data being filtered out as outliers.")

st.markdown("---")

# --- Explore Individual Country CPI Data Table ---
all_countries_available_for_details = sorted(df_cpi['COUNTRY_NAME'].unique())
selected_country_agg_explore = st.selectbox(
    'Select a Country to view all its CPI data:',
    all_countries_available_for_details,
    key="country_cpi_details_select"
)

if selected_country_agg_explore:
    country_df_agg_explore = df_cpi[
        df_cpi['COUNTRY_NAME'] == selected_country_agg_explore
        ].copy()
    st.write(f"### Detailed CPI Data for {selected_country_agg_explore}")
    st.dataframe(country_df_agg_explore.round(2), use_container_width=True)