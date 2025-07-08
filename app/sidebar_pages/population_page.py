from ..util import util
import pandas as pd
import streamlit as st
import plotly.express as px


df_population = util.load_data('data/world_population_data.csv')

def population_page():
    st.sidebar.title("Population Data Insights")

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

    exclusion_text = ""
    if exclude_countries_global:
        exclusion_text = f" (Excluding {', '.join(exclude_countries_global)})"
    # --- END GLOBAL FILTER ---

    # Display the raw dataframe (optional, good for initial inspection)
    with st.expander("View Raw Population Data"):
        st.dataframe(df_population_filtered)  # Display filtered data
        st.write("Columns available for analysis:", df_population_filtered.columns.tolist())

    st.markdown("---")

    # 1. Population Trend Over Years for Selected Countries
    st.subheader(f"Population Trends by Country and Year{exclusion_text}")

    # Ensure 'Year' is treated as a numerical type for sorting
    # This check and conversion should ideally happen once after loading and before filtering if Year is critical for all subsequent steps.
    # But since it's already done globally, we apply it to the filtered DF now.
    if 'Year' in df_population_filtered.columns:
        df_population_filtered['Year'] = pd.to_numeric(df_population_filtered['Year'], errors='coerce')
        df_population_filtered.dropna(subset=['Year'], inplace=True)  # Drop rows where Year couldn't be converted

    countries = sorted(df_population_filtered['Country/Territory'].unique())
    selected_countries_trend = st.multiselect(
        "Select Countries to Compare Population Trends:",
        options=countries,
        default=countries[:5] if len(countries) >= 5 else countries,  # Default to top 5 or all if less
        key="trend_countries_selector"  # Added unique key
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
                hover_data={'Population': ':,', 'Year': True}  # Format population with commas
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
        latest_year = df_population_filtered['Year'].max()
        if pd.isna(latest_year):  # Check if max() returned NaN, meaning df_population_filtered is empty for 'Year'
            st.info("No valid years found in the filtered dataset for 'Top Countries by Population'.")
            return

        st.write(f"Showing data for the latest available year: **{int(latest_year)}**")

        df_latest_year = df_population_filtered[df_population_filtered['Year'] == latest_year].sort_values(
            by='Population', ascending=False)
        top_n = st.slider("Select number of top countries:", min_value=1, max_value=min(50, len(df_latest_year)),
                          value=min(10, len(df_latest_year)))  # Adjust max_value dynamically
        if top_n == 0:  # Handle case where slider min value is 0 and no data
            st.info("Please select a number greater than 0 for top countries.")
            return

        if not df_latest_year.empty:
            fig_top_population = px.bar(
                df_latest_year.head(top_n),
                x='Country/Territory',
                y='Population',
                color='Population',
                title=f'Top {top_n} Countries by Population in {int(latest_year)}{exclusion_text}',
                labels={'Population': 'Population', 'Country/Territory': 'Country'},
                hover_data={'Population': ':,', 'Area (km²)': ':,', 'Density (per km²)': ':.2f'}
            )
            fig_top_population.update_layout(xaxis={'categoryorder': 'total descending'})
            st.plotly_chart(fig_top_population, use_container_width=True)
        else:
            st.info(f"No population data found for the year {int(latest_year)} after filters.")
    else:
        st.warning(
            "Required columns ('Year', 'Population') not found in the dataset for 'Top Countries by Population' visualization after filters.")

    st.markdown("---")

    # 3. Population Density vs. Area (Scatter Plot)
    st.subheader(f"Population Density vs. Area{exclusion_text}")
    st.write("Examine the relationship between a country's area and its population density.")

    if df_population_filtered['Year'].empty:
        st.info("No valid years available in the filtered dataset for Density vs. Area analysis.")
        return

    year_density = st.slider(
        "Select Year for Density vs. Area:",
        min_value=int(df_population_filtered['Year'].min()),
        max_value=int(df_population_filtered['Year'].max()),
        value=int(df_population_filtered['Year'].max()),
        step=1,
        key="density_year_slider"  # Added unique key
    )

    df_density_year = df_population_filtered[df_population_filtered['Year'] == year_density]

    if not df_density_year.empty:
        fig_density = px.scatter(
            df_density_year,
            x='Area (km²)',
            y='Density (per km²)',
            size='Population',  # Size of marker based on population
            color='Country/Territory',
            hover_name='Country/Territory',
            log_x=True,  # Area can vary widely, log scale helps
            title=f'Population Density vs. Area for {int(year_density)}{exclusion_text}',
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
        st.plotly_chart(fig_density, use_container_width=True)
    else:
        st.info(f"No data available for Population Density vs. Area for the year {int(year_density)}{exclusion_text}.")

    st.markdown("---")

    # 4. World Population Percentage (Pie Chart for a specific year)
    st.subheader(f"World Population Share by Country{exclusion_text}")

    if df_population_filtered['Year'].empty:
        st.info("No valid years available in the filtered dataset for World Population Percentage analysis.")
        return

    year_percentage = st.slider(
        "Select Year for World Population Percentage:",
        min_value=int(df_population_filtered['Year'].min()),
        max_value=int(df_population_filtered['Year'].max()),
        value=int(df_population_filtered['Year'].max()),
        step=1,
        key='percentage_year_slider'  # Unique key for this slider
    )

    df_percentage_year = df_population_filtered[df_population_filtered['Year'] == year_percentage].sort_values(
        by='World Population Percentage', ascending=False)

    if not df_percentage_year.empty:
        # We might want to combine smaller percentages into "Other" for better readability
        # Define a threshold for "Other" category (e.g., countries with < 1% of world population)
        threshold = 1.0  # percentage
        df_large_share = df_percentage_year[df_percentage_year['World Population Percentage'] >= threshold].copy()
        df_other = df_percentage_year[df_percentage_year['World Population Percentage'] < threshold].copy()

        if not df_other.empty:
            other_percentage = df_other['World Population Percentage'].sum()
            other_population = df_other['Population'].sum()
            df_large_share.loc[len(df_large_share)] = {
                'Country/Territory': 'Other Countries',
                'World Population Percentage': other_percentage,
                'Population': other_population,
                'Year': year_percentage,
                'CCA3': 'OTH'  # Placeholder
            }
            # Fill other columns to avoid NaN if they are used elsewhere
            df_large_share['Rank'] = df_large_share['Rank'].fillna(0)
            df_large_share['Area (km²)'] = df_large_share['Area (km²)'].fillna(0)
            df_large_share['Density (per km²)'] = df_large_share['Density (per km²)'].fillna(0)
            df_large_share['Growth Rate'] = df_large_share['Growth Rate'].fillna(0)

        fig_percentage = px.pie(
            df_large_share,
            values='World Population Percentage',
            names='Country/Territory',
            title=f'World Population Share by Country in {int(year_percentage)}{exclusion_text}',
            hover_data={'Population': ':,', 'World Population Percentage': ':.2f%'},
            labels={'World Population Percentage': 'Share (%)'}
        )
        fig_percentage.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_percentage, use_container_width=True)
    else:
        st.info(f"No data available for World Population Share for the year {int(year_percentage)}{exclusion_text}.")

    st.markdown("---")

    # 5. Population Growth Rate (Bar Chart)
    st.subheader(f"Population Growth Rate by Country{exclusion_text}")
    st.write("Visualize the population growth rates across different countries for a selected year.")

    if df_population_filtered['Year'].empty:
        st.info("No valid years available in the filtered dataset for Growth Rate analysis.")
        return

    year_growth = st.slider(
        "Select Year for Growth Rate:",
        min_value=int(df_population_filtered['Year'].min()),
        max_value=int(df_population_filtered['Year'].max()),
        value=int(df_population_filtered['Year'].max()),
        step=1,
        key='growth_rate_year_slider'  # Unique key
    )

    df_growth_year = df_population_filtered[df_population_filtered['Year'] == year_growth].copy()

    # Filter out NaN or extremely high/low growth rates that might skew the visualization
    df_growth_year_cleaned = df_growth_year.dropna(subset=['Growth Rate'])
    # Optional: set a reasonable range for growth rate display if outliers are present
    # df_growth_year_cleaned = df_growth_year_cleaned[
    #     (df_growth_year_cleaned['Growth Rate'] > -0.05) &
    #     (df_growth_year_cleaned['Growth Rate'] < 0.05)
    # ]

    if not df_growth_year_cleaned.empty:
        fig_growth = px.bar(
            df_growth_year_cleaned.head(50),  # Show top 50 countries by growth rate, or all if less
            x='Country/Territory',
            y='Growth Rate',
            color='Growth Rate',
            title=f'Population Growth Rate by Country in {int(year_growth)}{exclusion_text}',
            labels={'Growth Rate': 'Growth Rate (%)'},
            hover_data={'Growth Rate': ':.2%', 'Population': ':,', 'Density (per km²)': ':.2f'}
        )
        fig_growth.update_layout(xaxis={'categoryorder': 'total descending'})
        st.plotly_chart(fig_growth, use_container_width=True)
    else:
        st.info(f"No valid growth rate data available for the year {int(year_growth)}{exclusion_text}.")
