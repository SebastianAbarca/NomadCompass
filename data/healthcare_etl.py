import requests
import pandas as pd
import xmltodict
import json
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
import os
import ppp_information_etl

print("Attempting to read Excel file")

try:
    # Step 1: Read the Excel file into a DataFrame with openpyxl engine
    df = pd.read_excel('NHA_indicators.xlsx', engine='openpyxl')
    #print("DataFrame loaded successfully from Excel.")
    #print(f"Original Columns: {df.columns.tolist()}")
    #print("\nFirst 5 rows of the original DataFrame:")
    #print(df.head())

    # Step 2: Identify id_vars and year columns dynamically
    id_vars = ['Countries', 'Indicators', 'Unnamed: 2']
    year_columns = [col for col in df.columns if str(col).isdigit() and 2013 <= int(col) <= 2023]

    # Step 3: Melt the DataFrame from wide to long format
    df_melted = pd.melt(df, id_vars=id_vars, value_vars=year_columns,
                        var_name='Year', value_name='Value')
    #print("\nDataFrame pivoted successfully to long format.")
    #print(f"New Columns: {df_melted.columns.tolist()}")
    #print("\nFirst 5 rows of the melted DataFrame:")
    #print(df_melted.head())
    #print(f"\nTotal rows in melted DataFrame: {len(df_melted)}")

    # Step 4: Drop the unnecessary 'Unnamed: 2' column
    df_melted.drop(columns=['Unnamed: 2'], inplace=True)
    #print(f"Columns after dropping 'Unnamed: 2': {df_melted.columns.tolist()}")

    # Step 5: Clean the data by removing rows where both 'Indicators' and 'Countries' are NaN
    df_melted = df_melted[~(df_melted['Indicators'].isna() & df_melted['Countries'].isna())].copy()

    # Step 6: Convert 'Value' to numeric, coercing errors to NaN
    df_melted['Value'] = pd.to_numeric(df_melted['Value'], errors='coerce')

    # Step 7: Convert 'Year' to int and strip whitespace from 'Countries'
    df_melted['Year'] = df_melted['Year'].astype(int)
    df_melted['Countries'] = df_melted['Countries'].astype(str).str.strip()

    # Step 8: Load PPP data and clean it
    df_ppp = ppp_information_etl.get_ppp_info()
    df_ppp.rename(columns={'Country': 'Countries'}, inplace=True)
    df_ppp['Year'] = df_ppp['Year'].astype(int)
    df_ppp['Countries'] = df_ppp['Countries'].astype(str).str.strip()

    # Step 9: Separate OOPS rows and remove from main DataFrame
    df_oops = df_melted[df_melted['Indicators'] == 'Out-of-Pocket Expenditure (OOPS) per Capita in US$'].copy()
    df_non_oops = df_melted[df_melted['Indicators'] != 'Out-of-Pocket Expenditure (OOPS) per Capita in US$'].copy()

    # Step 10: Merge OOPS with PPP data
    df_oops = df_oops.merge(df_ppp[['Countries', 'Year', 'PPP_conversion_factor']],
                            on=['Countries', 'Year'], how='left')

    # Step 11: Calculate adjusted value for OOPS only where PPP data exists
    df_oops['Value_PPP'] = df_oops['Value'] / df_oops['PPP_conversion_factor']

    # Step 12: For OOPS rows where PPP_conversion_factor is missing, fallback to original Value
    df_oops['Value_PPP'] = df_oops['Value_PPP'].fillna(df_oops['Value'])

    # Step 13: For non-OOPS rows, Value_PPP = Value (copy original values)
    df_non_oops['Value_PPP'] = df_non_oops['Value']

    # Step 14: Combine back all rows (OOPS adjusted + others)
    df_melted = pd.concat([df_non_oops, df_oops], ignore_index=True)

    print(df_melted.isna().sum())
    print(df_melted['Indicators'].unique())

    # Optional: Save merged DataFrame to CSV
    #df_melted.to_csv("NHA_indicators_PPP.csv", index=False)
    #print("\nMerged data saved to 'NHA_indicators_PPP.csv'")

except FileNotFoundError:
    print("Please ensure the 'data' folder exists in the same directory as your script,")
    print("and 'NHA_indicators.xlsx' is inside it, or adjust the file path accordingly.")
except Exception as e:
    print(f"An error occurred while reading or processing the Excel file: {e}")
    print(f"Detailed error: {e}")
