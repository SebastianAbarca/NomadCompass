import streamlit as st
import pandas as pd
from app.util import util
from app.util import nha_indicators_graphs # Import the new graphs module
import numpy as np



df_nha_indicators = util.load_data('../../data/NHA_indicators_PPP.csv')
st.header('National Health Accounts Indicators')
st.write("This section displays National Health Accounts indicators and their trends.")

# This is the main check: if the NHA data loaded successfully
if not df_nha_indicators.empty:
    df_nha_display = df_nha_indicators.dropna(subset=['Value']).copy()

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
            fig_line = nha_indicators_graphs.plot_nha_line_chart(filtered_df_line, selected_nha_indicator_line)
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
            fig_scatter = nha_indicators_graphs.plot_nha_animated_scatter(
                df_scatter_sorted, selected_nha_indicator_x, selected_nha_indicator_y
            )
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
            fig_bar = nha_indicators_graphs.plot_nha_bar_chart(
                filtered_df_bar, selected_nha_indicator_bar, selected_nha_year_bar
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("No data available for the selected indicator and year.")

    # --- Visualization 4: Health Expenditure Breakdown for a Country Over Time (Stacked Bar Chart) ---
    st.markdown("---")
    st.subheader("4. Health Expenditure Breakdown for a Country Over Time (Stacked Bar Chart)")
    st.write(
        "This chart visualizes the contribution of different health indicators to a specific country's health expenditure over time.")

    selected_nha_country_stacked = st.selectbox(
        'Select a Country for Breakdown',
        all_nha_countries,
        index=all_nha_countries.index('United States') if 'United States' in all_nha_countries else 0,
        key='stacked_country_select'
    )


    default_stacked_indicators = []
    if 'Current health expenditure (CHE) per capita' in nha_indicators_list:
        default_stacked_indicators.append('Current health expenditure (CHE) per capita')
    if 'Domestic general government health expenditure (GGHE-D) per capita' in nha_indicators_list:
        default_stacked_indicators.append('Domestic general government health expenditure (GGHE-D) per capita')
    if 'Out-of-pocket (OOP) expenditure per capita' in nha_indicators_list:
        default_stacked_indicators.append('Out-of-pocket (OOP) expenditure per capita')

    if not default_stacked_indicators and len(nha_indicators_list) > 0:
        default_stacked_indicators = nha_indicators_list[:3]

    selected_nha_indicators_stacked = st.multiselect(
        'Select Indicators to Stack',
        nha_indicators_list,
        default=default_stacked_indicators,
        key='stacked_indicators_select'
    )

    if selected_nha_country_stacked and selected_nha_indicators_stacked:
        filtered_df_stacked = df_nha_display[
            (df_nha_display['Countries'] == selected_nha_country_stacked) &
            (df_nha_display['Indicators'].isin(selected_nha_indicators_stacked))
            ].copy()

        if not filtered_df_stacked.empty:
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
            fig_stacked_bar = nha_indicators_graphs.plot_nha_stacked_bar_chart(
                filtered_df_stacked, selected_nha_country_stacked
            )
            st.plotly_chart(fig_stacked_bar, use_container_width=True)
        else:
            st.info("No data available for the selected country and indicators for the stacked bar chart.")
    else:
        st.info("Please select a country and at least one indicator for the stacked bar chart.")

        # --- NEW Visualization 5: Top/Bottom N Countries Comparison ---
    st.markdown("---")
    st.subheader("5. Top/Bottom Countries Comparison for a Selected Indicator")
    st.write("Identify the leading or lagging countries for a specific health indicator in a given year.")

    col_viz5_a, col_viz5_b, col_viz5_c = st.columns(3)

    with col_viz5_a:
        selected_nha_indicator_top_n = st.selectbox(
            'Select Indicator for Top/Bottom Comparison',
            nha_indicators_list,
            index=nha_indicators_list.index(
                'Current health expenditure (CHE) per capita') if 'Current health expenditure (CHE) per capita' in nha_indicators_list else 0,
            key='top_n_indicator_select'
        )
    with col_viz5_b:
        selected_nha_year_top_n = st.selectbox(
            'Select Year for Top/Bottom Comparison',
            nha_years_list,
            index=len(nha_years_list) - 1 if nha_years_list else 0,
            key='top_n_year_select'
        )
    with col_viz5_c:
        num_countries_top_n = st.slider(
            'Number of Countries to Show',
            min_value=5,
            max_value=min(20, len(all_nha_countries)),  # Cap max at 20 or available countries
            value=10,
            step=1,
            key='top_n_slider'
        )

    top_bottom_choice = st.radio(
        "Show:",
        ('Top Countries', 'Bottom Countries'),
        key='top_bottom_radio',
        horizontal=True
    )

    if selected_nha_indicator_top_n and selected_nha_year_top_n and num_countries_top_n:
        df_top_n_filtered = df_nha_display[
            (df_nha_display['Indicators'] == selected_nha_indicator_top_n) &
            (df_nha_display['Year'] == selected_nha_year_top_n)
            ].dropna(subset=['Value']).copy()  # Ensure no NaN values affect sorting

        if not df_top_n_filtered.empty:
            if top_bottom_choice == 'Top Countries':
                df_sorted_top_n = df_top_n_filtered.sort_values(by='Value', ascending=False).head(
                    num_countries_top_n)
                chart_title_prefix = "Top"
            else:  # Bottom Countries
                df_sorted_top_n = df_top_n_filtered.sort_values(by='Value', ascending=True).head(
                    num_countries_top_n)
                chart_title_prefix = "Bottom"

            if not df_sorted_top_n.empty:
                fig_top_n_bar = nha_indicators_graphs.plot_nha_top_bottom_bar_chart(
                    df_sorted_top_n, selected_nha_indicator_top_n, selected_nha_year_top_n, chart_title_prefix
                )
                st.plotly_chart(fig_top_n_bar, use_container_width=True)
            else:
                st.info(f"No sufficient data to show {top_bottom_choice} for the selected criteria.")
        else:
            st.info("No data available for the selected indicator and year to perform the comparison.")
    else:
        st.info("Please select an indicator, year, and number of countries for comparison.")
