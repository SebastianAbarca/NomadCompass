import pandas as pd
import numpy as np
def population_projection(df: pd.DataFrame, future_years: list, backcast_years: list):
    if df.empty or 'Country/Territory' not in df.columns or 'Year' not in df.columns or \
            'Population' not in df.columns or 'Growth Rate' not in df.columns:
        # print("Error: Input DataFrame is missing required columns or is empty.") # Don't print in Streamlit app directly
        return pd.DataFrame()

    # Ensure relevant columns are numeric (already done in load_population_data, but good for robustness)
    df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
    df['Population'] = pd.to_numeric(df['Population'], errors='coerce')
    df['Growth Rate'] = pd.to_numeric(df['Growth Rate'], errors='coerce')

    # Drop rows with NaNs in critical columns for projection
    df_cleaned = df.dropna(subset=['Year', 'Population', 'Growth Rate']).copy()

    all_projected_data = []

    # Get the latest and earliest historical data for each country once
    df_latest_historical_per_country = df_cleaned.loc[df_cleaned.groupby('Country/Territory')['Year'].idxmax()]
    df_earliest_historical_per_country = df_cleaned.loc[df_cleaned.groupby('Country/Territory')['Year'].idxmin()]

    for country in df_cleaned['Country/Territory'].unique():
        # Add historical data for this country
        country_historical_data = df_cleaned[df_cleaned['Country/Territory'] == country].copy()
        for _, row in country_historical_data.iterrows():
            row_dict = row.to_dict()
            row_dict['Type'] = 'Historical'  # Mark historical data
            all_projected_data.append(row_dict)

        # --- Data for Future Projections ---
        latest_data_row_series = df_latest_historical_per_country[
            df_latest_historical_per_country['Country/Territory'] == country
            ].squeeze()

        if latest_data_row_series.empty or pd.isna(latest_data_row_series.get('Population')) or \
                pd.isna(latest_data_row_series.get('Growth Rate')):
            continue

        population_P0_future = latest_data_row_series['Population']
        growth_rate_decimal_future = latest_data_row_series['Growth Rate'] / 100.0
        year_P0_future = latest_data_row_series['Year']

        # Future Projections
        for target_year in future_years:
            if target_year > year_P0_future:
                t_years = target_year - year_P0_future
                projected_population = population_P0_future * ((1 + growth_rate_decimal_future) ** t_years)

                new_projected_row = latest_data_row_series.to_dict()
                new_projected_row['Year'] = target_year
                new_projected_row['Population'] = projected_population
                new_projected_row['Type'] = 'Projected (Future)'
                all_projected_data.append(new_projected_row)

        # --- Data for Backcasting ---
        earliest_data_row_series = df_earliest_historical_per_country[
            df_earliest_historical_per_country['Country/Territory'] == country
            ].squeeze()

        if earliest_data_row_series.empty or pd.isna(earliest_data_row_series.get('Population')) or \
                pd.isna(earliest_data_row_series.get('Growth Rate')):
            continue

        population_Pt_back = earliest_data_row_series['Population']
        growth_rate_decimal_back = latest_data_row_series[
                                       'Growth Rate'] / 100.0  # Using latest growth rate for backcasting
        year_Pt_back = earliest_data_row_series['Year']

        # Backcasting
        for target_year in backcast_years:
            if target_year < year_Pt_back:
                t_years = year_Pt_back - target_year
                if (1 + growth_rate_decimal_back) == 0:
                    backcasted_population = np.nan
                else:
                    backcasted_population = population_Pt_back / ((1 + growth_rate_decimal_back) ** t_years)

                new_backcasted_row = earliest_data_row_series.to_dict()
                new_backcasted_row['Year'] = target_year
                new_backcasted_row['Population'] = backcasted_population
                new_backcasted_row['Type'] = 'Projected (Past)'
                all_projected_data.append(new_backcasted_row)

    df_result = pd.DataFrame(all_projected_data)

    if not df_result.empty:
        df_result['Year'] = df_result['Year'].astype(int)
        df_result.drop_duplicates(subset=['Country/Territory', 'Year'], inplace=True)
        df_result.sort_values(by=['Country/Territory', 'Year'], inplace=True, ignore_index=True)

    return df_result


def apply_iqr_outlier_filter(df: pd.DataFrame, columns_to_filter: list, iqr_multiplier: float) -> pd.DataFrame:
    filtered_df = df.copy()
    initial_rows = len(df)

    for col in columns_to_filter:
        if col in filtered_df.columns and len(filtered_df) >= 4: # Need at least 4 data points for quartiles
            Q1 = filtered_df[col].quantile(0.25)
            Q3 = filtered_df[col].quantile(0.75)
            IQR = Q3 - Q1

            lower_bound = Q1 - iqr_multiplier * IQR
            upper_bound = Q3 + iqr_multiplier * IQR

            filtered_df = filtered_df[
                (filtered_df[col] >= lower_bound) &
                (filtered_df[col] <= upper_bound)
            ]
        elif len(filtered_df) < 4 and len(filtered_df) > 0:
            # Not enough data for IQR calculation, but data exists.
            # No filtering for this column, and subsequent columns if loop breaks.
            # The calling function will handle the message.
            pass
        elif len(filtered_df) == 0:
            # No data left to filter, stop processing.
            break

    removed_rows = initial_rows - len(filtered_df)
    return filtered_df, removed_rows