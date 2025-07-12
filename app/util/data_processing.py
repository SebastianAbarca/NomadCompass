import streamlit as st
import pandas as pd
from data.etl import cpi_api_download
from . import util
@st.cache_data
def load_and_preprocess_cpi_data():
    df_aggregate_cpi = cpi_api_download.cpi_api_data()
    if df_aggregate_cpi.empty:
        st.warning("Aggregate CPI data not loaded. Please ensure the CPI API data is available.")
        return pd.DataFrame() # Return empty DataFrame to prevent downstream errors

    df_aggregate_cpi['OBS_VALUE'] = pd.to_numeric(df_aggregate_cpi['OBS_VALUE'], errors='coerce')
    df_aggregate_cpi.dropna(subset=['OBS_VALUE'], inplace=True)
    df_aggregate_cpi['COUNTRY_NAME'] = df_aggregate_cpi['COUNTRY'].apply(util.get_country_name)

    # Common CPI preprocessing
    try:
        df_aggregate_cpi['TIME_PERIOD_PERIOD'] = pd.PeriodIndex(df_aggregate_cpi['TIME_PERIOD'], freq='Q')
    except Exception as e:
        st.error(
            f"Error converting CPI TIME_PERIOD to a PeriodIndex: {e}. Please ensure it's in 'YYYYQn' format (e.g., '2020Q1').")
        return pd.DataFrame() # Return empty on critical error

    df_aggregate_cpi['Year'] = df_aggregate_cpi['TIME_PERIOD_PERIOD'].dt.year
    df_aggregate_cpi['Q_Num'] = df_aggregate_cpi['TIME_PERIOD_PERIOD'].dt.quarter
    df_aggregate_cpi['Time'] = df_aggregate_cpi['TIME_PERIOD_PERIOD'].dt.to_timestamp()
    df_aggregate_cpi = df_aggregate_cpi.sort_values(['COUNTRY_NAME', 'Time'])
    # Calculate Year-over-Year change (e.g., Q1 2021 vs Q1 2020)
    df_aggregate_cpi['YoY_change'] = df_aggregate_cpi.groupby('COUNTRY_NAME')['OBS_VALUE'].pct_change(periods=4) * 100

    return df_aggregate_cpi

@st.cache_data
def load_and_preprocess_population_data():
    """Loads and preprocesses world population data."""
    df_population = util.load_data('../../data/world_population_data.csv')
    if df_population.empty:
        st.warning("Population data could not be loaded. Check path.")
        return pd.DataFrame() # Return empty DF

    if 'Population' in df_population.columns:
        df_population['Population'] = pd.to_numeric(df_population['Population'], errors='coerce')
        df_population.dropna(subset=['Population', 'Year', 'Country/Territory'], inplace=True)
    else:
        st.error(
            "Population data missing 'Population' or 'Country/Territory' column. Population-related analysis may be affected.")
        return pd.DataFrame(columns=['Country/Territory', 'Year', 'Population']) # Empty DF to prevent errors
    return df_population

