import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
import os
import ppp_information_etl

print("Attempting to read Excel file")

try:
    # Step 1: Read the Excel file into a DataFrame with openpyxl engine
    df = pd.read_excel('NHA_indicators.xlsx', engine='openpyxl')
    print("\n--- Snapshot: Original DataFrame Head ---")
    print(df.head())
    print(f"Original Columns: {df.columns.tolist()}")

    # Step 2: Identify id_vars and year columns dynamically
    id_vars = ['Countries', 'Indicators', 'Unnamed: 2']
    year_columns = [col for col in df.columns if str(col).isdigit() and 2013 <= int(col) <= 2023]

    # Step 3: Melt the DataFrame from wide to long format
    df_melted = pd.melt(df, id_vars=id_vars, value_vars=year_columns,
                        var_name='Year', value_name='Value')
    print("\nDataFrame pivoted successfully to long format.")
    print("\n--- Snapshot: Melted DataFrame Head ---")
    print(df_melted.head())
    print(f"New Columns: {df_melted.columns.tolist()}")
    print(f"Total rows in melted DataFrame: {len(df_melted)}")

    # Step 4: Drop the unnecessary 'Unnamed: 2' column
    df_melted.drop(columns=['Unnamed: 2'], inplace=True)
    print(f"Columns after dropping 'Unnamed: 2': {df_melted.columns.tolist()}")

    print("\n--- Snapshot: NaN counts before dropping rows ---")
    print(df_melted.isna().sum())
    print("\n--- Snapshot: Non-null counts before dropping rows ---")
    print(df_melted.count())

    # Step 5: Clean the data by removing rows where both 'Indicators' and 'Countries' are NaN
    initial_rows = len(df_melted)
    df_melted = df_melted[~(df_melted['Indicators'].isna() & df_melted['Countries'].isna())].copy()
    print(f"\nDropped {initial_rows - len(df_melted)} rows where 'Indicators' and 'Countries' were both NaN.")

    print(f"\nValue column data type before coercion: {df_melted['Value'].dtype}")
    # Step 6: Convert 'Value' to numeric, coercing errors to NaN
    df_melted['Value'] = pd.to_numeric(df_melted['Value'], errors='coerce')
    print(f"Value column data type after coercion: {df_melted['Value'].dtype}")

    # Step 7: Convert 'Year' to int and strip whitespace from 'Countries'
    df_melted['Year'] = df_melted['Year'].astype(int)
    df_melted['Countries'] = df_melted['Countries'].astype(str).str.strip()

    print("\n--- Snapshot: Cleaned Melted DataFrame Head (after initial cleaning) ---")
    print(df_melted.head())
    print("\n--- Snapshot: NaN counts after initial cleaning ---")
    print(df_melted.isna().sum())

    # Step 8: Load PPP data and clean it
    df_ppp = ppp_information_etl.get_ppp_info()
    df_ppp.rename(columns={'Country': 'Countries'}, inplace=True)
    df_ppp['Year'] = df_ppp['Year'].astype(int)
    df_ppp['Countries'] = df_ppp['Countries'].astype(str).str.strip()
    print("\n--- Snapshot: PPP DataFrame Head ---")
    print(df_ppp.head())
    print(f"PPP Columns: {df_ppp.columns.tolist()}")

    # Step 9: Separate OOPS rows and remove from main DataFrame
    df_oops = df_melted[df_melted['Indicators'] == 'Out-of-Pocket Expenditure (OOPS) per Capita in US$'].copy()
    df_non_oops = df_melted[df_melted['Indicators'] != 'Out-of-Pocket Expenditure (OOPS) per Capita in US$'].copy()

    print(f"\nNumber of OOPS rows: {len(df_oops)}")
    print(f"Number of Non-OOPS rows: {len(df_non_oops)}")

    # Step 10: Merge OOPS with PPP data
    df_oops = df_oops.merge(df_ppp[['Countries', 'Year', 'PPP_conversion_factor']],
                            on=['Countries', 'Year'], how='left')
    print("\n--- Snapshot: OOPS DataFrame after merge with PPP (head) ---")
    print(df_oops.head())
    print("\n--- Snapshot: OOPS DataFrame NaN counts after PPP merge ---")
    print(df_oops.isna().sum())

    # Step 11: Calculate adjusted value for OOPS only where PPP data exists
    df_oops['Value_PPP'] = df_oops['Value'] / df_oops['PPP_conversion_factor']

    # Step 12: For OOPS rows where PPP_conversion_factor is missing, fallback to original Value
    df_oops['Value_PPP'] = df_oops['Value_PPP'].fillna(df_oops['Value'])
    print("\n--- Snapshot: OOPS DataFrame with Value_PPP (head) ---")
    print(df_oops.head())

    # Step 13: For non-OOPS rows, Value_PPP = Value (copy original values)
    df_non_oops['Value_PPP'] = df_non_oops['Value']
    print("\n--- Snapshot: Non-OOPS DataFrame with Value_PPP (head) ---")
    print(df_non_oops.head())

    # Step 14: Combine back all rows (OOPS adjusted + others)
    df_final = pd.concat([df_non_oops, df_oops], ignore_index=True)

    print("\n--- Snapshot: Final Merged DataFrame Head ---")
    print(df_final.head())
    print(f"Final DataFrame Columns: {df_final.columns.tolist()}")
    print("\n--- Snapshot: Final Merged DataFrame NaN counts ---")
    print(df_final.isna().sum())
    print(f"Unique Indicators in final DataFrame: {df_final['Indicators'].unique()}")

    # Optional: Save merged DataFrame to CSV
    #output_csv_path = "NHA_indicators_PPP.csv"
    #df_final.to_csv(output_csv_path, index=False)
    #print(f"\nMerged data saved to '{output_csv_path}'")

    # Data Exploration: Countries with non-NaN values for each 'Indicator'
    print("\n--- Data Exploration: Countries with Non-NaN Values for Each Indicator ---")

    indicator_country_counts = df_final.groupby('Indicators')['Countries'].apply(
        lambda x: x[df_final.loc[x.index, 'Value_PPP'].notna()].unique().tolist()
    )

    for indicator, countries in indicator_country_counts.items():
        print(f"\nIndicator: {indicator}")
        if countries:
            print(f"  Countries with non-NaN values: {', '.join(countries)}")
        else:
            print("  No countries with non-NaN values for this indicator.")

    print("\n--- Data Exploration: Number of Non-NaN Values per Indicator per Country ---")

    # Count non-NaN 'Value_PPP' for each Indicator and Country
    non_na_counts = df_final.groupby(['Indicators', 'Countries'])['Value_PPP'].count().reset_index()
    non_na_counts.rename(columns={'Value_PPP': 'Non_NaN_Value_PPP_Count'}, inplace=True)

    # Filter to show only combinations with at least one non-NaN value
    non_na_counts = non_na_counts[non_na_counts['Non_NaN_Value_PPP_Count'] > 0]

    if not non_na_counts.empty:
        print(non_na_counts.to_string())
    else:
        print("No non-NaN values found for any indicator-country combination.")


except FileNotFoundError:
    print("Please ensure 'NHA_indicators.xlsx' is in the same directory as your script,")
    print("or adjust the file path accordingly.")
except Exception as e:
    print(f"An error occurred while reading or processing the Excel file: {e}")
    print(f"Detailed error: {e}")
    import traceback

    traceback.print_exc()