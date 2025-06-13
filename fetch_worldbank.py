import wbgapi as wb
import pandas as pd

INDICATORS = {
    "GDP_per_capita": "NY.GDP.PCAP.CD",
    "Internet_users_pct": "IT.NET.USER.ZS",
    "Urban_population_pct": "SP.URB.TOTL.IN.ZS",
    "Life_expectancy": "SP.DYN.LE00.IN"
}


def fetch_data(indicators, iso_codes, year=2021):
    """
    Fetch multiple indicators and merge them into a single DataFrame.
    """
    merged_df = None

    for readable_name, indicator_code in indicators.items():
        df = wb.data.DataFrame(indicator_code, economy=iso_codes, time=year, labels=True).reset_index()
        df = df.rename(columns={indicator_code: readable_name})

        # Only keep necessary columns
        df = df[["economy", "Country", readable_name]]

        if merged_df is None:
            merged_df = df
        else:
            merged_df = pd.merge(merged_df, df, on=["economy", "Country"], how="outer")

    return merged_df