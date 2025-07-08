import streamlit as st
import pandas as pd
import plotly.express as px
from ..util import util

def categorical_cpi_page():
    df_granular_cpi = util.load_data('data/imf_cpi_selected_categories_quarterly_data.csv')
    df_granular_cpi['COUNTRY_NAME'] = df_granular_cpi['COUNTRY'].apply(util.get_country_name)
    st.header("Categorical CPI Data")
    if df_granular_cpi.empty:
        st.warning("Granular CPI data not loaded.")
    else:
        # Map COICOP codes to readable names
        coicop_labels = {
            "CP01": "Food & Non-Alcoholic Beverages",
            "CP04": "Housing",
            "CP06": "Health",
            "CP07": "Transport",
            "CP09": "Recreation & Culture",
            "CP11": "Restaurants & Hotels"
        }

        df_granular_cpi['Category'] = df_granular_cpi['COICOP_1999'].map(coicop_labels).fillna(
            df_granular_cpi['COICOP_1999'])

        # Extract year, quarter, and create datetime
        df_granular_cpi['Year'] = df_granular_cpi['TIME_PERIOD'].str.extract(r'(\d{4})').astype(int)
        df_granular_cpi['Q_Num'] = df_granular_cpi['TIME_PERIOD'].str.extract(r'Q([1-4])').astype(int)
        df_granular_cpi['Time'] = pd.to_datetime(
            df_granular_cpi['Year'].astype(str) + '-Q' + df_granular_cpi['Q_Num'].astype(str))

        df_granular_cpi = df_granular_cpi.sort_values(['COUNTRY_NAME', 'Time'])

        # Country selection
        selected_countries = st.multiselect(
            "Select up to 2 countries to compare CPI breakdown:",
            sorted(df_granular_cpi['COUNTRY_NAME'].unique()),
            default=["United States"],
            max_selections=2
        )

        # Category filter
        all_categories = sorted(df_granular_cpi['Category'].unique())
        selected_categories = st.multiselect(
            "Filter CPI categories to visualize:",
            options=all_categories,
            default=all_categories
        )

        if selected_countries and selected_categories:
            df_compare = df_granular_cpi[
                df_granular_cpi['COUNTRY_NAME'].isin(selected_countries) &
                df_granular_cpi['Category'].isin(selected_categories)
                ].copy()

            grouped = df_compare.groupby(['Time', 'COUNTRY_NAME', 'Category'])['OBS_VALUE'].sum().reset_index()

            # ==== Stacked Bar Chart ====
            fig = px.bar(
                grouped,
                x='Time',
                y='OBS_VALUE',
                color='Category',
                facet_col='COUNTRY_NAME',
                labels={'OBS_VALUE': 'CPI (PPP)', 'Time': 'Quarter'},
                title="CPI Breakdown by Category (Comparison)",
                template='plotly_white'
            )
            fig.update_layout(barmode='stack', title_font_size=20, legend_title_text='Category',
                              hovermode='x unified')
            st.plotly_chart(fig, use_container_width=True)

            # ==== Line Chart by Category ====
            selected_line_category = st.selectbox("Compare specific category across countries:",
                                                  sorted(df_compare['Category'].unique()))
            cat_line_df = df_compare[df_compare['Category'] == selected_line_category]
            fig_line = px.line(
                cat_line_df,
                x='Time',
                y='OBS_VALUE',
                color='COUNTRY_NAME',
                title=f"{selected_line_category} CPI Over Time",
                labels={'OBS_VALUE': 'CPI (PPP)', 'Time': 'Quarter'},
                template='plotly_white'
            )
            st.plotly_chart(fig_line, use_container_width=True)

            # ==== YoY % Change Bar Chart ====
            st.subheader("Year-over-Year Change by Category")

            # 1. Calculate YoY % change (4 quarters back)
            df_compare['YoY_pct'] = df_compare.groupby(['COUNTRY_NAME', 'Category'])['OBS_VALUE'].pct_change(
                periods=4) * 100

            # 2. Get latest quarter shared across both countries
            latest_time = df_compare['Time'].max()

            # 3. Filter to that quarter and drop rows without YoY %
            yoy_df = df_compare[df_compare['Time'] == latest_time].dropna(subset=['YoY_pct'])

            # 4. Optional: apply category filter if you've allowed users to select categories
            # e.g., filtered_yoy_df = yoy_df[yoy_df['Category'].isin(selected_categories)]

            # 5. Plot grouped bar chart
            if not yoy_df.empty:
                fig_yoy = px.bar(
                    yoy_df,
                    x='Category',
                    y='YoY_pct',
                    color='COUNTRY_NAME',
                    barmode='group',
                    title=f"YoY % Change in CPI by Category ({latest_time.strftime('%Y-Q%q')})",
                    labels={'YoY_pct': 'YoY % Change'},
                    template='plotly_white'
                )
                fig_yoy.update_layout(legend_title_text="Country")
                st.plotly_chart(fig_yoy, use_container_width=True)
            else:
                st.info("No YoY data available for the latest quarter and selected categories.")

            # ==== Heatmap (Single Country) ====
            st.subheader("CPI Heatmap")
            st.markdown("Only meant for a single country:smile:")
            if len(selected_countries) == 1:
                heat_df = df_compare[df_compare['COUNTRY_NAME'] == selected_countries[0]].pivot_table(
                    index='Time',
                    columns='Category',
                    values='OBS_VALUE'
                )
                fig_heat = px.imshow(
                    heat_df.T,
                    aspect='auto',
                    color_continuous_scale='YlOrRd',
                    title=f"CPI Heatmap - {selected_countries[0]}"
                )
                st.plotly_chart(fig_heat, use_container_width=True)

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