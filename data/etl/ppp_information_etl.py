import pandas as pd
import os

def get_ppp_info():
    # Step 1: Read the file, skipping metadata lines
    df = pd.read_csv('../PPP_yearly_infomation_data.csv', skiprows=4)


    # Step 3: Rename for clarity (optional)
    df.rename(columns={
        'Country Name': 'Country',
        'Country Code': 'CountryCode',
        'Indicator Name': 'Indicator',
        'Indicator Code': 'IndicatorCode'
    }, inplace=True)



    # List all year columns as strings (adjust end year as needed)
    year_cols = [str(year) for year in range(1960, 2025)]

    # Melt to long format
    df_long = df.melt(
        id_vars=['Country', 'CountryCode', 'Indicator', 'IndicatorCode'],
        value_vars=year_cols,
        var_name='Year',
        value_name='PPP_conversion_factor'
    )

    # Convert Year to integer and PPP to float
    df_long['Year'] = df_long['Year'].astype(int)
    df_long['PPP_conversion_factor'] = pd.to_numeric(df_long['PPP_conversion_factor'], errors='coerce')

    return df_long
