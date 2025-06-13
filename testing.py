from fetch_worldbank import fetch_data, INDICATORS
from fetch_oecd import fetch_oecd_health_expenditure  # Assuming you defined fetch_oecd in fetch_oecd.py


def test_fetch_data():
    iso_codes = ['PRT', 'THA', 'USA']
    year = 2021
    df = fetch_data(INDICATORS, iso_codes, year)


    print("✅ World Bank data fetched successfully:")
    print(df)


def test_fetch_oecd_health_expenditure():
    df = fetch_oecd_health_expenditure()


    print("✅ OECD data fetched successfully:")
    print(df.head())


if __name__ == "__main__":
    test_fetch_data()
    test_fetch_oecd_health_expenditure()
