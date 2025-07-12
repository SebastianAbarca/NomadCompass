import streamlit as st
import pandas as pd
import plotly.express as px
from app.util import util
from data.etl import imf_granular_cpi_etl

def categorical_cpi_page():
    st.header("Categorical CPI Data")

    df_granular_cpi = imf_granular_cpi_etl.granular_cpi_data()

    if df_granular_cpi.empty:
        st.warning("Granular CPI data could not be loaded. Please check the data source and ETL process.")
        return

    if 'COUNTRY' in df_granular_cpi.columns:
        df_granular_cpi['COUNTRY_NAME'] = df_granular_cpi['COUNTRY'].apply(util.get_country_name)
    else:
        st.error("Missing 'COUNTRY' column in granular CPI data. Cannot map country names.")
        return

    df_granular_cpi['Year'] = df_granular_cpi['TIME_PERIOD'].dt.year
    df_granular_cpi['Q_Num'] = df_granular_cpi['TIME_PERIOD'].dt.quarter
    df_granular_cpi['Time'] = df_granular_cpi['TIME_PERIOD'].dt.to_timestamp()

    df_granular_cpi = df_granular_cpi.sort_values(['COUNTRY_NAME', 'Time'])

    available_countries = sorted(df_granular_cpi['COUNTRY_NAME'].unique())
    available_categories = sorted(df_granular_cpi['Category'].unique())

    default_countries = ["United States"]
    default_countries = [c for c in default_countries if c in available_countries]
    if not default_countries and available_countries:
        default_countries = [available_countries[0]]

    selected_countries = st.multiselect(
        "Select up to 2 countries to compare CPI breakdown:",
        options=available_countries,
        default=default_countries,
        max_selections=2
    )

    selected_categories = st.multiselect(
        "Filter CPI categories to visualize:",
        options=available_categories,
        default=available_categories
    )

    if not selected_countries:
        st.info("Please select at least one country to view the charts.")
        return
    if not selected_categories:
        st.info("Please select at least one category to view the charts.")
        return

    df_compare = df_granular_cpi[
        df_granular_cpi['COUNTRY_NAME'].isin(selected_countries) &
        df_granular_cpi['Category'].isin(selected_categories)
    ].copy()

    if df_compare.empty:
        st.warning("No data available for the selected countries and categories. Try different selections.")
        return

    grouped = df_compare.groupby(['Time', 'COUNTRY_NAME', 'Category'])['OBS_VALUE'].sum().reset_index()

    st.markdown("---")

    # ==== Stacked Bar Chart (Total CPI broken down by category) ====
    st.subheader("CPI Breakdown by Category (Comparison)")
    fig = px.bar(
        grouped,
        x='Time',
        y='OBS_VALUE',
        color='Category',
        facet_col='COUNTRY_NAME',
        labels={'OBS_VALUE': 'CPI Value', 'Time': 'Quarter'},
        title="Total CPI Broken Down by Category",
        template='plotly_white'
    )
    fig.update_layout(barmode='stack', title_font_size=20, legend_title_text='Category', hovermode='x unified')
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ==== Line Chart by Category (Compare a single category across countries) ====
    st.subheader("Line Chart: Compare a Specific Category Across Countries")
    selected_line_category = st.selectbox(
        "Select a category to compare across countries:",
        sorted(df_compare['Category'].unique())
    )

    cat_line_df = df_compare[df_compare['Category'] == selected_line_category].copy()

    if not cat_line_df.empty:
        min_y_val = cat_line_df['OBS_VALUE'].min()
        max_y_val = cat_line_df['OBS_VALUE'].max()

        y_buffer = (max_y_val - min_y_val) * 0.05
        y_axis_range = [max(0, min_y_val - y_buffer), max_y_val + y_buffer]

        if (max_y_val - min_y_val) > 0:
            y_interval = round((max_y_val - min_y_val) / 10, 0)
            if y_interval == 0: y_interval = 1
        else:
            y_interval = 10

        fig_line = px.line(
            cat_line_df,
            x='Time',
            y='OBS_VALUE',
            color='COUNTRY_NAME',
            title=f"{selected_line_category} CPI Over Time",
            labels={'OBS_VALUE': 'CPI Value', 'Time': 'Quarter'},
            template='plotly_white'
        )

        fig_line.update_yaxes(
            range=y_axis_range,
            tick0=min_y_val,
            dtick=y_interval
        )
        fig_line.update_layout(hovermode='x unified')
        st.plotly_chart(fig_line, use_container_width=True)
    else:
        st.info(f"No data available for '{selected_line_category}' after country and category filters.")

    st.markdown("---")

    # ==== YoY % Change Bar Chart (Fixed to Q4 2024) ====
    st.subheader("Year-over-Year Change by Category (Q4 2024)")

    df_compare['YoY_pct'] = df_compare.groupby(['COUNTRY_NAME', 'Category'])['OBS_VALUE'].pct_change(periods=4) * 100

    # --- Change starts here: Target Q4 2024 explicitly ---
    target_year_yoy = 2024
    target_quarter_yoy = 4

    # Filter for the specific quarter
    yoy_df = df_compare[
        (df_compare['Time'].dt.year == target_year_yoy) &
        (df_compare['Time'].dt.quarter == target_quarter_yoy)
    ].dropna(subset=['YoY_pct']).copy()

    if not yoy_df.empty:
        fig_yoy = px.bar(
            yoy_df,
            x='Category',
            y='YoY_pct',
            color='COUNTRY_NAME',
            barmode='group',
            title=f"YoY % Change in CPI by Category (Q4 {target_year_yoy})", # Updated title
            labels={'YoY_pct': 'YoY % Change'},
            template='plotly_white'
        )
        fig_yoy.update_layout(legend_title_text="Country")
        st.plotly_chart(fig_yoy, use_container_width=True)
    else:
        st.info(f"No Year-over-Year data available for Q4 {target_year_yoy} and selected categories. This might be because data for Q4 {target_year_yoy} (and Q4 {target_year_yoy-1}) is incomplete or missing for your selections.")
    # --- Change ends here ---

    st.markdown("---")

    # ==== YoY % Change Line Graph (Comparing over time) ====
    st.subheader("YoY % Change Over Time by Category")
    st.info("This graph compares the Year-over-Year % change for a selected category between countries over time.")

    selected_yoy_line_category = st.selectbox(
        "Select a category for YoY % Change Over Time comparison:",
        sorted(df_compare['Category'].unique()),
        key="yoy_line_category_select"
    )

    yoy_line_df = df_compare[df_compare['Category'] == selected_yoy_line_category].dropna(subset=['YoY_pct']).copy()

    if not yoy_line_df.empty:
        min_yoy = yoy_line_df['YoY_pct'].min()
        max_yoy = yoy_line_df['YoY_pct'].max()

        yoy_buffer = (max_yoy - min_yoy) * 0.10
        yoy_axis_range = [min_yoy - yoy_buffer, max_yoy + yoy_buffer]

        if (max_yoy - min_yoy) > 0:
            yoy_interval = round((max_yoy - min_yoy) / 10, 0)
            if yoy_interval == 0: yoy_interval = 1
        else:
            yoy_interval = 5

        fig_yoy_line = px.line(
            yoy_line_df,
            x='Time',
            y='YoY_pct',
            color='COUNTRY_NAME',
            markers=True,
            title=f"YoY % Change in {selected_yoy_line_category} CPI Over Time",
            labels={'YoY_pct': 'YoY % Change', 'Time': 'Quarter'},
            template='plotly_white'
        )
        fig_yoy_line.update_yaxes(
            range=yoy_axis_range,
            dtick=yoy_interval
        )
        fig_yoy_line.update_layout(hovermode='x unified', legend_title_text="Country")
        st.plotly_chart(fig_yoy_line, use_container_width=True)
    else:
        st.info(f"No YoY % Change data available for '{selected_yoy_line_category}' over time with the current selections. Ensure there are at least 4 quarters of data for this category and country combination.")

    st.markdown("---")

    # ==== Heatmap (Single Country) ====
    st.subheader("CPI Heatmap")
    st.info("This heatmap is best viewed for a single country as it aggregates categories over time.")

    if len(selected_countries) == 1:
        heat_df = df_compare[df_compare['COUNTRY_NAME'] == selected_countries[0]].copy()

        if not heat_df.empty:
            heatmap_pivot = heat_df.pivot_table(
                index='Time',
                columns='Category',
                values='OBS_VALUE'
            )
            heatmap_pivot = heatmap_pivot.reindex(columns=available_categories, fill_value=0)

            fig_heat = px.imshow(
                heatmap_pivot.T,
                x=heatmap_pivot.index.strftime('%Y-Q%q'),
                y=heatmap_pivot.columns,
                aspect='auto',
                color_continuous_scale='YlOrRd',
                title=f"CPI Heatmap - {selected_countries[0]} (Value: Index)",
                labels=dict(x="Time Period", y="Category", color="CPI Value")
            )
            fig_heat.update_xaxes(side="top")
            st.plotly_chart(fig_heat, use_container_width=True)
        else:
            st.info(f"No data available for heatmap for {selected_countries[0]} with current category filters.")
    elif len(selected_countries) > 1:
        st.warning("Please select only one country to display the CPI Heatmap.")
    else:
        st.info("Select a country to view the CPI Heatmap.")

    st.markdown("---")

    # ==== Raw Table ====
    with st.expander("View Raw CPI Comparison Table"):
        if len(selected_countries) == 1:
            country = selected_countries[0]
            pivot = grouped[grouped['COUNTRY_NAME'] == country].pivot_table(
                index='Time', columns='Category', values='OBS_VALUE'
            ).round(2)
            st.markdown(f"**{country}**")
            st.dataframe(pivot, use_container_width=True)
        elif len(selected_countries) == 2:
            c1, c2 = selected_countries
            pivot1 = grouped[grouped['COUNTRY_NAME'] == c1].pivot_table(index='Time',
                                                                        columns='Category',
                                                                        values='OBS_VALUE').round(2)
            pivot2 = grouped[grouped['COUNTRY_NAME'] == c2].pivot_table(index='Time',
                                                                        columns='Category',
                                                                        values='OBS_VALUE').round(2)
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**{c1}**")
                st.dataframe(pivot1, use_container_width=True)
            with col2:
                st.markdown(f"**{c2}**")
                st.dataframe(pivot2, use_container_width=True)
        else:
            st.info("Please select at least one country to view the data.")