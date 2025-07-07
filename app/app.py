import streamlit as st
import pandas as pd
import os
import plotly.express as px
import pycountry
from sidebar_pages import aggregate_cpi_page, categorical_cpi_page, home_page, nha_indicators_page


# Using st.cache_data to cache the data loading, improving performance
@st.cache_data
def load_data(file_path):
    try:
        df = pd.read_csv(file_path)
        return df
    except FileNotFoundError:
        st.error(f"Error: The file '{os.path.basename(file_path)}' was not found at '{file_path}'. Please check the path.")
        return pd.DataFrame() # Return empty DataFrame on error
    except Exception as e:
        st.error(f"An error occurred loading '{os.path.basename(file_path)}': {e}")
        return pd.DataFrame() # Return empty DataFrame on error

def get_country_name(alpha_3_code):
    try:
        return pycountry.countries.get(alpha_3=alpha_3_code).name
    except:
        return alpha_3_code  # fallback to code if not found


df_aggregate_cpi = load_data('data/imf_cpi_all_countries_quarterly_data.csv')
df_granular_cpi = load_data('data/imf_cpi_selected_categories_quarterly_data.csv')
df_nha_indicators = load_data('data/NHA_indicators_PPP.csv')
df_aggregate_cpi['COUNTRY_NAME'] = df_aggregate_cpi['COUNTRY'].apply(get_country_name)
df_granular_cpi['COUNTRY_NAME'] = df_granular_cpi['COUNTRY'].apply(get_country_name)
df_population = load_data('data/world_population_data.csv')

st.title('Welcome to Nomad Compass :globe_with_meridians:')
st.header('Economic and Health Data Insights')

st.sidebar.header('Site Map')
selected_page = st.sidebar.radio('Go to', ['Home', 'Aggregate CPI', 'Categorical CPI', 'NHA Indicators']) # Fixed input variable

if selected_page == 'Home':
    home_page.home_page()
elif selected_page == 'Aggregate CPI':
    aggregate_cpi_page.aggregate_cpi_page()
elif selected_page == 'Categorical CPI':
    categorical_cpi_page.categorical_cpi_page()
elif selected_page == 'NHA Indicators':
    nha_indicators_page.nha_indicators_page()

st.markdown("---")
st.markdown("Dashboard developed using Streamlit and Plotly.")
