from app.util import util
import pandas as pd
import streamlit as st
import plotly.express as px
import numpy as np  # Import numpy for np.nan


# Load data once at the beginning to avoid re-loading on every Streamlit rerun
@st.cache_data
def load_population_data():
    return util.load_data('data/world_population_data.csv')


df_population = load_population_data()


def population_page():
    # Define the explicitly available years
    AVAILABLE_YEARS = [2022, 2020, 2015, 2010, 2000, 1990, 1980, 1970]
    # Sort them for proper display order
    AVAILABLE_YEARS.sort() # Ensure they are sorted for the pills display

    # *** CRITICAL CHANGE HERE: Initialize selected_year with a guaranteed valid default ***
    # This ensures selected_year always has an int value, even if st.pills
    # returns None on initial render or if AVAILABLE_YEARS is unexpectedly empty.
    if AVAILABLE_YEARS:
        selected_year = AVAILABLE_YEARS[-1] # Default to the most recent year (e.g., 2022)
    else:
        # Fallback to a hardcoded year if AVAILABLE_YEARS is empty (highly unlikely for hardcoded list)
        selected_year = 2022
        st.error("Error: No available years defined for population data.")
        return # Exit early if no years are available

    st.header("Population Data Insights")
    if df_population.empty:
        st.warning(
            "Population data not loaded. Please ensure 'data/world_population_data.csv' exists and is accessible.")
        return

    st.header("World Population Overview")
    st.write("Explore various aspects of global population data.")

    # --- GLOBAL FILTER FOR CHINA/INDIA ---
    st.subheader("Global Data Filters")
    exclude_countries_global = st.multiselect(
        "Exclude Countries from All Visualizations:",
        options=['China', 'India'],
        default=[],
        help="Select countries to exclude from all charts on this page. Useful for focusing on patterns without large outliers."
    )

    df_population_filtered = df_population.copy()
    if exclude_countries_global:
        df_population_filtered = df_population_filtered[
            ~df_population_filtered['Country/Territory'].isin(exclude_countries_global)]

    # Ensure 'Year' is treated as a numerical type globally for consistency
    if 'Year' in df_population_filtered.columns:
        df_population_filtered['Year'] = pd.to_numeric(df_population_filtered['Year'], errors='coerce')
        # Drop rows where Year couldn't be converted before any further operations
        df_population_filtered.dropna(subset=['Year'], inplace=True)

    # --- NEW: Filter df_population_filtered to ONLY include the AVAILABLE_YEARS ---
    df_population_filtered = df_population_filtered[df_population_filtered['Year'].isin(AVAILABLE_YEARS)]

    # Check if there's any valid data left after all filtering and year conversion
    if df_population_filtered.empty:
        st.warning("No valid data remaining after applying global filters and filtering for available years.")
        return

    exclusion_text = ""
    if exclude_countries_global:
        exclusion_text = f" (Excluding {', '.join(exclude_countries_global)})"
    # --- END GLOBAL FILTER ---

    # --- MODIFIED: GLOBAL YEAR SELECTION WITH ST.PILLS ---
    st.markdown("---")
    st.subheader("Select Year for All Single-Year Charts")

    # The value from st.pills will be stored here.
    # If it's not None, it will update the `selected_year` initialized above.
    pills_output = st.pills(
        label="Year", # Label for the pills component
        options=AVAILABLE_YEARS, # List of years to display as pills
        default=selected_year, # Use the already initialized selected_year as the default
        key="global_year_pills_selector", # Unique key for the component
    )

    # *** CRITICAL CHANGE HERE: Conditionally update selected_year based on pills_output ***
    if pills_output is not None:
        selected_year = pills_output
    # Else, selected_year retains its initial default value, ensuring it's never None.


    st.write(f"All single-year charts are currently showing data for: **{int(selected_year)}**")
    st.markdown("---")
    # --- END GLOBAL YEAR SELECTION ---


    # Display the raw dataframe (optional, good for initial inspection)
    with st.expander("View Raw Population Data"):
        st.dataframe(df_population_filtered)  # Display filtered data
        st.write("Columns available for analysis:", df_population_filtered.columns.tolist())

    st.markdown("---")

    # 1. Population Trend Over Years for Selected Countries
    st.subheader(f"Population Trends by Country and Year{exclusion_text}")

    countries = sorted(df_population_filtered['Country/Territory'].unique())
    selected_countries_trend = st.multiselect(
        "Select Countries to Compare Population Trends:",
        options=countries,
        default=countries[:5] if len(countries) >= 5 else countries,  # Default to top 5 or all if less
        key="trend_countries_selector"
    )

    if selected_countries_trend:
        df_filtered_trend = df_population_filtered[
            df_population_filtered['Country/Territory'].isin(selected_countries_trend)].sort_values(by='Year')
        if not df_filtered_trend.empty:
            fig_trend = px.line(
                df_filtered_trend,
                x='Year',
                y='Population',
                color='Country/Territory',
                title=f'Population Over Time for Selected Countries{exclusion_text}',
                labels={'Population': 'Population', 'Year': 'Year'},
                hover_data={'Population': ':,', 'Year': True}
            )
            fig_trend.update_layout(hovermode="x unified")
            st.plotly_chart(fig_trend, use_container_width=True)
        else:
            st.info("No data available for the selected countries and years.")
    else:
        st.info("Please select at least one country to view population trends.")

    st.markdown("---")

    # 2. Top N Countries by Population (Current Year)
    st.subheader(f"Top Countries by Population{exclusion_text}")

    if 'Year' in df_population_filtered.columns and 'Population' in df_population_filtered.columns:
        # This chart now uses the `selected_year` from the pills
        # The pd.isna check is a safeguard, but selected_year should now always be an int
        if pd.isna(selected_year): # This line should now virtually never be True
            st.info("No valid year selected or found in the filtered dataset for 'Top Countries by Population'.")
        else:
            st.write(f"Showing data for the selected year: **{int(selected_year)}**")

            df_selected_year = df_population_filtered[df_population_filtered['Year'] == selected_year].sort_values(
                by='Population', ascending=False)
            top_n = st.slider(
                "Select number of top countries:",
                min_value=1,
                max_value=min(50, len(df_selected_year)),
                value=min(10, len(df_selected_year))
            )

            if top_n == 0:
                st.info("Please select a number greater than 0 for top countries.")
            elif not df_selected_year.empty:
                fig_top_population = px.bar(
                    df_selected_year.head(top_n),
                    x='Country/Territory',
                    y='Population',
                    color='Population',
                    title=f'Top {top_n} Countries by Population in {int(selected_year)}{exclusion_text}',
                    labels={'Population': 'Population', 'Country/Territory': 'Country'},
                    hover_data={'Population': ':,', 'Area (km²)': ':,', 'Density (per km²)': ':.2f'}
                )
                fig_top_population.update_layout(xaxis={'categoryorder': 'total descending'})
                st.plotly_chart(fig_top_population, use_container_width=True)
            else:
                st.info(f"No population data found for the year {int(selected_year)} after filters.")
    else:
        st.warning(
            "Required columns ('Year', 'Population') not found in the dataset for 'Top Countries by Population' visualization after filters.")

    st.markdown("---")

    # 3. Population Density vs. Area (Scatter Plot)
    # Fixed typo here: added missing '(' around selected_year
    st.subheader(f"Population Density vs. Area ({selected_year}){exclusion_text}")
    st.write("Examine the relationship between a country's area and its population density.")

    # Now uses the globally determined selected_year
    df_density_year = df_population_filtered[df_population_filtered['Year'] == selected_year].copy()
    df_density_year.dropna(subset=['Area (km²)', 'Density (per km²)', 'Population'], inplace=True)


    if not df_density_year.empty:
        min_area = df_density_year['Area (km²)'].min()
        max_area = df_density_year['Area (km²)'].max()

        min_density = df_density_year['Density (per km²)'].min()
        max_density = df_density_year['Density (per km²)'].max()

        range_x_min_val = max(1.0, min_area * 0.9)
        range_x_max_val = max_area * 1.1

        range_y_min_val = max(0.1, min_density * 0.9)
        range_y_max_val = max_density * 1.1


        fig_density = px.scatter(
            df_density_year,
            x='Area (km²)',
            range_x=[range_x_min_val, range_x_max_val],
            y='Density (per km²)',
            range_y=[range_y_min_val, range_y_max_val],
            size='Population',
            color='Country/Territory',
            hover_name='Country/Territory',
            log_x=True,
            title=f'Population Density vs. Area for {int(selected_year)}{exclusion_text}', # Used selected_year
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
        fig_density.update_traces(marker=dict(sizemin=3))
        st.plotly_chart(fig_density, use_container_width=True)
    else:
        st.info(f"No data available for Population Density vs. Area for the year {int(selected_year)}{exclusion_text}.")

    st.markdown("---")

    # --- NEW SECTION: 3b. Population Density vs. Area (Outliers Removed) ---
    st.subheader(f"Population Density vs. Area (Top 5 Density Outliers Removed - {int(selected_year)}){exclusion_text}")
    st.write("This plot excludes the 5 countries with the highest population density to better show patterns among others.")

    # Now uses the globally determined selected_year
    df_density_year_filtered_outliers = df_population_filtered[df_population_filtered['Year'] == selected_year].copy()
    df_density_year_filtered_outliers.dropna(subset=['Area (km²)', 'Density (per km²)', 'Population'], inplace=True)

    if not df_density_year_filtered_outliers.empty:
        # Slider for number of outliers to remove (independent of year)
        n_outliers_to_remove = st.slider("Number of Outliers to remove", min_value=1, max_value=min(10, len(df_density_year_filtered_outliers)-1), value=5, key="num_outliers_slider")
        if n_outliers_to_remove == 0: # Handle case if slider is accidentally set to 0, though min_value=1
             st.info("Please select a number greater than 0 for outliers to remove.")
        else:
            # Sort by Density in descending order and remove the top n
            df_density_year_filtered_outliers = df_density_year_filtered_outliers.sort_values(
                by='Density (per km²)', ascending=False
            ).iloc[n_outliers_to_remove:].copy() # Remove the top n

            if df_density_year_filtered_outliers.empty:
                st.info("No data remaining after removing top outliers. Try reducing the number of outliers to remove.")
            else:
                # Recalculate ranges based on the new, filtered dataframe
                min_area_outliers = df_density_year_filtered_outliers['Area (km²)'].min()
                max_area_outliers = df_density_year_filtered_outliers['Area (km²)'].max()

                min_density_outliers = df_density_year_filtered_outliers['Density (per km²)'].min()
                max_density_outliers = df_density_year_filtered_outliers['Density (per km²)'].max()

                range_x_min_outliers = max(1.0, min_area_outliers * 0.9)
                range_x_max_outliers = max_area_outliers * 1.1

                range_y_min_outliers = max(0.1, min_density_outliers * 0.9)
                range_y_max_outliers = max_density_outliers * 1.1

                fig_density_outliers = px.scatter(
                    df_density_year_filtered_outliers,
                    x='Area (km²)',
                    range_x=[range_x_min_outliers, range_x_max_outliers],
                    y='Density (per km²)',
                    range_y=[range_y_min_outliers, range_y_max_outliers],
                    size='Population',
                    color='Country/Territory',
                    hover_name='Country/Territory',
                    log_x=True,
                    title=f'Population Density vs. Area in {int(selected_year)}{exclusion_text} (Top {n_outliers_to_remove} Density Outliers Removed)', # Used selected_year
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
                fig_density_outliers.update_traces(marker=dict(sizemin=3))
                st.plotly_chart(fig_density_outliers, use_container_width=True)
    else:
        st.info(
            f"No data available or not enough data after removing outliers for Population Density vs. Area for the year {int(selected_year)}{exclusion_text}.")

    st.markdown("---")

    # 4. World Population Percentage (Pie Chart for a specific year)
    st.subheader(f"World Population Share by Country{exclusion_text}")

    # Now uses the globally determined selected_year
    df_percentage_year = df_population_filtered[df_population_filtered['Year'] == selected_year].sort_values(
        by='World Population Percentage', ascending=False)

    if not df_percentage_year.empty:
        threshold = 1.0
        df_large_share = df_percentage_year[df_percentage_year['World Population Percentage'] >= threshold].copy()
        df_other = df_percentage_year[df_percentage_year['World Population Percentage'] < threshold].copy()

        if not df_other.empty:
            other_percentage = df_other['World Population Percentage'].sum()
            other_population = df_other['Population'].sum()
            new_row = {
                'Country/Territory': 'Other Countries',
                'World Population Percentage': other_percentage,
                'Population': other_population,
                'Year': selected_year, # Used selected_year
                'CCA3': 'OTH',
                'Rank': np.nan, 'Area (km²)': np.nan, 'Density (per km²)': np.nan, 'Growth Rate': np.nan,
                'World Population Percentage Rank': np.nan
            }
            df_large_share = pd.concat([df_large_share, pd.DataFrame([new_row])], ignore_index=True)

        fig_percentage = px.pie(
            df_large_share,
            values='World Population Percentage',
            names='Country/Territory',
            title=f'World Population Share by Country in {int(selected_year)}{exclusion_text}', # Used selected_year
            hover_data={'Population': ':,', 'World Population Percentage': ':.2f%'},
            labels={'World Population Percentage': 'Share (%)'}
        )
        fig_percentage.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_percentage, use_container_width=True)
    else:
        st.info(f"No data available for World Population Share for the year {int(selected_year)}{exclusion_text}.")

    st.markdown("---")

    # 5. Population Growth Rate (Bar Chart)
    st.subheader(f"Population Growth Rate by Country{exclusion_text}")
    st.write(f"Visualize the population growth rates across different countries for {int(selected_year)}.") # Added int() for consistency

    # Now uses the globally determined selected_year
    df_growth_year = df_population_filtered[df_population_filtered['Year'] == selected_year].copy()
    df_growth_year_cleaned = df_growth_year.dropna(subset=['Growth Rate'])

    if not df_growth_year_cleaned.empty:
        fig_growth = px.bar(
            df_growth_year_cleaned.head(50),
            x='Country/Territory',
            y='Growth Rate',
            color='Growth Rate',
            title=f'Population Growth Rate by Country in {int(selected_year)}{exclusion_text}', # Used selected_year
            labels={'Growth Rate': 'Growth Rate (%)'},
            hover_data={'Growth Rate': ':.2%', 'Population': ':,', 'Density (per km²)': ':.2f'}
        )
        fig_growth.update_layout(xaxis={'categoryorder': 'total descending'})
        st.plotly_chart(fig_growth, use_container_width=True)
    else:
        st.info(f"No valid growth rate data available for the year {int(selected_year)}{exclusion_text}.")

    st.markdown("---")

    # --- NEW SECTION: 6. Population vs. Density (Scatter Plot) ---
    st.subheader(f"Population vs. Density Scatter Plot{exclusion_text}")
    st.write("Explore the relationship between a country's total population and its density.")

    # Now uses the globally determined selected_year
    df_pop_density_scatter = df_population_filtered[df_population_filtered['Year'] == selected_year].copy()
    df_pop_density_scatter.dropna(subset=['Population', 'Density (per km²)'], inplace=True)

    if not df_pop_density_scatter.empty:
        fig_pop_density = px.scatter(
            df_pop_density_scatter,
            x='Population',
            y='Density (per km²)',
            size='Population',
            color='Country/Territory',
            hover_name='Country/Territory',
            log_x=True,
            log_y=True,
            title=f'Population vs. Density in {int(selected_year)}{exclusion_text}', # Used selected_year
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
        fig_pop_density.update_traces(marker=dict(sizemin=3))
        st.plotly_chart(fig_pop_density, use_container_width=True)
    else:
        st.info(
            f"No data available for Population vs. Density for the year {int(selected_year)}{exclusion_text}.")

    st.markdown("---")

    ## World population heatmap
    st.subheader(f"World Population Density Heatmap ({int(selected_year)}){exclusion_text}")
    st.write("Visualize global population density by country. Countries with missing data will be uncolored.")

    # Prepare data for density map - do NOT dropna on 'Density (per km²)' or 'CCA3' here
    df_map_density = df_population_filtered[df_population_filtered['Year'] == selected_year].copy()

    # Ensure essential columns exist for mapping
    if not df_map_density.empty and 'Density (per km²)' in df_map_density.columns and 'CCA3' in df_map_density.columns:
        fig_density_map = px.choropleth(
            df_map_density,
            locations='CCA3',
            color='Density (per km²)',
            hover_name='Country/Territory',
            color_continuous_scale=px.colors.sequential.Viridis,  # Another suitable sequential color scale
            title=f'World Population Density Distribution in {int(selected_year)}{exclusion_text}',
            projection='natural earth',
            labels={'Density (per km²)': 'Density (per km²)'},
            hover_data={'Population': ':,', 'Area (km²)': ':,', 'Density (per km²)': ':.2f'},
            range_color='logarithmic'
        )
        # Add a light blue ocean and blue lakes/rivers for better aesthetics
        fig_density_map.update_geos(
            showland=True, showocean=True, oceancolor="LightBlue",
            showlakes=True, lakecolor="Blue", showrivers=True, rivercolor="Blue"
        )
        st.plotly_chart(fig_density_map, use_container_width=True)
    else:
        st.info(
            f"No sufficient data available for World Population Density Heatmap for the year {int(selected_year)}{exclusion_text}.")

    st.markdown("---")