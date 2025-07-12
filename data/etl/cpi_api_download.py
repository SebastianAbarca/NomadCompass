import requests
import pandas as pd
import xmltodict
import json



def cpi_api_data():
    # Base URL for the IMF SDMX 2.1 API
    BASE_URL = "https://api.imf.org/external/sdmx/2.1/data/"

    # Define the dataflow and key for the All Countries Quarterly CPI query
    # IMF.STA,CPI: agencyID and resourceID for Consumer Price Index data
    # .CPI._T.IX.Q: The key for dimensions
    #   - '.' for all countries (REF_AREA)
    #   - 'CPI' for INDEX_TYPE
    #   - '_T' for the aggregate/total CPI indicator (COICOP_1999)
    #   - 'IX' for TYPE_OF_TRANSFORMATION (Index)
    #   - 'Q' for Quarterly Frequency
    DATAFLOW = "IMF.STA,CPI"
    KEY = ".CPI._T.IX.Q"  # All countries, CPI, Aggregate, Index, Quarterly

    # Query parameters for the specified time period (2016-2025)
    PARAMS = {
        "startPeriod": "2015",
        "endPeriod": "2025",
        "dimensionAtObservation": "TIME_PERIOD",
        "detail": "dataonly",
        "includeHistory": "false"
    }

    # Construct the full URL
    url = f"{BASE_URL}{DATAFLOW}/{KEY}"

    # Add query parameters to the URL
    query_string = "&".join([f"{k}={v}" for k, v in PARAMS.items()])
    full_url = f"{url}?{query_string}"

    # Headers for the request
    headers = {
        "Accept": "application/xml",  # Request XML format
        "Cache-Control": "no-cache",
    }

    print(f"Attempting to fetch data from: {full_url}")

    # Initialize response to None BEFORE the try block
    response = None
    xml_data = None # Also initialize xml_data to None for broader scope if parsing fails

    try:
        response = requests.get(full_url, headers=headers)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)

        # Parse the XML response
        xml_data = response.content
        data_dict = xmltodict.parse(xml_data)

        # Print the beginning of the data_dict for debugging
        print("\nBeginning of parsed data_dict (truncated):")
        # Check if 'Series' exists before trying to print it
        if 'message:StructureSpecificData' in data_dict and \
                'message:DataSet' in data_dict['message:StructureSpecificData'] and \
                'Series' in data_dict['message:StructureSpecificData']['message:DataSet']:
            print(json.dumps(data_dict["message:StructureSpecificData"]["message:DataSet"]["Series"], indent=2)[:2000])
        else:
            print("No 'Series' found in the XML response or unexpected structure to display truncated dict.")

        # Initialize a list to hold processed data for the DataFrame
        processed_data = []

        # Navigate the dictionary to extract series and observations
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

        # Create a Pandas DataFrame
        if processed_data:
            df = pd.DataFrame(processed_data)
            print("\nDataFrame created successfully:")
            print(df.head())
            print(f"\nTotal rows: {len(df)}")
            print(f"\nTotal columns: {len(df.columns)}")
            print(f"\nDescribe before dropping columns:\n{df.describe()}")

            # Drop columns with only one unique value (these are likely the fixed indicator parts)
            cols_to_drop = []
            # Dynamically check which of these columns have only one unique value
            # Exclude 'COICOP_1999' from this dynamic drop list as it will be mapped
            for col in ['INDEX_TYPE', 'TYPE_OF_TRANSFORMATION', 'FREQUENCY']:
                if col in df.columns and df[col].nunique() == 1:
                    cols_to_drop.append(col)

            if cols_to_drop:
                df.drop(columns=cols_to_drop, inplace=True)
                print(f"\nDropped columns: {', '.join(cols_to_drop)}")
            else:
                print("\nNo columns with single unique values to drop.")

            print(f"\nDescribe after dropping columns:\n{df.describe()}")

            # Map COICOP_1999 to "Aggregate"
            if 'COICOP_1999' in df.columns:
                print("\nCOICOP_1999 Categories (before mapping):")
                print(df['COICOP_1999'].value_counts())
                df['COICOP_1999'] = df['COICOP_1999'].replace({'_T': 'Aggregate'})
                print("\nCOICOP_1999 Categories (after mapping):")
                print(df['COICOP_1999'].value_counts())
            else:
                print("\n'COICOP_1999' column not found for mapping.")

            return df
            # Save the DataFrame to a CSV file
            #csv_filename = 'imf_cpi_all_countries_quarterly_data.csv'
            #df.to_csv(csv_filename, index=False)
            #print(f"\nDataFrame successfully saved to {csv_filename}")
            #^artifacts from previous iterations kept just in case.
        else:
            print("\nNo data to create DataFrame. The API might have returned an empty dataset.")
            return pd.DataFrame() # Return empty DataFrame on no data

    except requests.exceptions.RequestException as e:
        print(f"HTTP Request failed: {e}")
        if response is not None:
            print(f"Status Code: {response.status_code}")
            print(f"Response Content: {response.text}")
        return pd.DataFrame() # Return empty DataFrame on request failure
    except Exception as e:
        print(f"An error occurred: {e}")
        if xml_data is not None: # Check if xml_data was assigned before trying to use it
            print("Raw XML data that caused the parsing error (truncated):", xml_data.decode('utf-8')[:1000])
        return pd.DataFrame() # Return empty DataFrame on other errors