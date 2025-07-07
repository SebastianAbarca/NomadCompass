import streamlit as st
import pandas as pd
import os
import plotly.express as px
import pycountry
from sidebar_pages import aggregate_cpi_page, categorical_cpi_page, home_page, nha_indicators_page, population_page


st.title('Welcome to Nomad Compass :globe_with_meridians:')
st.header('Economic and Health Data Insights')

st.sidebar.header('Site Map')
selected_page = st.sidebar.radio('Go to', ['Home', 'Aggregate CPI', 'Categorical CPI', 'NHA Indicators', 'Population']) # Fixed input variable

if selected_page == 'Home':
    home_page.home_page()
elif selected_page == 'Aggregate CPI':
    aggregate_cpi_page.aggregate_cpi_page()
elif selected_page == 'Categorical CPI':
    categorical_cpi_page.categorical_cpi_page()
elif selected_page == 'NHA Indicators':
    nha_indicators_page.nha_indicators_page()
elif selected_page =='Population':
    population_page.population_page()

st.markdown("---")
st.markdown("Dashboard developed using Streamlit and Plotly.")
