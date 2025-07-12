import requests
import pandas as pd
import xmltodict
import json

BASE_URL = "https://api.imf.org/external/sdmx/2.1/data/"
# Define the dataflow and key for the selected CPI categories query
# IMF.STA,CPI: agencyID and resourceID for Consumer Price Index data
# .CPI.CP04+CP06+CP07+CP09+CP11+CP01.IX.Q: The key for dimensions
#   - '.' for all countries (REF_AREA)
#   - 'CPI' for INDEX_TYPE
#   - 'CP04' (Housing), 'CP06' (Health), 'CP07' (Transport),
#     'CP09' (Recreation and Culture), 'CP11' (Restaurants and Hotels),
#     'CP01' (Food and non-alcoholic beverages) for multiple COICOP_1999 categories
#   - 'IX' for TYPE_OF_TRANSFORMATION (Index)
#   - 'Q' for Quarterly Frequency
DATAFLOW = "IMF.STA,CPI"
KEY = ".CPI.CP01+CP03+CP04+CP06+CP07+CP09+CP11+CP12.IX.Q"  # All countries, CPI, Selected COICOPs, Index, Quarterly

# Query parameters for the specified time period (2016-2025)
PARAMS = {
    "startPeriod": "2016",
    "endPeriod": "2025",
    "dimensionAtObservation": "TIME_PERIOD",
    "detail": "dataonly",
    "includeHistory": "false"
}

url = f"{BASE_URL}{DATAFLOW}/{KEY}"

query_string = "&".join([f"{k}={v}" for k, v in PARAMS.items()])
full_url = f"{url}?{query_string}"


headers = {
    "Accept": "application/xml",  # Request XML format
    "Cache-Control": "no-cache",
}

print(f"Attempting to fetch data from: {full_url}")

try:
    response = requests.get(full_url, headers=headers)
    response.raise_for_status()

    xml_data = response.content
    data_dict = xmltodict.parse(xml_data)

    processed_data = []

    if 'message:StructureSpecificData' in data_dict and \
            'message:DataSet' in data_dict['message:StructureSpecificData'] and \
            'Series' in data_dict['message:StructureSpecificData']['message:DataSet']:

        series_data = data_dict['message:StructureSpecificData']['message:DataSet']['Series']

        if not isinstance(series_data, list):
            series_data = [series_data]

        for series in series_data:
            series_dimensions = {k.replace('@', ''): v for k, v in series.items() if
                                 k.startswith('@') and k != '@xsi:type'}
            observations = series.get('Obs', [])

            if not isinstance(observations, list):
                observations = [observations]

            for obs in observations:
                observation_data = {k.replace('@', ''): v for k, v in obs.items() if k.startswith('@')}
                row_data = {**series_dimensions, **observation_data}
                processed_data.append(row_data)

    else:
        print("No 'Series' found in the XML response or unexpected structure.")
        print("Full XML response (truncated for brevity):", response.text[:1000])

    if processed_data:
        df = pd.DataFrame(processed_data)
        print("\nDataFrame created successfully:")
        print(df.head())
        print(f"\nTotal rows: {len(df)}")
        print(f"\nTotal columns: {len(df.columns)}")
        print(f"\nUniques columns:\n{df.columns}")
        print(f"\nDescribe before dropping columns:\n{df.describe()}")
        print("\nUnique Values in columns:")
        for col in df.columns:
            print(f"{col}: {df[col].unique()}")
        print(f"\nhead:{df.head()}")

        df = df.drop(columns=['FREQUENCY', 'TYPE_OF_TRANSFORMATION', 'INDEX_TYPE'])
        for col in df.columns:
            print(f"{col}: {df[col].unique()}")
        print(f"\nhead:{df.head()}")
        if 'COICOP_1999' in df.columns:
            print("\nCOICOP_1999 Categories (before mapping):")
            print(df['COICOP_1999'].value_counts())

            coicop_mapping = {
                'CP01': 'Food and non-alcoholic beverages',
                'CP03': 'Clothing and Footwear',
                'CP04': 'Housing',
                'CP06': 'Health',
                'CP07': 'Transport',
                'CP09': 'Recreation and Culture',
                'CP11': 'Restaurants and hotels',
                'CP12': 'Miscellaneous goods and services'
            }
            df['COICOP_1999'] = df['COICOP_1999'].replace(coicop_mapping)
            print("\nCOICOP_1999 Categories (after mapping):")
            print(df['COICOP_1999'].value_counts())
        else:
            print("\n'COICOP_1999' column not found for mapping.")

        for col in df.columns:
            print(f"{col}: {df[col].unique()}")
        print(f"\nhead:{df.head()}")
        print(df.dtypes)

        df['OBS_VALUE'] = pd.to_numeric(df['OBS_VALUE'], errors='coerce')
        df['TIME_PERIOD'] = pd.PeriodIndex(df['TIME_PERIOD'], freq='Q')


except requests.exceptions.RequestException as e:
    print(f"HTTP Request failed: {e}")
    if response is not None:
        print(f"Status Code: {response.status_code}")
        print(f"Response Content: {response.text}")
except Exception as e:
    print(f"An error occurred: {e}")
    if 'xml_data' in locals():
        print("Raw XML data that caused the parsing error (truncated):", xml_data.decode('utf-8')[:1000])