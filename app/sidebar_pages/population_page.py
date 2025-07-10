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
    AVAILABLE_YEARS.sort()  # Ensure they are sorted for the pills display

    if AVAILABLE_YEARS:
        selected_year = AVAILABLE_YEARS[-1]
    else:
        selected_year = 2022
        st.error("Error: No available years defined for population data. Defaulting to 2022.")
        return

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

    if 'Year' in df_population_filtered.columns:
        df_population_filtered['Year'] = pd.to_numeric(df_population_filtered['Year'], errors='coerce')
        df_population_filtered.dropna(subset=['Year'], inplace=True)

    df_population_filtered = df_population_filtered[df_population_filtered['Year'].isin(AVAILABLE_YEARS)]

    if df_population_filtered.empty:
        st.warning("No valid data remaining after applying global filters and filtering for available years.")
        return

    exclusion_text = ""
    if exclude_countries_global:
        exclusion_text = f" (Excluding {', '.join(exclude_countries_global)})"
    # --- END GLOBAL FILTER ---

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

    # 1. Population Trend Over Years for Selected Countries
    st.subheader(f"Population Trends by Country and Year{exclusion_text}")

    countries = sorted(df_population_filtered['Country/Territory'].unique())
    selected_countries_trend = st.multiselect(
        "Select Countries to Compare Population Trends:",
        options=countries,
        default=countries[:5] if len(countries) >= 5 else countries,
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
        if pd.isna(selected_year):
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
    st.subheader(f"Population Density vs. Area ({selected_year}){exclusion_text}")
    st.write("Examine the relationship between a country's area and its population density.")

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
            title=f'Population Density vs. Area for {int(selected_year)}{exclusion_text}',
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

    # 3b. Population Density vs. Area (Outliers Removed)
    st.subheader(f"Population Density vs. Area (Top 5 Density Outliers Removed - {int(selected_year)}){exclusion_text}")
    st.write(
        "This plot excludes the 5 countries with the highest population density to better show patterns among others.")

    df_density_year_filtered_outliers = df_population_filtered[df_population_filtered['Year'] == selected_year].copy()
    df_density_year_filtered_outliers.dropna(subset=['Area (km²)', 'Density (per km²)', 'Population'], inplace=True)

    if not df_density_year_filtered_outliers.empty:
        n_outliers_to_remove = st.slider("Number of Outliers to remove", min_value=1,
                                         max_value=min(10, len(df_density_year_filtered_outliers) - 1), value=5,
                                         key="num_outliers_slider")
        if n_outliers_to_remove == 0:
            st.info("Please select a number greater than 0 for outliers to remove.")
        else:
            df_density_year_filtered_outliers = df_density_year_filtered_outliers.sort_values(
                by='Density (per km²)', ascending=False
            ).iloc[n_outliers_to_remove:].copy()

            if df_density_year_filtered_outliers.empty:
                st.info("No data remaining after removing top outliers. Try reducing the number of outliers to remove.")
            else:
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
                    title=f'Population Density vs. Area in {int(selected_year)}{exclusion_text} (Top {n_outliers_to_remove} Density Outliers Removed)',
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
                'Year': selected_year,
                'CCA3': 'OTH',
                'Rank': np.nan, 'Area (km²)': np.nan, 'Density (per km²)': np.nan, 'Growth Rate': np.nan,
                'World Population Percentage Rank': np.nan
            }
            df_large_share = pd.concat([df_large_share, pd.DataFrame([new_row])], ignore_index=True)

        fig_percentage = px.pie(
            df_large_share,
            values='World Population Percentage',
            names='Country/Territory',
            title=f'World Population Share by Country in {int(selected_year)}{exclusion_text}',
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
    st.write(f"Visualize the population growth rates across different countries for {int(selected_year)}.")

    df_growth_year = df_population_filtered[df_population_filtered['Year'] == selected_year].copy()
    df_growth_year_cleaned = df_growth_year.dropna(subset=['Growth Rate'])

    if not df_growth_year_cleaned.empty:
        fig_growth = px.bar(
            df_growth_year_cleaned.head(50),
            x='Country/Territory',
            y='Growth Rate',
            color='Growth Rate',
            title=f'Population Growth Rate by Country in {int(selected_year)}{exclusion_text}',
            labels={'Growth Rate': 'Growth Rate (%)'},
            hover_data={'Growth Rate': ':.2%', 'Population': ':,', 'Density (per km²)': ':.2f'}
        )
        fig_growth.update_layout(xaxis={'categoryorder': 'total descending'})
        st.plotly_chart(fig_growth, use_container_width=True)
    else:
        st.info(f"No valid growth rate data available for the year {int(selected_year)}{exclusion_text}.")

    st.markdown("---")

    # 6. Population vs. Density (Scatter Plot)
    st.subheader(f"Population vs. Density Scatter Plot{exclusion_text}")
    st.write("Explore the relationship between a country's total population and its density.")

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
        fig_pop_density.update_traces(marker=dict(sizemin=3))
        st.plotly_chart(fig_pop_density, use_container_width=True)
    else:
        st.info(
            f"No data available for Population vs. Density for the year {int(selected_year)}{exclusion_text}.")

    st.markdown("---")

    # 7. World Population Heatmap
    st.subheader(f"World Population Heatmap ({int(selected_year)}){exclusion_text}")
    st.write("Visualize global population distribution by country. Countries with missing data will be uncolored.")

    df_map_population = df_population_filtered[df_population_filtered['Year'] == selected_year].copy()

    if not df_map_population.empty and 'Population' in df_map_population.columns and 'CCA3' in df_map_population.columns:
        fig_population_map = px.choropleth(
            df_map_population,
            locations='CCA3',
            color='Population',
            hover_name='Country/Territory',
            color_continuous_scale=px.colors.sequential.Plasma,
            title=f'World Population Distribution in {int(selected_year)}{exclusion_text}',
            projection='natural earth',
            labels={'Population': 'Population'},
            hover_data={'Population': ':,', 'Area (km²)': ':,', 'Density (per km²)': ':.2f'}
        )
        fig_population_map.update_geos(
            showland=True, showocean=True, oceancolor="LightBlue",
            showlakes=True, lakecolor="Blue", showrivers=True, rivercolor="Blue"
        )
        st.plotly_chart(fig_population_map, use_container_width=True)
    else:
        st.info(
            f"No sufficient data available for World Population Heatmap for the year {int(selected_year)}{exclusion_text}.")

    st.markdown("---")

    # 8. World Population Density Heatmap (Manually Log-Scaled)
    st.subheader(f"World Population Density Heatmap ({int(selected_year)}){exclusion_text}")
    st.write(
        "Visualize global population density by country. Colors are on a **logarithmic scale** for better expressiveness. Countries with missing or zero density data will be uncolored.")

    df_map_density = df_population_filtered[df_population_filtered['Year'] == selected_year].copy()

    # --- MANUAL LOG TRANSFORMATION ---
    df_map_density['Density (per km²)'] = pd.to_numeric(df_map_density['Density (per km²)'], errors='coerce')

    # Replace 0s with NaN for log transformation, and apply a small offset for very small positive values if desired
    # For choropleth, if a value is NaN, the country will be uncolored, which is good for 0 density.
    df_map_density['Density_Log10'] = df_map_density['Density (per km²)'].apply(
        lambda x: np.log10(x) if x > 0 else np.nan
    )

    # Drop rows where 'CCA3' or the new log-transformed density became NaN
    df_map_density.dropna(subset=['CCA3', 'Density_Log10'], inplace=True)
    # --- END MANUAL LOG TRANSFORMATION ---

    if not df_map_density.empty:
        # Determine the min/max of the log-transformed data for the color scale legend.
        # This will make the color bar show log values.
        min_log_density = df_map_density['Density_Log10'].min()
        max_log_density = df_map_density['Density_Log10'].max()

        # If you still want to cap the *visual* range to a maximum original value (e.g., 500)
        # after log transform, you can set color_continuous_max to log10(500).
        # Otherwise, let it scale to the max log value in your data.

        # Example if you want to cap at original 500 density:
        # capped_log_max = np.log10(500) if max_log_density > np.log10(500) else max_log_density

        fig_density_map = px.choropleth(
            df_map_density,
            locations='CCA3',
            color='Density_Log10',  # Use the manually log-transformed column
            hover_name='Country/Territory',
            color_continuous_scale=px.colors.sequential.Viridis,
            title=f'World Population Density Distribution in {int(selected_year)}{exclusion_text} (Logarithmic Scale)',
            projection='natural earth',
            # Labels for the color bar and hover info
            labels={'Density_Log10': 'Density (log10)'},
            # Crucially, show original density in hover for context
            hover_data={
                'Population': ':,',
                'Area (km²)': ':,',
                'Density (per km²)': ':.2f',  # Show original density here
                'Density_Log10': ':.2f'  # Show log density here for debugging/understanding
            },
            # Optional: Set a continuous color range using the log-transformed values if desired
            # For instance, if you want the color bar to span log10(1) to log10(500)
            # color_continuous_range=[np.log10(1), np.log10(500)]
        )
        fig_density_map.update_geos(
            showland=True, showocean=True, oceancolor="LightBlue",
            showlakes=True, lakecolor="Blue", showrivers=True, rivercolor="Blue"
        )
        st.plotly_chart(fig_density_map, use_container_width=True)
    else:
        st.info(
            f"No sufficient data available for World Population Density Heatmap for the year {int(selected_year)}{exclusion_text}.")

    st.markdown("---")