@st.cache_data # Consider caching this if the input df_cpi is large and stable
def calculate_cpi_stability(df_cpi: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates a CPI stability metric for each country based on the standard deviation
    of its Year-over-Year (YoY) CPI change. A lower score indicates higher stability.

    Args:
        df_cpi (pd.DataFrame): DataFrame containing CPI data, expected to have
                                'COUNTRY_NAME' and 'YoY_change' columns.

    Returns:
        pd.DataFrame: A DataFrame with 'COUNTRY_NAME' and 'CPI_Stability_Score'
                      representing the standard deviation of YoY change.
                      Returns an empty DataFrame if required columns are missing.
    """
    required_cols = ['COUNTRY_NAME', 'YoY_change']
    if not all(col in df_cpi.columns for col in required_cols):
        st.warning(f"Missing required columns {required_cols} for CPI stability calculation.")
        return pd.DataFrame(columns=['COUNTRY_NAME', 'CPI_Stability_Score'])

    # Ensure 'YoY_change' is numeric
    df_cpi['YoY_change'] = pd.to_numeric(df_cpi['YoY_change'], errors='coerce')

    # Calculate the standard deviation of Year-over-Year change for each country
    # Lower standard deviation means more stable YoY changes
    stability_df = df_cpi.groupby('COUNTRY_NAME')['YoY_change'].std().reset_index()
    stability_df.rename(columns={'YoY_change': 'CPI_Stability_Score'}, inplace=True)

    # Handle cases where a country might not have enough data points for std dev (results in NaN)
    stability_df.dropna(subset=['CPI_Stability_Score'], inplace=True)

    # Optional: If you want a 'higher is better' stability score, you could inverse it
    # For example, 1 / (score + epsilon) or max_score - score
    # For now, std dev is intuitive: lower score = more stable.

    return stability_df

@st.cache_data # Cache this function's output as it involves merging potentially large datasets
def prepare_cpi_population_scatter_data(df_cpi: pd.DataFrame, df_population: pd.DataFrame) -> pd.DataFrame:
    """
    Prepares data for a scatter plot by merging annual CPI data and population data.
    Aggregates quarterly CPI data to annual averages.

    Args:
        df_cpi (pd.DataFrame): Processed CPI DataFrame, expected to have
                                'COUNTRY_NAME', 'Year', 'OBS_VALUE', and 'YoY_change'.
        df_population (pd.DataFrame): Processed Population DataFrame, expected to have
                                      'Country/Territory', 'Year', and 'Population'.

    Returns:
        pd.DataFrame: A merged DataFrame with 'COUNTRY_NAME', 'Year', 'Population',
                      'Avg_Annual_CPI_Value', and 'Avg_Annual_CPI_YoY_Change' suitable for plotting.
                      Returns an empty DataFrame if required columns are missing or merge fails.
    """
    if df_cpi.empty or df_population.empty:
        st.warning("One or both input DataFrames for scatter data preparation are empty.")
        return pd.DataFrame()

    # --- Input Validation ---
    cpi_req_cols = ['COUNTRY_NAME', 'Year', 'OBS_VALUE', 'YoY_change']
    pop_req_cols = ['Country/Territory', 'Year', 'Population']

    if not all(col in df_cpi.columns for col in cpi_req_cols):
        st.error(f"Missing required CPI columns {cpi_req_cols} for scatter data preparation.")
        return pd.DataFrame()
    if not all(col in df_population.columns for col in pop_req_cols):
        st.error(f"Missing required Population columns {pop_req_cols} for scatter data preparation.")
        return pd.DataFrame()

    # --- Step 1: Aggregate CPI data to annual level ---
    # Take the mean of OBS_VALUE and YoY_change for each country per year
    df_cpi_annual = df_cpi.groupby(['COUNTRY_NAME', 'Year']).agg(
        Avg_Annual_CPI_Value=('OBS_VALUE', 'mean'),
        Avg_Annual_CPI_YoY_Change=('YoY_change', 'mean')
    ).reset_index()

    # --- Step 2: Prepare Population data ---
    # Rename 'Country/Territory' to 'COUNTRY_NAME' for consistent merging
    # Also ensure 'Population' is numeric and clean
    df_population_cleaned = df_population.rename(columns={'Country/Territory': 'COUNTRY_NAME'}).copy()
    df_population_cleaned['Population'] = pd.to_numeric(df_population_cleaned['Population'], errors='coerce')
    df_population_cleaned.dropna(subset=['Population', 'Year', 'COUNTRY_NAME'], inplace=True)
    df_population_cleaned['Year'] = df_population_cleaned['Year'].astype(int) # Ensure year is integer for merging

    # --- Step 3: Merge the two DataFrames ---
    # Use an inner merge to only keep countries/years present in both datasets
    merged_df = pd.merge(
        df_cpi_annual,
        df_population_cleaned[['COUNTRY_NAME', 'Year', 'Population']],
        on=['COUNTRY_NAME', 'Year'],
        how='inner'
    )

    if merged_df.empty:
        st.warning("No common data found after merging CPI and Population data.")
        return pd.DataFrame()

    # --- Step 4: Select and return relevant columns for scatter plot ---
    # The merged_df already has the desired columns for plotting
    return merged_df[['COUNTRY_NAME', 'Year', 'Population', 'Avg_Annual_CPI_Value', 'Avg_Annual_CPI_YoY_Change']]

@st.cache_data # Cache this function's output as it's a data merge operation
def merge_cpi_with_population_for_filtering(df_cpi: pd.DataFrame, df_population: pd.DataFrame) -> pd.DataFrame:
    """
    Merges quarterly CPI data with annual population data to enable population-based filtering
    on the CPI DataFrame. Population data is added to the CPI DataFrame without
    aggregating CPI data.

    Args:
        df_cpi (pd.DataFrame): The processed CPI DataFrame (quarterly level),
                               expected to have 'COUNTRY_NAME' and 'Year'.
        df_population (pd.DataFrame): The processed Population DataFrame (annual level),
                                      expected to have 'Country/Territory', 'Year', 'Population'.

    Returns:
        pd.DataFrame: The original CPI DataFrame with an added 'Population' column.
                      Returns a copy of the original CPI DataFrame if population data is
                      empty or lacks required columns for merging.
    """
    # Start with a copy of the CPI DataFrame to ensure we don't modify the original input
    df_cpi_merged = df_cpi.copy()

    if df_population.empty:
        st.info("Population data is empty. Skipping merge for filtering.")
        return df_cpi_merged

    pop_req_cols = ['Country/Territory', 'Year', 'Population']
    if not all(col in df_population.columns for col in pop_req_cols):
        st.warning(f"Population data missing required columns {pop_req_cols} for merge. Skipping population filter.")
        return df_cpi_merged

    # Prepare population data for merging: rename, convert types, drop NaNs
    df_pop_prepared = df_population.copy()
    df_pop_prepared.rename(columns={'Country/Territory': 'COUNTRY_NAME'}, inplace=True)
    df_pop_prepared['Population'] = pd.to_numeric(df_pop_prepared['Population'], errors='coerce')
    df_pop_prepared.dropna(subset=['Population', 'Year', 'COUNTRY_NAME'], inplace=True)
    df_pop_prepared['Year'] = df_pop_prepared['Year'].astype(int) # Ensure consistent year type for merge

    # Select only the necessary columns from population for the merge
    df_pop_for_merge_subset = df_pop_prepared[['COUNTRY_NAME', 'Year', 'Population']].copy()

    # Perform a left merge: keep all CPI rows, and add population where available
    df_cpi_merged = pd.merge(
        df_cpi_merged,
        df_pop_for_merge_subset,
        on=['COUNTRY_NAME', 'Year'],
        how='left' # Use left merge to keep all CPI entries, and add population if matched
    )

    # Ensure the 'Population' column is numeric after merge (might have NaNs from unmatched rows)
    df_cpi_merged['Population'] = pd.to_numeric(df_cpi_merged['Population'], errors='coerce')

    return df_cpi_merged
