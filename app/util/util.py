import streamlit as st
import pandas as pd
import os
import pycountry
@st.cache_data
def load_data(file_path: str) -> pd.DataFrame:
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Construct the full absolute path
    abs_filepath = os.path.abspath(os.path.join(current_dir, file_path))

    # --- ADD THESE DEBUG PRINT STATEMENTS ---
    print(f"\n--- DEBUG: util.load_data called ---")
    print(f"DEBUG: current_dir (where util.py is): {current_dir}")
    print(f"DEBUG: input 'filepath' from calling function: {file_path}")
    print(f"DEBUG: ABSOLUTE path attempting to open: {abs_filepath}")
    print(f"--- END DEBUG ---\n")
    # --- END DEBUG PRINT STATEMENTS ---

    try:
        df = pd.read_csv(abs_filepath)
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