import requests
import pandas as pd
import xmltodict
import json


def granular_cpi_data():
    BASE_URL = "https://api.imf.org/external/sdmx/2.1/data/"
    DATAFLOW = "IMF.STA,CPI"
    # Added CP03 (Clothing and Footwear) and CP12 (Miscellaneous goods and services)
    KEY = ".CPI.CP01+CP03+CP04+CP06+CP07+CP09+CP11+CP12.IX.Q"

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
        "Accept": "application/xml",
        "Cache-Control": "no-cache",
    }

    print(f"Attempting to fetch data from: {full_url}")  # For debugging in console

    try:
        response = requests.get(full_url, headers=headers, timeout=30)  # Added timeout
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)

        xml_data = response.content
        data_dict = xmltodict.parse(xml_data)

        processed_data = []

        # Check for expected structure
        if 'message:StructureSpecificData' in data_dict and \
                'message:DataSet' in data_dict['message:StructureSpecificData'] and \
                'Series' in data_dict['message:StructureSpecificData']['message:DataSet']:

            series_data = data_dict['message:StructureSpecificData']['message:DataSet']['Series']

            # Ensure series_data is always a list for consistent iteration
            if not isinstance(series_data, list):
                series_data = [series_data]

            for series in series_data:
                # Extract series-level dimensions (e.g., COUNTRY, COICOP_1999)
                series_dimensions = {k.replace('@', ''): v for k, v in series.items() if
                                     k.startswith('@') and k != '@xsi:type'}

                observations = series.get('Obs', [])

                # Ensure observations is always a list
                if not isinstance(observations, list):
                    observations = [observations]

                for obs in observations:
                    # Extract observation-level data (e.g., TIME_PERIOD, OBS_VALUE)
                    observation_data = {k.replace('@', ''): v for k, v in obs.items() if k.startswith('@')}
                    row_data = {**series_dimensions, **observation_data}
                    processed_data.append(row_data)

        else:
            print("No 'Series' found in the XML response or unexpected structure. Check response content.")
            print(f"Full XML response (truncated for brevity): {response.text[:1000]}")
            return pd.DataFrame()  # Return empty DataFrame if structure is unexpected

        if processed_data:
            df = pd.DataFrame(processed_data)

            # Drop unnecessary columns immediately after DataFrame creation
            df = df.drop(columns=['FREQUENCY', 'TYPE_OF_TRANSFORMATION', 'INDEX_TYPE'], errors='ignore')

            # Convert OBS_VALUE to numeric
            df['OBS_VALUE'] = pd.to_numeric(df['OBS_VALUE'], errors='coerce')
            df.dropna(subset=['OBS_VALUE'], inplace=True)  # Drop rows where conversion failed

            # Convert TIME_PERIOD to Period type
            df['TIME_PERIOD'] = pd.PeriodIndex(df['TIME_PERIOD'], freq='Q')

            # Map COICOP codes to readable names (THIS IS THE PRIMARY LOCATION FOR MAPPING)
            if 'COICOP_1999' in df.columns:
                coicop_mapping = {
                    'CP01': 'Food & Non-Alcoholic Beverages',
                    'CP03': 'Clothing & Footwear',
                    'CP04': 'Housing',
                    'CP06': 'Health',
                    'CP07': 'Transport',
                    'CP09': 'Recreation & Culture',
                    'CP11': 'Restaurants & Hotels',
                    'CP12': 'Miscellaneous Goods & Services'
                }
                df['COICOP_1999'] = df['COICOP_1999'].map(coicop_mapping).fillna(
                    df['COICOP_1999'])  # Use fillna to keep original code if not mapped
                df.rename(columns={'COICOP_1999': 'Category'}, inplace=True)  # Rename here as well
            else:
                print("'COICOP_1999' column not found in DataFrame for mapping.")

            print("\nDataFrame processed successfully in ETL:")
            print(df.head())
            print(df.dtypes)
            print(f"Total rows after processing: {len(df)}")
            return df

        else:
            print("No processed data extracted from XML.")
            return pd.DataFrame()

    except requests.exceptions.Timeout:
        print("The request timed out.")
        return pd.DataFrame()
    except requests.exceptions.ConnectionError:
        print("A connection error occurred. Check your internet connection or URL.")
        return pd.DataFrame()
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e.response.status_code} - {e.response.text}")
        return pd.DataFrame()
    except requests.exceptions.RequestException as e:
        print(f"An unexpected request error occurred: {e}")
        return pd.DataFrame()
    except pd.errors.MergeError as e:  # Catch potential pandas merge errors if any
        print(f"Pandas merge error: {e}")
        return pd.DataFrame()
    except Exception as e:
        print(f"An unexpected error occurred during data processing: {e}")
        # Optionally print raw XML if parsing failed unexpectedly
        # if 'xml_data' in locals():
        #     print("Raw XML data (truncated):", xml_data.decode('utf-8')[:1000])
        return pd.DataFrame()
