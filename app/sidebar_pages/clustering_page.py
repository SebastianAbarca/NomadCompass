import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# ML specific imports
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA

# Assuming these are available from your project structure
from app.util import util
from data.etl import imf_granular_cpi_etl # For granular/categorical CPI


def clustering_page():
    st.header("Country Segmentation using ML Clustering")
    st.markdown("""
        This section uses Machine Learning, specifically **Clustering**, to group countries based on their
        economic patterns (CPI), health expenditure indicators (NHA), and demographic data (Population).
        Clustering is an **unsupervised learning** technique that finds natural groupings within data
        without needing predefined labels. Tools used: scikit-learn
        """)

    # --- Step 0: Load All Raw Dataframes ---
    st.subheader("1. Data Collection and Initial Preprocessing")
    st.markdown("""
        Our first step involves loading our various datasets and performing initial cleaning.
        This includes converting relevant columns to numerical types (In systems, data is stored in different types.
        We cannot do math on 'String' values like "Hello" or "2", but we can on the value 2 or 21)
        and handling any immediate missing data points that would prevent basic calculations.
        """)
    with st.spinner('Loading and performing initial data checks...'):
        try:
            # Load Granular CPI Data
            df_granular_cpi_raw = imf_granular_cpi_etl.granular_cpi_data()
            # Initial preprocessing for CPI
            df_granular_cpi_raw['OBS_VALUE'] = pd.to_numeric(df_granular_cpi_raw['OBS_VALUE'], errors='coerce')
            df_granular_cpi_raw.dropna(subset=['OBS_VALUE'], inplace=True)
            df_granular_cpi_raw['COUNTRY_NAME'] = df_granular_cpi_raw['COUNTRY'].apply(util.get_country_name)

            # Load World Population Data
            df_population_raw = util.load_data('data/world_population_data.csv')
            # Initial preprocessing for Population
            df_population_raw.rename(columns={'Country/Territory': 'COUNTRY_NAME'}, inplace=True)
            df_population_raw['Population'] = pd.to_numeric(df_population_raw['Population'], errors='coerce')
            df_population_raw['Area (km²)'] = pd.to_numeric(df_population_raw['Area (km²)'], errors='coerce')
            df_population_raw['Density (per km²)'] = pd.to_numeric(df_population_raw['Density (per km²)'], errors='coerce')
            df_population_raw.dropna(subset=['Population', 'Density (per km²)'], inplace=True)

            # Load NHA Indicators Data
            # Replace 'data/NHA_indicators_PPP.csv' with your actual NHA ETL or file path
            df_nha_indicators = util.load_data('data/NHA_indicators_PPP.csv')
            # Initial preprocessing for NHA
            df_nha_indicators['Value'] = pd.to_numeric(df_nha_indicators['Value'], errors='coerce')
            df_nha_indicators['Value_PPP'] = pd.to_numeric(df_nha_indicators['Value_PPP'], errors='coerce')
            df_nha_indicators.dropna(subset=['Value_PPP'], inplace=True)
            df_nha_indicators['COUNTRY_NAME'] = df_nha_indicators['Countries'].apply(util.get_country_name)


            st.success("All raw dataframes loaded and initially cleaned.")

        except Exception as e:
            st.error(f"Error loading datasets: {e}. Please ensure all ETL functions and file paths are correct.")
            return

    # --- Step 2: Feature Engineering ---
    st.subheader("2. Feature Engineering: Creating Country Profiles")
    st.markdown("""
        For clustering, each country needs to be represented by a single "profile" or vector of features.
        Since our data is time-series based, we summarize it using aggregate statistics (like averages,
        standard deviations, or average growth rates) over the entire available period.
        This transforms the raw time-series into meaningful, comparable characteristics for each country.
        """)

    with st.spinner('Engineering features...'):
        # 2.1 Process Granular/Categorical CPI Data
        coicop_labels = {
            "CP01": "Food & Non-Alcoholic Beverages", "CP04": "Housing", "CP06": "Health",
            "CP07": "Transport", "CP09": "Recreation & Culture", "CP11": "Restaurants & Hotels"
        }
        df_granular_cpi = df_granular_cpi_raw.copy()
        df_granular_cpi['Category'] = df_granular_cpi['COICOP_1999'].map(coicop_labels).fillna(df_granular_cpi['COICOP_1999'])

        # Ensure 'Time' is created for correct YoY_pct calculation (quarterly data)
        df_granular_cpi['Year'] = df_granular_cpi['TIME_PERIOD'].str.extract(r'(\d{4})').astype(int)
        df_granular_cpi['Q_Num'] = df_granular_cpi['TIME_PERIOD'].str.extract(r'Q([1-4])').astype(int)
        df_granular_cpi['Time'] = pd.to_datetime(df_granular_cpi['Year'].astype(str) + '-Q' + df_granular_cpi['Q_Num'].astype(str))
        df_granular_cpi = df_granular_cpi.sort_values(['COUNTRY_NAME', 'Category', 'Time'])
        df_granular_cpi['YoY_pct'] = df_granular_cpi.groupby(['COUNTRY_NAME', 'Category'])['OBS_VALUE'].pct_change(periods=4) * 100

        cpi_agg_features = df_granular_cpi.groupby(['COUNTRY_NAME', 'Category']).agg(
            Avg_CPI=('OBS_VALUE', 'mean'),
            Std_CPI=('OBS_VALUE', 'std'),
            Avg_YoY_CPI=('YoY_pct', 'mean')
        ).unstack(level='Category')
        cpi_agg_features.columns = ['_'.join(col).strip() for col in cpi_agg_features.columns.values]
        cpi_agg_features.reset_index(inplace=True)


        # 2.2 Process NHA Indicators Data
        nha_agg_features = df_nha_indicators.groupby(['COUNTRY_NAME', 'Indicators']).agg(
            Avg_NHA_PPP=('Value_PPP', 'mean')
        ).unstack(level='Indicators')
        nha_agg_features.columns = ['_'.join(col).strip() for col in nha_agg_features.columns.values]
        nha_agg_features.reset_index(inplace=True)


        # 2.3 Process Population Data
        population_features = df_population_raw.groupby('COUNTRY_NAME').agg(
            Avg_Population=('Population', 'mean'),
            Avg_Density=('Density (per km²)', 'mean')
        ).reset_index()
    st.success("Features engineered for CPI, NHA, and Population data.")

    # --- Step 3: Merge All Processed Dataframes ---
    st.subheader("3. Combining Features into a Single Matrix")
    st.markdown("""
        All engineered features (economic, health, demographic) are now merged into one comprehensive
        data table where each row represents a unique country, and columns are its defining features.
        """)
    with st.spinner('Merging features...'):
        combined_features = pd.merge(cpi_agg_features, nha_agg_features, on='COUNTRY_NAME', how='outer')
        combined_features = pd.merge(combined_features, population_features, on='COUNTRY_NAME', how='outer')
    st.success(f"Combined feature matrix created. It contains {combined_features.shape[0]} countries and {combined_features.shape[1]-1} features.")
    st.dataframe(combined_features.head())


    # --- Step 4: Handling Missing Values ---
    st.subheader("4. Addressing Missing Data")
    st.markdown("""
        In real-world datasets, some countries might not have data for all indicators.
        Missing values can cause problems for many machine learning algorithms. Here,
        we handle them by:
        1.  **Dropping columns** that are entirely empty (no data for any country).
        2.  **Imputing (filling in)** remaining missing values in numerical columns with the
            **mean** value of that feature across all available countries. This is a common
            strategy to retain as much data as possible.
        3.  **Dropping** any country rows that still have missing data after imputation (e.g.,
            if a country had no original data for *any* numerical feature).
        """)
    with st.spinner('Handling missing values...'):
        initial_countries = combined_features.shape[0]
        combined_features.dropna(axis=1, how='all', inplace=True)
        for col in combined_features.select_dtypes(include=np.number).columns:
            combined_features[col].fillna(combined_features[col].mean(), inplace=True)
        combined_features.dropna(inplace=True)
        final_countries = combined_features.shape[0]
    st.info(f"Started with {initial_countries} countries. After handling missing values, {final_countries} countries remain for clustering.")
    st.dataframe(combined_features.head())

    if final_countries < 2:
        st.warning("Not enough countries with complete data to perform clustering. Please check your data sources.")
        return


    # --- NEW STEP: 5. Select Features for Clustering ---
    st.subheader("5. Select Features for Clustering")
    st.markdown("""
        Now, select the specific characteristics you want to use to group countries.
        A good set of features provides a comprehensive profile for each country,
        allowing the clustering algorithm to find meaningful similarities.
        <br><br>
        **Hover over the selected features** in the scatter plot below the results
        to see their full values for each country.
        """, unsafe_allow_html=True)

    # Get all potential numerical features after cleaning and merging
    # Exclude 'Cluster' column if it exists from previous runs/reload
    available_features = combined_features.select_dtypes(include=np.number).columns.tolist()
    if 'Cluster' in available_features:
        available_features.remove('Cluster')

    # Default selection: A balanced set or all, depending on expected number
    # For now, default to all, users can deselect
    selected_features = st.multiselect(
        "Choose features to include in the clustering analysis:",
        options=available_features,
        default=None # Default to all available features
    )

    if not selected_features:
        st.warning("Please select at least one feature to perform clustering. Stopping process.")
        return # Stop execution if no features selected

    st.info(f"You have selected {len(selected_features)} features for clustering.")

    # Prepare X_numeric based on selected features for scaling
    X_for_scaling = combined_features[selected_features]
    # Update numeric_cols for later use in cluster interpretation
    numeric_cols_for_clustering = selected_features


    # --- Step 6: Feature Scaling: Normalizing the Data --- (Renumbered from 5)
    st.subheader("6. Feature Scaling: Normalizing the Data")
    st.markdown("""
        Clustering algorithms, especially those based on distance (like K-Means), are sensitive to the
        scale of the features. For example, 'Population' values are in millions/billions, while 'CPI
        volatility' might be a small decimal. Without scaling, features with larger magnitudes would
        disproportionately influence the clustering.
        <br><br>
        We use **Standard Scaling (Z-score normalization)**, which transforms each feature so it has a
        mean of 0 and a standard deviation of 1. This ensures all features contribute equally to the
        distance calculations.
        """, unsafe_allow_html=True)
    with st.spinner('Scaling features...'):
        country_names = X_for_scaling.index # Ensure index is country names if not already
        if not isinstance(country_names, pd.Index) or country_names.name != 'COUNTRY_NAME':
            # This handles cases where COUNTRY_NAME is a column, not an index
            country_names = combined_features['COUNTRY_NAME']


        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X_for_scaling) # Use X_for_scaling here
        X_scaled_df = pd.DataFrame(X_scaled, columns=numeric_cols_for_clustering, index=country_names) # Use numeric_cols_for_clustering
    st.success("Features scaled successfully. Data is now ready for clustering.")
    st.dataframe(X_scaled_df.head())


    # --- Step 7: Determine Optimal Number of Clusters (K) --- (Renumbered from 6)
    st.subheader("7. Choosing the Optimal Number of Clusters (K)")
    st.markdown("""
        One of the challenges in clustering is deciding how many groups (K) to form.
        We explore two common methods:
        * **Elbow Method:** Plots the Sum of Squared Errors (SSE) against K. The "elbow" point
            on the graph, where the rate of decrease in SSE sharply changes, suggests an optimal K.
        * **Silhouette Score:** Measures how similar an object is to its own cluster compared to
            other clusters. Scores range from -1 (bad clustering) to +1 (dense, well-separated clusters).
            A higher score indicates better-defined clusters.
        """)

    min_k_val = 2
    # Ensure max_k_val doesn't exceed the number of selected features (for PCA later)
    # and also doesn't exceed final_countries - 1
    max_k_val = min(15, final_countries - 1, len(numeric_cols_for_clustering))
    if max_k_val < 2:
        st.warning("Not enough distinct countries or features selected to perform K-Means clustering (need at least 2 countries and 2 features).")
        return

    selected_method = st.radio(
        "Select method to determine optimal K:",
        ('Elbow Method', 'Silhouette Score')
    )
    max_k = st.slider("Select maximum K to test for Elbow/Silhouette:",
                      min_value=min_k_val, max_value=max_k_val, value=min(8, max_k_val))


    sse = []
    silhouette_scores = []
    k_range = range(min_k_val, max_k + 1)

    with st.spinner(f'Calculating SSE and Silhouette scores for K from {min_k_val} to {max_k}...'):
        for k in k_range:
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            kmeans.fit(X_scaled_df)
            sse.append(kmeans.inertia_)
            if k > 1: # Silhouette score requires at least 2 clusters
                score = silhouette_score(X_scaled_df, kmeans.labels_)
                silhouette_scores.append(score)
            else:
                silhouette_scores.append(np.nan) # Placeholder for K=1

    if selected_method == 'Elbow Method':
        st.write("#### Elbow Method Plot")
        fig_elbow, ax_elbow = plt.subplots(figsize=(10, 6))
        ax_elbow.plot(k_range, sse, marker='o', linestyle='--', color='blue')
        ax_elbow.set_xlabel("Number of Clusters (K)")
        ax_elbow.set_ylabel("Sum of Squared Errors (SSE)")
        ax_elbow.set_title("Elbow Method for Optimal K")
        ax_elbow.grid(True)
        st.pyplot(fig_elbow)
        st.info("Look for a point where the decrease in SSE starts to slow down significantly. This 'elbow' indicates a good trade-off between cluster tightness and number of clusters.")

    elif selected_method == 'Silhouette Score':
        st.write("#### Silhouette Score Plot")
        fig_silhouette, ax_silhouette = plt.subplots(figsize=(10, 6))
        ax_silhouette.plot(k_range, silhouette_scores, marker='o', linestyle='-', color='green')
        ax_silhouette.set_xlabel("Number of Clusters (K)")
        ax_silhouette.set_ylabel("Silhouette Score")
        ax_silhouette.set_title("Silhouette Score for Optimal K")
        ax_silhouette.grid(True)
        st.pyplot(fig_silhouette)
        st.info("Aim for the highest Silhouette Score, which indicates well-separated and cohesive clusters. Scores closer to 1 are better.")


    # --- Step 8: Apply K-Means Clustering --- (Renumbered from 7)
    st.subheader("8. Applying the K-Means Algorithm")
    st.markdown("""
        Once an optimal K is chosen, the K-Means algorithm is run. It iteratively assigns
        each data point (country) to the cluster whose center (centroid) is closest,
        and then recalculates the centroids based on the new assignments. This process
        repeats until cluster assignments no longer change or a maximum number of iterations is reached.
        """)
    selected_k_final = st.slider("Select the final number of clusters (K) for K-Means:",
                               min_value=min_k_val, max_value=max_k_val, value=min(3, max_k_val))
    if selected_k_final > final_countries:
         st.warning(f"Selected K ({selected_k_final}) is greater than the number of available countries ({final_countries}). Please select a K less than or equal to {final_countries}.")
         return
    if selected_k_final < 2:
        st.warning("Please select at least 2 clusters for K-Means.")
        return


    with st.spinner(f'Running K-Means with K = {selected_k_final}...'):
        kmeans = KMeans(n_clusters=selected_k_final, random_state=42, n_init=10)
        clusters = kmeans.fit_predict(X_scaled_df)
        X_scaled_df['Cluster'] = clusters
        combined_features['Cluster'] = clusters # Add cluster labels to original combined_features as well
    st.success(f"Clustering complete! Countries grouped into {selected_k_final} clusters.")
    st.dataframe(combined_features[['COUNTRY_NAME', 'Cluster']].head())

    # --- Step 9: Visualize and Interpret Clusters --- (Renumbered from 8)
    st.subheader("9. Cluster Visualization and Interpretation")
    st.markdown("""
            After clustering, the next crucial step is to understand what distinguishes each group.
            Visualizations help us see the groupings, and examining the **mean feature values**
            for each cluster reveals their unique characteristics.
            """)

    # Use PCA for 2D visualization if features are too many
    st.write("#### Visualizing Clusters (using PCA for high-dimensional data)")
    st.markdown("""
            When we have many features (dimensions), it's hard to visualize clusters directly.
            **Principal Component Analysis (PCA)** is a technique used to reduce the dimensionality
            of data while retaining as much variance as possible. Here, we reduce the many features
            into two main components (PC1 and PC2) to plot the clusters.
            """)
    if len(numeric_cols_for_clustering) > 2:  # Use length of selected features for PCA applicability
        with st.spinner("Performing PCA and plotting..."):
            pca = PCA(n_components=2)
            pca_input_df = X_scaled_df.drop(columns='Cluster', errors='ignore')
            components = pca.fit_transform(pca_input_df)

            # Define the country name column from the index of the scaled data
            country_name_col_name = X_scaled_df.index.name if X_scaled_df.index.name else 'COUNTRY_NAME'

            # Create pca_plot_df with PC1, PC2, Cluster, and COUNTRY_NAME as regular columns
            pca_plot_df = pd.DataFrame(data=components, columns=['PC1', 'PC2'])
            pca_plot_df[country_name_col_name] = pca_input_df.index.values  # Assign the index values as a column
            pca_plot_df['Cluster'] = X_scaled_df['Cluster'].values  # Assign cluster values as a column

            # --- CRITICAL FIX FOR AMBIGUITY ---
            # Ensure combined_features has a default numerical index and COUNTRY_NAME is only a column
            # This is crucial before selecting columns for hover_data
            temp_combined_features_for_hover = combined_features.copy()  # Work on a copy to avoid side effects
            if temp_combined_features_for_hover.index.name == country_name_col_name:
                temp_combined_features_for_hover = temp_combined_features_for_hover.reset_index(drop=False)
                # If reset_index creates a duplicate 'COUNTRY_NAME' column (unlikely if original was only index),
                # we'd need more complex logic, but this `drop=False` is safer here for general use.
                # For this specific error, it implies the original column existed AND it was the index.

            # Now, select the columns for hover data from the guaranteed non-ambiguous DataFrame
            features_for_hover = temp_combined_features_for_hover[[country_name_col_name] + numeric_cols_for_clustering]

            # Merge the PCA results with the original features
            pca_plot_df = pd.merge(pca_plot_df,
                                   features_for_hover,
                                   on=country_name_col_name,
                                   how='left')

            fig_pca = px.scatter(
                pca_plot_df,  # Use the new merged DataFrame which contains all needed columns
                x='PC1',
                y='PC2',
                color='Cluster',
                hover_name=country_name_col_name,  # Use the defined country name column
                hover_data={col: ':.2f' for col in numeric_cols_for_clustering},  # Show original feature values
                title='Country Clusters (PCA Reduced Dimensions)',
                template='plotly_white'
            )

            st.plotly_chart(fig_pca, use_container_width=True)
    else:
        st.info(
            "Not enough features selected for PCA (need at least 3 features for meaningful PCA visualization). Skipping PCA visualization.")
        st.info("If you selected 2 features, the clusters are directly visible in 2D without PCA.")

    st.write("#### Cluster Characteristics: What Defines Each Group?")
    st.markdown("""
            To understand each cluster, we look at the **average (mean) values of the original, unscaled
            features** for all countries within that cluster. This helps us identify the shared
            characteristics that led to their grouping.
            """)
    # This line should already be correct, assuming numeric_cols_for_clustering is accurate
    cluster_centers_df = combined_features.groupby('Cluster')[numeric_cols_for_clustering].mean().round(2)
    st.dataframe(cluster_centers_df)

    st.write("#### Countries per Cluster")
    cluster_counts = combined_features['Cluster'].value_counts().sort_index()
    st.dataframe(cluster_counts.to_frame(name='Number of Countries'))

    st.write("#### Detailed Cluster Membership")
    for i in range(selected_k_final):
        st.write(f"**Cluster {i}:**")
        st.write(combined_features[combined_features['Cluster'] == i]['COUNTRY_NAME'].tolist())