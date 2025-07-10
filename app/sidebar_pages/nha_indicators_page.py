import streamlit as st
import plotly.express as px
import pandas as pd
from ..util import util
import numpy as np  # Import numpy for np.nan


def nha_indicators_page():
    df_nha_indicators = util.load_data('data/NHA_indicators_PPP.csv')
    st.header('National Health Accounts Indicators')
    st.write("This section displays National Health Accounts indicators and their trends.")

    if not df_nha_indicators.empty:
        # Filter out rows with NaN in 'Value' for display and selectors
        df_nha_display = df_nha_indicators.dropna(subset=['Value']).copy()

        st.subheader("Raw Data Sample (Non-Null Values)")
        st.dataframe(df_nha_display.head())
        # Get unique indicators and years from the filtered DataFrame for selection
        nha_indicators_list = sorted(df_nha_display['Indicators'].unique())
        nha_years_list = sorted(df_nha_display['Year'].dropna().unique().tolist())
        all_nha_countries = sorted(df_nha_display['Countries'].unique())

        # --- Visualization 1: Line Chart - Indicator Trend for Selected Countries ---
        st.subheader("1. Health Expenditure Trend for Selected Countries")

        selected_nha_indicator_line = st.selectbox(
            'Select Indicator for Line Chart',
            nha_indicators_list,
            index=nha_indicators_list.index(
                'Current health expenditure (CHE) as percentage of GDP') if 'Current health expenditure (CHE) as percentage of GDP' in nha_indicators_list else 0,
            key='line_indicator_select'
        )

        selected_nha_countries_line = st.multiselect(
            'Select Countries for Line Chart',
            all_nha_countries,
            default=all_nha_countries[:5]
        )

        if selected_nha_indicator_line and selected_nha_countries_line:
            filtered_df_line = df_nha_display[
                (df_nha_display['Indicators'] == selected_nha_indicator_line) &
                (df_nha_display['Countries'].isin(selected_nha_countries_line))
                ].sort_values(by='Year')

            if not filtered_df_line.empty:
                fig_line = px.line(
                    filtered_df_line,
                    x='Year',
                    y='Value',
                    color='Countries',
                    title=f'{selected_nha_indicator_line} Trend for Selected Countries',
                    labels={'Value': selected_nha_indicator_line, 'Year': 'Year'},
                    markers=True
                )
                st.plotly_chart(fig_line, use_container_width=True)
            else:
                st.info("No data available for the selected indicator and countries.")

        # --- Visualization 2: Animated Scatter Plot - Relationship between two Indicators over Time ---
        st.subheader("2. Relationship between Two Health Indicators Over Time (Animated)")

        scatter_indicators_list = sorted(df_nha_display['Indicators'].unique())

        col1, col2 = st.columns(2)
        with col1:
            selected_nha_indicator_x = st.selectbox(
                'Select X-axis Indicator',
                scatter_indicators_list,
                index=scatter_indicators_list.index(
                    'Current health expenditure (CHE) as percentage of GDP') if 'Current health expenditure (CHE) as percentage of GDP' in scatter_indicators_list else 0,
                key='scatter_x_indicator'
            )
        with col2:
            selected_nha_indicator_y = st.selectbox(
                'Select Y-axis Indicator',
                scatter_indicators_list,
                index=scatter_indicators_list.index(
                    'Current health expenditure (CHE) per capita') if 'Current health expenditure (CHE) per capita' in scatter_indicators_list else 0,
                key='scatter_y_indicator'
            )

        selected_nha_countries_scatter = st.multiselect(
            'Select Countries for Animated Scatter Plot',
            all_nha_countries,
            default=all_nha_countries[:3],
            key='scatter_countries_select'
        )

        if selected_nha_indicator_x and selected_nha_indicator_y and selected_nha_countries_scatter:
            df_filtered_x = df_nha_display[
                (df_nha_display['Indicators'] == selected_nha_indicator_x) &
                (df_nha_display['Countries'].isin(selected_nha_countries_scatter))
                ].rename(columns={'Value': 'X_Value'})[['Year', 'Countries', 'X_Value']]

            df_filtered_y = df_nha_display[
                (df_nha_display['Indicators'] == selected_nha_indicator_y) &
                (df_nha_display['Countries'].isin(selected_nha_countries_scatter))
                ].rename(columns={'Value': 'Y_Value'})[['Year', 'Countries', 'Y_Value']]

            df_scatter = pd.merge(df_filtered_x, df_filtered_y, on=['Year', 'Countries'], how='inner').dropna()

            if not df_scatter.empty:
                df_scatter_sorted = df_scatter.sort_values(by='Year')

                fig_scatter = px.scatter(
                    df_scatter_sorted,
                    x='X_Value',
                    y='Y_Value',
                    animation_frame='Year',
                    animation_group='Countries',
                    color='Countries',
                    size='X_Value',
                    hover_name='Countries',
                    color_discrete_sequence=px.colors.qualitative.Plotly,
                    title=f'Relationship between {selected_nha_indicator_x} and {selected_nha_indicator_y} over Time',
                    labels={'X_Value': selected_nha_indicator_x, 'Y_Value': selected_nha_indicator_y},
                    range_x=[df_scatter_sorted['X_Value'].min() * 0.9, df_scatter_sorted['X_Value'].max() * 1.1],
                    range_y=[df_scatter_sorted['Y_Value'].min() * 0.9, df_scatter_sorted['Y_Value'].max() * 1.1]
                )

                fig_scatter.layout.updatemenus[0].buttons[0].args[1]['frame']['duration'] = 1000
                fig_scatter.layout.updatemenus[0].buttons[0].args[1]['transition']['duration'] = 500

                fig_scatter.update_traces(
                    mode='lines+markers',
                    line=dict(width=5),
                    marker=dict(size=10)
                )
                fig_scatter.layout.updatemenus[0].buttons[0].args[1]["frame"]["redraw"] = True

                st.plotly_chart(fig_scatter, use_container_width=True)
            else:
                st.info(
                    "No common data available for the selected indicators and countries to create the animated scatter plot.")
        else:
            st.info("Please select two indicators and at least one country for the animated scatter plot.")

        # --- Visualization 3: Bar Chart - Indicator by Country for a Specific Year ---
        st.subheader("3. Health Expenditure by Country for a Specific Year")

        selected_nha_indicator_bar = st.selectbox(
            'Select Indicator for Bar Chart',
            nha_indicators_list,
            index=nha_indicators_list.index(
                'Current health expenditure (CHE) as percentage of GDP') if 'Current health expenditure (CHE) as percentage of GDP' in nha_indicators_list else 0,
            key='bar_indicator_select'
        )
        selected_nha_year_bar = st.selectbox(
            'Select Year for Bar Chart',
            nha_years_list,
            index=len(nha_years_list) - 1 if nha_years_list else 0,
            key='bar_year_select'
        )

        if selected_nha_indicator_bar and selected_nha_year_bar:
            filtered_df_bar = df_nha_display[
                (df_nha_display['Indicators'] == selected_nha_indicator_bar) &
                (df_nha_display['Year'] == selected_nha_year_bar)
                ].sort_values(by='Value', ascending=False)

            if not filtered_df_bar.empty:
                fig_bar = px.bar(
                    filtered_df_bar,
                    x='Countries',
                    y='Value',
                    title=f'{selected_nha_indicator_bar} by Country in {selected_nha_year_bar}',
                    labels={'Value': selected_nha_indicator_bar, 'Countries': 'Country'}
                )
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.info("No data available for the selected indicator and year.")

        # --- NEW Visualization 4: Health Expenditure Breakdown for a Country Over Time (Stacked Bar Chart) ---
        st.markdown("---")
        st.subheader("4. Health Expenditure Breakdown for a Country Over Time (Stacked Bar Chart)")
        st.write(
            "This chart visualizes the contribution of different health indicators to a specific country's health expenditure over time.")

        # Select a single country
        selected_nha_country_stacked = st.selectbox(
            'Select a Country for Breakdown',
            all_nha_countries,
            index=all_nha_countries.index('United States') if 'United States' in all_nha_countries else 0,
            # Default to US or first country
            key='stacked_country_select'
        )

        # Select multiple indicators to stack
        # Default to a few common breakdown indicators if they exist
        default_stacked_indicators = []
        if 'Current health expenditure (CHE) per capita' in nha_indicators_list:
            default_stacked_indicators.append('Current health expenditure (CHE) per capita')
        if 'Domestic general government health expenditure (GGHE-D) per capita' in nha_indicators_list:
            default_stacked_indicators.append('Domestic general government health expenditure (GGHE-D) per capita')
        if 'Out-of-pocket (OOP) expenditure per capita' in nha_indicators_list:
            default_stacked_indicators.append('Out-of-pocket (OOP) expenditure per capita')

        if not default_stacked_indicators and len(nha_indicators_list) > 0:  # Fallback if specific ones not found
            default_stacked_indicators = nha_indicators_list[:3]

        selected_nha_indicators_stacked = st.multiselect(
            'Select Indicators to Stack',
            nha_indicators_list,  # Use the full list of indicators
            default=default_stacked_indicators,
            key='stacked_indicators_select'
        )

        if selected_nha_country_stacked and selected_nha_indicators_stacked:
            filtered_df_stacked = df_nha_display[
                (df_nha_display['Countries'] == selected_nha_country_stacked) &
                (df_nha_display['Indicators'].isin(selected_nha_indicators_stacked))
                ].copy()

            if not filtered_df_stacked.empty:
                # Heuristic to check for unit compatibility and issue a warning if needed
                # This check assumes 'percentage', 'per capita', and 'us$' are main unit types
                units_in_selection = filtered_df_stacked['Indicators'].apply(
                    lambda x: 'percentage' if 'percentage' in x.lower() or '%' in x else \
                        'per capita' if 'per capita' in x.lower() else \
                            'us$' if 'us$' in x.lower() else 'other'
                ).unique()

                if len(selected_nha_indicators_stacked) > 1 and len(units_in_selection) > 1:
                    st.warning(
                        "**Warning:** You have selected indicators with potentially incompatible units "
                        "(e.g., percentages and per capita values). Stacking them directly may result "
                        "in a numerically meaningless sum on the Y-axis. Please interpret with caution, "
                        "or consider selecting indicators with the same units for a clear sum."
                    )

                fig_stacked_bar = px.bar(
                    filtered_df_stacked,
                    x='Year',
                    y='Value',
                    color='Indicators',  # Now color by Indicator to stack them
                    title=f'Health Expenditure Breakdown for {selected_nha_country_stacked} Over Time',
                    labels={'Value': 'Indicator Value', 'Year': 'Year', 'Indicators': 'Indicator'},
                    hover_data={'Value': ':.2f'}
                )
                fig_stacked_bar.update_layout(barmode='stack')  # Explicitly ensure stacking
                st.plotly_chart(fig_stacked_bar, use_container_width=True)
            else:
                st.info("No data available for the selected country and indicators for the stacked bar chart.")
        else:
            st.info("Please select a country and at least one indicator for the stacked bar chart.")

        # --- Visualization 5: Choropleth Map for an Indicator ---
        st.markdown("---")
        st.subheader("5. Global Distribution of Health Indicator (Choropleth Map)")
        st.write("Visualize the geographical distribution of a selected health indicator for a specific year.")

        df_population_for_merge = util.load_data('data/world_population_data.csv')
        df_population_for_merge = df_population_for_merge[['Country/Territory', 'CCA3']].drop_duplicates()

        df_nha_map_data = pd.merge(
            df_nha_display,
            df_population_for_merge,
            left_on='Countries',
            right_on='Country/Territory',
            how='inner'
        )
        df_nha_map_data.drop(columns=['Country/Territory'], inplace=True)

        if not df_nha_map_data.empty:
            selected_nha_indicator_map = st.selectbox(
                'Select Indicator for Map',
                nha_indicators_list,
                index=nha_indicators_list.index(
                    'Current health expenditure (CHE) as percentage of GDP') if 'Current health expenditure (CHE) as percentage of GDP' in nha_indicators_list else 0,
                key='map_indicator_select'
            )

            selected_nha_year_map = st.selectbox(
                'Select Year for Map',
                nha_years_list,
                index=len(nha_years_list) - 1 if nha_years_list else 0,
                key='map_year_select'
            )

            df_map_filtered = df_nha_map_data[
                (df_nha_map_data['Indicators'] == selected_nha_indicator_map) &
                (df_nha_map_data['Year'] == selected_nha_year_map)
                ].copy()

            if not df_map_filtered.empty:
                df_map_filtered['Value_for_Map'] = df_map_filtered['Value'].apply(lambda x: x if x > 0 else np.nan)
                df_map_filtered.dropna(subset=['Value_for_Map'], inplace=True)

                if not df_map_filtered.empty:
                    use_log_scale_for_map = st.checkbox(
                        f"Use logarithmic scale for '{selected_nha_indicator_map}' on map",
                        value=(
                                    'per capita' in selected_nha_indicator_map.lower() or 'us$' in selected_nha_indicator_map.lower()),
                        key='map_log_scale_checkbox'
                    )

                    color_col = 'Value_for_Map'
                    color_label = selected_nha_indicator_map

                    if use_log_scale_for_map:
                        df_map_filtered['Value_for_Map_Log'] = df_map_filtered['Value_for_Map'].apply(
                            lambda x: np.log10(x)
                        )
                        df_map_filtered.dropna(subset=['Value_for_Map_Log'], inplace=True)
                        color_col = 'Value_for_Map_Log'
                        color_label = f'{selected_nha_indicator_map} (log10)'

                    if not df_map_filtered.empty:
                        fig_choropleth = px.choropleth(
                            df_map_filtered,
                            locations='CCA3',
                            color=color_col,
                            hover_name='Countries',
                            color_continuous_scale=px.colors.sequential.Plasma,
                            title=f'{selected_nha_indicator_map} in {selected_nha_year_map}',
                            projection='natural earth',
                            labels={color_col: color_label},
                            hover_data={'Value': ':.2f'}
                        )
                        fig_choropleth.update_geos(
                            showland=True, showocean=True, oceancolor="LightBlue",
                            showlakes=True, lakecolor="Blue", showrivers=True, rivercolor="Blue"
                        )
                        st.plotly_chart(fig_choropleth, use_container_width=True)
                    else:
                        st.info("No valid data remaining for the map after applying the logarithmic scale.")
                else:
                    st.info(
                        "No data available for the selected indicator and year for the map after initial processing.")
            else:
                st.info("No data available for the selected indicator and year to create the map.")
        else:
            st.info(
                "No data available to create the map. Ensure NHA data can be merged with country codes from 'world_population_data.csv'.")

    else:
        st.warning("NHA Indicators data is not available or failed to load.")