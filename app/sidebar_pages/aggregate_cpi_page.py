import streamlit as st
import pandas as pd
import plotly.express as px
from app.util import util
from data.etl import cpi_api_download


def aggregate_cpi_page():
    st.header("Aggregate CPI Data")
    df_aggregate_cpi = cpi_api_download.cpi_api_data()
    df_aggregate_cpi['OBS_VALUE'] = pd.to_numeric(df_aggregate_cpi['OBS_VALUE'], errors='coerce')
    df_aggregate_cpi.dropna(subset=['OBS_VALUE'], inplace=True)
    df_aggregate_cpi['COUNTRY_NAME'] = df_aggregate_cpi['COUNTRY'].apply(util.get_country_name)
    df_population = util.load_data('data/world_population_data.csv')

    if df_aggregate_cpi.empty:
        st.warning("Aggregate CPI data not loaded.")
    else:
        # --- Data Preprocessing for CPI ---
        df_cpi = df_aggregate_cpi.copy()

        # Safely convert 'TIME_PERIOD' to PeriodIndex for proper quarterly handling
        try:
            # Assuming 'TIME_PERIOD' is directly like '2020Q1', '2020Q2', etc.
            df_cpi['TIME_PERIOD_PERIOD'] = pd.PeriodIndex(df_cpi['TIME_PERIOD'], freq='Q')
        except Exception as e:
            st.error(
                f"Error converting CPI TIME_PERIOD to a PeriodIndex: {e}. Please ensure it's in 'YYYYQn' format (e.g., '2020Q1').")

        # Extract Year and Quarter Number using the PeriodIndex accessor
        df_cpi['Year'] = df_cpi['TIME_PERIOD_PERIOD'].dt.year
        df_cpi['Q_Num'] = df_cpi['TIME_PERIOD_PERIOD'].dt.quarter

        # Convert PeriodIndex to Timestamp for Plotly (Plotly prefers datetime objects)
        df_cpi['Time'] = df_cpi['TIME_PERIOD_PERIOD'].dt.to_timestamp()
        df_cpi = df_cpi.sort_values(['COUNTRY_NAME', 'Time'])

        # Calculate Year-over-Year (YoY) % change
        # Ensure data is sorted for correct pct_change calculation within each country group
        df_cpi['YoY_change'] = df_cpi.groupby('COUNTRY_NAME')['OBS_VALUE'].pct_change(periods=4) * 100

        # --- CPI Over Time Visualization ---
        st.subheader("CPI Over Time by Country")
        countries = df_cpi['COUNTRY_NAME'].unique()
        selected_countries = st.multiselect(
            "Select one or more countries to visualize CPI over time:",
            options=sorted(countries),
            default=['Aruba']
        )

        if selected_countries:
            df_filtered_plot = df_cpi[df_cpi['COUNTRY_NAME'].isin(selected_countries)].copy()

            fig_cpi_time = px.line(
                df_filtered_plot,
                x='Time',
                y='OBS_VALUE',
                color='COUNTRY_NAME',
                markers=True,
                labels={'Time': 'Quarter', 'OBS_VALUE': 'CPI Value'},
                title='Aggregate CPI Over Time by Country',
                template='plotly_white'
            )
            fig_cpi_time.update_layout(hovermode='x unified', title_font_size=20)
            st.plotly_chart(fig_cpi_time, use_container_width=True)
        else:
            st.info("Please select at least one country to display the CPI over time chart.")

        # --- CPI Stability Analysis ---
        st.subheader("Top 10 Most Stable Countries (Lowest CPI Volatility)")

        # --- Prepare Population Data for Merging ---
        df_pop_processed = df_population.copy()
        if 'Country/Territory' in df_pop_processed.columns:
            df_pop_processed.rename(columns={'Country/Territory': 'COUNTRY_NAME'}, inplace=True)
        else:
            st.warning("Population data is missing 'Country/Territory' column. Cannot merge effectively.")
            df_pop_processed = pd.DataFrame()

        if not df_pop_processed.empty and 'Year' in df_pop_processed.columns and 'Population' in df_pop_processed.columns:
            df_pop_for_merge = df_pop_processed[['COUNTRY_NAME', 'Year', 'Population']].copy()

            # --- Merge CPI data with Population data ---
            df_cpi_with_population = pd.merge(
                df_cpi,
                df_pop_for_merge,
                on=['COUNTRY_NAME', 'Year'],
                how='left'
            )
        else:
            st.warning(
                "Population data is not in the expected format or is empty. Stability analysis will proceed without population filtering.")
            df_cpi_with_population = df_cpi.copy()

        # --- Population Filtering for Stability Analysis ---
        filtered_cpi_df = df_cpi_with_population.copy()

        if 'Population' in filtered_cpi_df.columns and not filtered_cpi_df['Population'].isnull().all():
            min_pop = int(filtered_cpi_df['Population'].min())
            max_pop = int(filtered_cpi_df['Population'].max())

            min_pop_M = min_pop // 1_000_000
            max_pop_M = (max_pop + 999_999) // 1_000_000

            population_range_M = st.slider(
                'Select Population Range (in millions) for Stability Analysis:',
                min_value=min_pop_M,
                max_value=max_pop_M,
                value=(min_pop_M, max_pop_M),
                step=10,
                format='%dM'
            )

            filtered_cpi_df = filtered_cpi_df[
                (filtered_cpi_df['Population'] >= population_range_M[0] * 1_000_000) &
                (filtered_cpi_df['Population'] <= population_range_M[1] * 1_000_000)
                ].copy()
            st.info(
                f"Filtering countries with population between {population_range_M[0]}M and {population_range_M[1]}M.")
        else:
            st.info(
                "Population data not available or incomplete for filtering. Displaying stability for all countries with CPI data.")

        # --- Calculate Stability ---
        if 'YoY_change' not in filtered_cpi_df.columns or filtered_cpi_df['YoY_change'].isnull().all():
            st.warning(
                "YoY_change data not available or is all null after filtering. Cannot calculate stability.")
            stability_df = pd.DataFrame()
        else:
            stability_df = (
                filtered_cpi_df.groupby('COUNTRY_NAME')['YoY_change']
                .std()
                .dropna()
                .sort_values()
                .reset_index()
                .rename(columns={'YoY_change': 'YoY_StdDev'})
            )

        # --- Display Stability Results ---
        if not stability_df.empty:
            top_stable = stability_df.head(10)

            col1, col2 = st.columns([4, 3])
            with col1:
                fig_stab = px.bar(
                    top_stable,
                    x='COUNTRY_NAME',
                    y='YoY_StdDev',
                    text=top_stable['YoY_StdDev'].round(2),
                    labels={'YoY_StdDev': 'Std. Dev of YoY % Change', 'COUNTRY_NAME': 'Country'},
                    title='Top 10 CPI Stable Countries',
                    template='plotly_white'
                )
                fig_stab.update_traces(marker_color='seagreen')
                fig_stab.update_layout(xaxis_title_text='')
                st.plotly_chart(fig_stab, use_container_width=True)

            with col2:
                st.write("### Stability Data Table")
                st.dataframe(top_stable.set_index('COUNTRY_NAME').round(2), use_container_width=True)
        else:
            st.info("Not enough data to calculate CPI stability for the selected population range.")


        #create plot
        # x_axis=population
        #y_axis=aggregate_cpi
        # --- Explore Individual Country CPI ---
        all_countries_merged = sorted(df_cpi_with_population['COUNTRY_NAME'].unique())
        selected_country_agg_explore = st.selectbox('Select a Country to view all its CPI data:',
                                                    all_countries_merged)

        if selected_country_agg_explore:
            country_df_agg_explore = df_cpi_with_population[
                df_cpi_with_population['COUNTRY_NAME'] == selected_country_agg_explore
                ].copy()
            st.write(f"### Detailed CPI Data for {selected_country_agg_explore}")
            st.dataframe(country_df_agg_explore.round(2), use_container_width=True)