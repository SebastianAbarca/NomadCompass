import streamlit as st
import plotly.express as px
import pandas as pd
from ..util import util

def nha_indicators_page():
    df_nha_indicators = util.load_data('data/NHA_indicators_PPP.csv')
    st.header('National Health Accounts Indicators')
    st.write("This section displays National Health Accounts indicators and their trends.")

    if not df_nha_indicators.empty:
        # Filter out rows with NaN in 'Value' for display and selectors
        df_nha_display = df_nha_indicators.dropna(subset=['Value']).copy()

        st.subheader("Raw Data Sample (Non-Null Values)")
        st.dataframe(df_nha_display.head())  # Display head of filtered data

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
            key='line_indicator_select'  # Unique key for this selectbox
        )

        selected_nha_countries_line = st.multiselect(
            'Select Countries for Line Chart',
            all_nha_countries,
            default=all_nha_countries[:5]  # Default to first 5 countries
        )

        if selected_nha_indicator_line and selected_nha_countries_line:
            filtered_df_line = df_nha_display[  # Use df_nha_display
                (df_nha_display['Indicators'] == selected_nha_indicator_line) &
                (df_nha_display['Countries'].isin(selected_nha_countries_line))
                ].sort_values(by='Year')  # dropna already done by df_nha_display

            if not filtered_df_line.empty:
                fig_line = px.line(
                    filtered_df_line,
                    x='Year',
                    y='Value',
                    color='Countries',
                    title=f'{selected_nha_indicator_line} Trend for Selected Countries',
                    labels={'Value': selected_nha_indicator_line, 'Year': 'Year'},
                    markers=True  # Show markers on the line
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

        # CHANGE: Allow multiple countries for animated scatter plot
        selected_nha_countries_scatter = st.multiselect(
            'Select Countries for Animated Scatter Plot',
            all_nha_countries,
            default=all_nha_countries[:3],  # Default to a few countries for demonstration
            key='scatter_countries_select'  # Changed key
        )

        if selected_nha_indicator_x and selected_nha_indicator_y and selected_nha_countries_scatter:
            # Prepare data for scatter plot with multiple countries
            # Filter df_nha_display for selected indicators AND selected countries
            df_filtered_x = df_nha_display[
                (df_nha_display['Indicators'] == selected_nha_indicator_x) &
                (df_nha_display['Countries'].isin(selected_nha_countries_scatter))
                ].rename(columns={'Value': 'X_Value'})[
                ['Year', 'Countries', 'X_Value']]  # Include 'Countries' for animation_group

            df_filtered_y = df_nha_display[
                (df_nha_display['Indicators'] == selected_nha_indicator_y) &
                (df_nha_display['Countries'].isin(selected_nha_countries_scatter))
                ].rename(columns={'Value': 'Y_Value'})[['Year', 'Countries', 'Y_Value']]  # Include 'Countries'

            # Merge on 'Year' and 'Countries'
            df_scatter = pd.merge(df_filtered_x, df_filtered_y, on=['Year', 'Countries'], how='inner').dropna()

            if not df_scatter.empty:
                # Ensure 'Year' is sorted for animation
                df_scatter_sorted = df_scatter.sort_values(by='Year')

                fig_scatter = px.scatter(
                    df_scatter_sorted,
                    x='X_Value',
                    y='Y_Value',
                    animation_frame='Year',
                    animation_group='Countries',  # Now 'Countries' column is present in df_scatter_sorted
                    color='Countries',  # Color by country to distinguish paths
                    size='X_Value',
                    hover_name='Countries',  # Show country name on hover
                    color_discrete_sequence=px.colors.qualitative.Plotly,
                    title=f'Relationship between {selected_nha_indicator_x} and {selected_nha_indicator_y} over Time',
                    labels={'X_Value': selected_nha_indicator_x, 'Y_Value': selected_nha_indicator_y},
                    range_x=[df_scatter_sorted['X_Value'].min() * 0.9, df_scatter_sorted['X_Value'].max() * 1.1],
                    range_y=[df_scatter_sorted['Y_Value'].min() * 0.9, df_scatter_sorted['Y_Value'].max() * 1.1]
                )

                # Set animation speed
                fig_scatter.layout.updatemenus[0].buttons[0].args[1]['frame']['duration'] = 1000
                fig_scatter.layout.updatemenus[0].buttons[0].args[1]['transition']['duration'] = 500

                # --- IMPORTANT: Add the trail effect ---
                fig_scatter.update_traces(
                    mode='lines+markers',  # Ensure lines are drawn
                    line=dict(width=5),  # Adjust line thickness
                    marker=dict(size=10)  # Adjust marker size
                )
                fig_scatter.layout.updatemenus[0].buttons[0].args[1]["frame"]["redraw"] = True  # Force redraw for trail

                st.plotly_chart(fig_scatter, use_container_width=True)
            else:
                st.info(
                    "No common data available for the selected indicators and countries to create the animated scatter plot.")
        else:
            st.info("Please select two indicators and at least one country for the animated scatter plot.")

        # --- Visualization 3: Bar Chart - Indicator by Country for a Specific Year (MOVED TO BOTTOM) ---
        st.subheader("3. Health Expenditure by Country for a Specific Year")  # Renumbered to 3

        selected_nha_indicator_bar = st.selectbox(
            'Select Indicator for Bar Chart',
            nha_indicators_list,
            index=nha_indicators_list.index(
                'Current health expenditure (CHE) as percentage of GDP') if 'Current health expenditure (CHE) as percentage of GDP' in nha_indicators_list else 0,
            key='bar_indicator_select'  # Unique key for this selectbox
        )
        selected_nha_year_bar = st.selectbox(
            'Select Year for Bar Chart',
            nha_years_list,
            index=len(nha_years_list) - 1 if nha_years_list else 0,  # Default to latest year
            key='bar_year_select'  # Unique key for this selectbox
        )

        if selected_nha_indicator_bar and selected_nha_year_bar:
            filtered_df_bar = df_nha_display[  # Use df_nha_display
                (df_nha_display['Indicators'] == selected_nha_indicator_bar) &
                (df_nha_display['Year'] == selected_nha_year_bar)
                ].sort_values(by='Value', ascending=False)  # dropna already done by df_nha_display

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

    else:
        st.warning("NHA Indicators data is not available or failed to load.")