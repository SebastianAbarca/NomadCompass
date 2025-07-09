import streamlit as st
import os
import sys
# --- START FIX ---
# Get the absolute path to the directory containing app.py
current_app_dir = os.path.dirname(os.path.abspath(__file__))

# Get the path to the 'NomadCompass' directory (which is the parent of 'app')
# This is your intended project root for imports.
project_root_dir = os.path.dirname(current_app_dir)

# Add this project root directory to Python's system path
# This allows Python to find 'app' as a package directly under this root.
if project_root_dir not in sys.path:
    sys.path.insert(0, project_root_dir)
# --- END FIX ---


# Now, your imports should resolve correctly because 'NomadCompass' is on sys.path
# and 'app' is a sub-directory with an __init__.py
from app.sidebar_pages import aggregate_cpi_page, categorical_cpi_page, home_page, nha_indicators_page, population_page, \
    clustering_page
pages = [
    'Home', 'Aggregate CPI', 'Categorical CPI', 'NHA Indicators', 'Population', 'Clustering'
]
st.sidebar.header('Site Map')
selected_page = st.sidebar.radio('Go to', pages) # Fixed input variable
st.title('Welcome to Nomad Dashboard :globe_with_meridians:')
st.header('World Economic, and Health Data Insights')


content_container = st.container(border=True)
with content_container:
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
#    elif selected_page == 'Clustering':
#        clustering_page.clustering_page()

st.warning("NOTE: "
               "\nCPI data is fetched using the IMF API"
               "\nHealthcare data was downloaded from WHO's online sources"
               "\nPopulation data was downloaded from a Kaggle dataset")
st.markdown("---")
st.markdown("Dashboard developed using Streamlit and Plotly.")
