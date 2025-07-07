import streamlit as st
import pandas as pd
import os
import plotly
import plotly.express as px
import pycountry
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
    st.header('Information')
    st.markdown("""
        This dashboard provides visualizations and insights into various economic and health indicators.
        Use the sidebar to navigate between different data views:
        - **Aggregate CPI**: Overall Consumer Price Index data for all countries, quarterly.
        - **Categorical CPI**: Consumer Price Index data broken down by specific expenditure categories (Housing, Transport, etc.), quarterly.
        - **NHA Indicators**: National Health Accounts indicators, transformed into a long format for easier analysis.
        """)
    st.subheader("Overview:")
    describe = st.radio('Choose a category', ['Aggregate CPI', 'Categorical CPI', 'NHA Indicators'])
    if describe =='Aggregate CPI':
        if not df_aggregate_cpi.empty:
            st.write("### Aggregate CPI Data")
            st.markdown("""
            # :chart_with_upwards_trend: Consumer Price Index (CPI)
    
            **CPI** stands for **Consumer Price Index**. It's a widely used economic indicator that measures the **average change over time in the prices paid by consumers for a basket of goods and services**.
    
            ---
    
            ## :small_blue_diamond: What CPI Measures
            - Inflation (when prices go up) or deflation (when prices go down)
            - The cost of living over time
    
            ---
    
            ## :small_blue_diamond: What's in the "Basket"?
    
            The basket typically includes categories like:
            - **Food and beverages**
            - **Housing** (rent, utilities)
            - **Apparel**
            - **Transportation** (gasoline, public transit)
            - **Medical care**
            - **Education**
            - **Recreation**
    
            ---
    
            ## :small_blue_diamond: Why CPI Matters
    
            - **Economists** use it to track inflation.
            - **Central banks** (like the U.S. Federal Reserve) use it to guide interest rate policy.
            - **Governments** use it to adjust social security payments, tax brackets, and wages.
            - **Businesses** use it for price-setting and contract adjustments.
            
            ---
            
            ## :small_blue_diamond: Example
            
            If CPI rises by 3% from last year, it means the average consumer is paying **3% more** for the same goods and services compared to last year.
            
            ---
            """)

    elif describe == 'Categorical CPI':
        if not df_granular_cpi.empty:
            st.write("### Granular CPI Data")
            st.markdown("""
            # :bar_chart: Introduction to COICOP

            The **Classification of Individual Consumption by Purpose (COICOP)** is the UN’s internationally recommended framework for categorizing household expenditures. It groups goods and services by their purpose to ensure CPI comparability across countries ([UN Stats](https://unstats.un.org/unsd/classifications/Econ/Download/In%20Text/COICOP_2018_pre_edited_white_cover_version_2018_12_26.pdf)).
            
            ---
            
            ## :house: Housing (COICOP04)
            
            Includes:
            - **Actual rents**: The market rent paid by tenants.
            - **Imputed rents**: An estimated “rental value” of owner‑occupied housing—what homeowners would pay if they were renting. This is included to capture the consumption value of shelter.
            
            Also includes maintenance, repair, and utilities such as electricity, water, gas, and other fuels.
            
            ---
            
            ## :hospital: Health (COICOP06)
            
            Covers expenditures on:
            - Medicines and health products  
            - Outpatient and inpatient services  
            - **Other medical services**, such as:
              - Dental care  
              - Physiotherapy  
              - Diagnostic tests
            
            ---
            
            ## :bus: Transport (COICOP07)
            
            Covers:
            - Purchase and maintenance of vehicles  
            - **Public transport**: Buses, trains, subways, air travel, ferries
            
            ---
            
            ## :performing_arts: Recreation and Culture (COICOP09)
            
            Includes spending on:
            - Audio‑visual and photographic goods  
            - Recreational equipment and supplies  
            - Garden and pet-related products  
            - Cultural and leisure services (e.g., cinema, concerts, museums)  
            - Books, newspapers, magazines  
            - Package holidays
            
            ---
            
            ## :plate_with_cutlery: Restaurants and Hotels (COICOP11 – CP11)
            
            Covers:
            - **Food & beverage services**: Restaurants, cafes, fast food, catering  
            - **Accommodation services**: Hotels, inns, hostels, and similar establishments
            
            ---
            
            ## :cup_with_straw: Food and Non‑Alcoholic Beverages (COICOP01 – CP01)
            
            Includes:
            - Groceries and drinks consumed at home  
            - **Processing services for primary items**: Services like grinding cereals into flour, pressing fruit into juice, or custom slaughtering. These are household-paid services for preparing raw food into edible form.
            
            ---
            
            ## :mag_right: IMF Approach & Usage
            
            The **IMF’s CPI Manual** and global statistical frameworks like **GDDS/E-GDDS** follow COICOP to standardize CPI across countries.  
            - National CPI baskets are aligned using COICOP divisions.  
            - **Expenditure weights** are based on household consumption surveys.  
            - **Imputed rents** are used to account for owner-occupied housing in a comparable way to rental housing.
            
            More at: [IMF CPI Manual – Concepts and Scope](https://www.imf.org/-/media/Files/Data/CPI/chapter-2-concepts-scope-and-uses-of-cpis.ashx)
            
            ---
            
            ## :pushpin: COICOP Code → Category
            
            | COICOP Code | Category                      |
            |-------------|-------------------------------|
            | 01          | Food & Non‑Alcoholic Beverages |
            | 04          | Housing                        |
            | 06          | Health                         |
            | 07          | Transport                      |
            | 09          | Recreation and Culture         |
            | 11          | Restaurants and Hotels         |
            
            ---

            """)
        else:
            st.warning("Granular CPI data not loaded.")
    elif describe == 'NHA Indicators':
        if not df_nha_indicators.empty:
            st.write("### NHA Indicators")
            st.markdown("""
                    ### Key Health Indicators Description
                    """)

            st.markdown("**Out-of-Pocket Expenditure (OOPS) per Capita (PPP Adjusted):**")
            st.markdown("This represents the average amount individuals spend directly from their own pockets on "
                        "healthcare services, adjusted for Purchasing Power Parity (PPP). PPP adjustment allows for "
                        "fairer comparisons across countries by accounting for differences in cost of living and inflation.")
            with st.expander("More information on Out-of-Pocket Expenditure (OOPS) per Capita", expanded=False):
                st.markdown("""
                        Out-of-Pocket Expenditure (OOPS) refers to direct payments made by individuals to healthcare providers at the 
                        time of service. This includes expenses for doctor visits, medications, diagnostics, hospital stays, and other 
                        medical services not covered by insurance or government programs.
                        High OOPS often indicates a heavier financial burden on individuals and households, especially in countries with 
                        limited health insurance coverage or weak public health systems. It can lead to catastrophic health expenditures, 
                        forcing families to cut spending on essential needs or fall into poverty.
                        \n**Note:** In this dataset, OOPS is adjusted using Purchasing Power Parity (PPP), allowing for fairer international 
                        comparisons by accounting for cost of living and currency differences.
                        \nIt will be labeld as 'Adjusted' in on visualizations and such
                        """)

            st.markdown("**Purchasing Power Parity (PPP):**")
            st.markdown("PPP is an economic metric that compares different countries’ currencies through a “basket of goods” "
                        "approach, enabling more accurate international comparisons of economic indicators and living standards.")
            with st.expander("More information on Purchasing Power Parity (PPP)", expanded=False):
                st.markdown("""
                        Purchasing Power Parity (PPP) is an economic theory and statistical method used to compare the relative value 
                        of different countries' currencies. The basic idea behind PPP is that in the absence of transportation costs and 
                        trade barriers, identical goods and services should have the same price in different countries when prices are converted 
                        to a common currency.
                        PPP is used to adjust economic indicators (like GDP, income, or health expenditures) to account for differences in 
                        price levels between countries, allowing for more accurate international comparisons. 
                        For example, 100 in Country A might buy more healthcare services than $100 in Country B due to differences in local prices. 
                        PPP adjusts for these differences, providing a better sense of the actual purchasing power of money.
                        \n Helpful Link:https://www.investopedia.com/updates/purchasing-power-parity-ppp/
                        """)

            st.markdown("**Curative Care:**")
            st.markdown("Services aimed at curing illnesses or health conditions through treatments, surgeries, or medications.")
            with st.expander("More information on Curative Care", expanded=False):
                st.markdown("""
                        Curative care refers to health services provided with the intent to cure a patient’s disease or alleviate 
                        symptoms until recovery. 
                        It includes interventions such as:

                        - **Medical treatments** (e.g., antibiotics, antiviral therapies)
                        - **Surgical procedures**
                        - **Hospitalization for acute conditions**
                        - **Specialist consultations and diagnostic services**
                        
                        Curative care is typically reactive—addressing health issues after they arise—rather than preventive. While essential 
                        for managing disease burden, an overreliance on curative services 
                        can strain healthcare systems and divert resources from preventive and primary care efforts.
                        
                        Investing in curative care is crucial for improving survival rates and quality of life, especially in systems managing a 
                        high prevalence of infectious or chronic diseases.
                        """)

            st.markdown("**Pharmaceuticals and Other Medical Durable Goods:**")
            st.markdown("Expenses related to medicines, vaccines, medical devices, and other durable healthcare products essential for treatment and management of diseases.")
            with st.expander("More information on Pharmaceuticals and Other Medical Durable Goods", expanded=False):
                st.markdown("""
                        Pharmaceuticals and other medical durable goods represent a core component of health spending. This category includes:

                        - **Prescription and over-the-counter (OTC) medications**
                        - **Vaccines and therapeutic biologics**
                        - **Medical supplies** (e.g., bandages, syringes, diagnostic strips)
                        - **Durable medical equipment (DME)** such as wheelchairs, hearing aids, prosthetics, or insulin pumps
                        
                        Pharmaceuticals play a critical role in the treatment and management of diseases, from acute infections to chronic conditions 
                        like diabetes or hypertension. 
                        
                        Durable medical goods are designed for repeated use and often support long-term patient care, especially for individuals with disabilities 
                        or chronic illnesses.
                        
                        Trends in this indicator can reflect access to modern therapies, healthcare affordability, and the strength of a country's 
                        pharmaceutical supply chain. In many countries,
                        rising pharmaceutical costs are a key concern for both public health systems and individual patients.
                        """)

            st.markdown("**Preventive Care:**")
            st.markdown("Health services focused on disease prevention, such as screenings, vaccinations, and health education to reduce the risk or severity of illness.")
            with st.expander("More information on Preventive Care", expanded=False):
                st.markdown("""
                        Preventive care refers to medical services and interventions aimed at preventing the onset of illness or detecting health issues at an early stage, before symptoms develop or conditions worsen.

                        This includes:
                        
                        - **Screenings and check-ups** (e.g., blood pressure checks, cholesterol tests, cancer screenings)
                        - **Health education and counseling** (e.g., lifestyle advice on smoking cessation, nutrition, and exercise)
                        - **Routine vaccinations** to prevent infectious diseases
                        - **Prenatal and well-child visits**
                        
                        Preventive care reduces long-term healthcare costs by avoiding more serious and expensive treatments later. It also improves quality of life and increases life expectancy by catching conditions early or avoiding them altogether.
                        
                        Investment in preventive services is often considered a high-value strategy for strengthening public health systems and reducing health disparities.

                        """)

            st.markdown("**Immunization Programmes:**")
            st.markdown("Organized efforts to provide vaccinations to populations, aiming to prevent infectious diseases and protect public health.")
            with st.expander("More information on Immunization Programmes", expanded=False):
                st.markdown("""
                        Immunization programmes are organized efforts by governments, health organizations, and communities to deliver vaccines to the population, 
                        particularly children and vulnerable groups.

                        These programmes aim to:
                        
                        - **Prevent infectious diseases** such as measles, polio, diphtheria, and hepatitis
                        - **Achieve herd immunity**, reducing the overall presence of disease in the population
                        - **Improve child survival rates** and reduce the burden of disease
                        - **Prevent disease outbreaks and pandemics**
                        
                        Key components of immunization programmes include:
                        
                        - **Routine childhood immunizations**
                        - **Supplementary immunization activities** during outbreaks
                        - **Cold chain systems** to keep vaccines safe and effective during transport and storage
                        - **Public education and outreach** to increase awareness and vaccine uptake
                        
                        Immunization is one of the most cost-effective health interventions available and is essential for achieving universal 
                        health coverage and global health security.
                        """)

            st.markdown("**Early Disease Detection Programmes:**")
            st.markdown("Initiatives designed to identify diseases at an early stage, improving treatment outcomes and reducing healthcare costs.")
            with st.expander("More information on Early Disease Detection Programmes", expanded=False):
                st.markdown("""
                        Early disease detection programmes are public health initiatives focused on identifying illnesses at an early, often asymptomatic stage.

                        Their goals include:
                        
                        - **Improving treatment outcomes** by catching diseases before they progress
                        - **Reducing long-term healthcare costs**
                        - **Increasing survival rates** for conditions like cancer, diabetes, and cardiovascular disease
                        
                        Common methods include:
                        
                        - Routine screenings (e.g., mammograms, blood pressure checks)
                        - Genetic testing for inherited conditions
                        - Health risk assessments based on lifestyle or family history
                        
                        These programmes are essential for shifting healthcare from reactive to proactive, enabling earlier interventions and better quality of life.
                        """)

            st.markdown("**Healthy Condition Monitoring Programmes:**")
            st.markdown("Ongoing monitoring services to manage chronic conditions and maintain health, including regular check-ups and health assessments.")
            with st.expander("More information on Healthy Condition Monitoring Programmes", expanded=False):
                st.markdown("""
                        Healthy condition monitoring programmes are designed to track individuals’ health status over time, especially for those with chronic conditions or at risk of developing them.

                        Key objectives include:
                        
                        - **Maintaining stable health** by catching early signs of deterioration
                        - **Personalized care** through regular check-ups and health metrics
                        - **Empowering patients** to take an active role in managing their health
                        
                        These programmes often involve:
                        
                        - Routine medical visits and laboratory tests
                        - Use of wearable technology or remote monitoring devices
                        - Data collection on vital signs, medication adherence, and symptoms
                        
                        By continuously monitoring health, these programmes help prevent complications, reduce hospitalizations, and support long-term well-being.
                        """)

            st.markdown("**Preparing for Disaster and Emergency Response Programmes:**")
            st.markdown("Activities and plans to ready healthcare systems for natural disasters, epidemics, or emergencies, ensuring timely and effective responses.")
            with st.expander("More information on Preparing for Disaster and Emergency Response Programmes",
                             expanded=False):
                st.markdown("""
                        Preparing for disaster and emergency response programmes ensures that health systems are equipped to handle sudden and large-scale crises, such as natural disasters, pandemics, or mass casualty events.

                        Key components include:
                        
                        - **Emergency preparedness planning** at national and local levels
                        - **Training healthcare personnel** for crisis scenarios
                        - **Stockpiling and distributing critical medical supplies**
                        - **Establishing early warning systems** and communication protocols
                        - **Coordinating with international and humanitarian organizations**
                        
                        These programmes are essential for minimizing the impact of emergencies on population health and ensuring timely and effective medical responses when systems are under stress.
                        """)
    else:
            st.warning("NHA Indicators data not loaded.")
elif selected_page == 'Aggregate CPI':
            st.header("Aggregate CPI Data")

            if df_aggregate_cpi.empty:
                st.warning("Aggregate CPI data not loaded.")
            else:
                # --- Data Preprocessing for CPI ---
                df_cpi = df_aggregate_cpi.copy()

                # Safely convert 'TIME_PERIOD' to PeriodIndex for proper quarterly handling
                try:
                    # Assuming 'TIME_PERIOD' is directly like '2020Q1', '2020Q2', etc.
                    df_cpi['TIME_PERIOD_PERIOD'] = pd.PeriodIndex(df_cpi['TIME_PERIOD'], freq='Q')
                except Exception as e:
                    st.error(
                        f"Error converting CPI TIME_PERIOD to a PeriodIndex: {e}. Please ensure it's in 'YYYYQn' format (e.g., '2020Q1').")

                # Extract Year and Quarter Number using the PeriodIndex accessor
                df_cpi['Year'] = df_cpi['TIME_PERIOD_PERIOD'].dt.year
                df_cpi['Q_Num'] = df_cpi['TIME_PERIOD_PERIOD'].dt.quarter

                # Convert PeriodIndex to Timestamp for Plotly (Plotly prefers datetime objects)
                df_cpi['Time'] = df_cpi['TIME_PERIOD_PERIOD'].dt.to_timestamp()
                df_cpi = df_cpi.sort_values(['COUNTRY_NAME', 'Time'])

                # Calculate Year-over-Year (YoY) % change
                # Ensure data is sorted for correct pct_change calculation within each country group
                df_cpi['YoY_change'] = df_cpi.groupby('COUNTRY_NAME')['OBS_VALUE'].pct_change(periods=4) * 100

                # --- CPI Over Time Visualization ---
                st.subheader("CPI Over Time by Country")
                countries = df_cpi['COUNTRY_NAME'].unique()
                selected_countries = st.multiselect(
                    "Select one or more countries to visualize CPI over time:",
                    options=sorted(countries),
                    default=['Aruba']
                )

                if selected_countries:
                    df_filtered_plot = df_cpi[df_cpi['COUNTRY_NAME'].isin(selected_countries)].copy()

                    fig_cpi_time = px.line(
                        df_filtered_plot,
                        x='Time',
                        y='OBS_VALUE',
                        color='COUNTRY_NAME',
                        markers=True,
                        labels={'Time': 'Quarter', 'OBS_VALUE': 'CPI Value'},
                        title='Aggregate CPI Over Time by Country',
                        template='plotly_white'
                    )
                    fig_cpi_time.update_layout(hovermode='x unified', title_font_size=20)
                    st.plotly_chart(fig_cpi_time, use_container_width=True)
                else:
                    st.info("Please select at least one country to display the CPI over time chart.")

                # --- CPI Stability Analysis ---
                st.subheader("Top 10 Most Stable Countries (Lowest CPI Volatility)")

                # --- Prepare Population Data for Merging ---
                df_pop_processed = df_population.copy()
                if 'Country/Territory' in df_pop_processed.columns:
                    df_pop_processed.rename(columns={'Country/Territory': 'COUNTRY_NAME'}, inplace=True)
                else:
                    st.warning("Population data is missing 'Country/Territory' column. Cannot merge effectively.")
                    df_pop_processed = pd.DataFrame()

                if not df_pop_processed.empty and 'Year' in df_pop_processed.columns and 'Population' in df_pop_processed.columns:
                    df_pop_for_merge = df_pop_processed[['COUNTRY_NAME', 'Year', 'Population']].copy()

                    # --- Merge CPI data with Population data ---
                    df_cpi_with_population = pd.merge(
                        df_cpi,
                        df_pop_for_merge,
                        on=['COUNTRY_NAME', 'Year'],
                        how='left'
                    )
                else:
                    st.warning(
                        "Population data is not in the expected format or is empty. Stability analysis will proceed without population filtering.")
                    df_cpi_with_population = df_cpi.copy()

                # --- Population Filtering for Stability Analysis ---
                filtered_cpi_df = df_cpi_with_population.copy()

                if 'Population' in filtered_cpi_df.columns and not filtered_cpi_df['Population'].isnull().all():
                    min_pop = int(filtered_cpi_df['Population'].min())
                    max_pop = int(filtered_cpi_df['Population'].max())

                    min_pop_M = min_pop // 1_000_000
                    max_pop_M = (max_pop + 999_999) // 1_000_000

                    population_range_M = st.slider(
                        'Select Population Range (in millions) for Stability Analysis:',
                        min_value=min_pop_M,
                        max_value=max_pop_M,
                        value=(min_pop_M, max_pop_M),
                        step=10,
                        format='%dM'
                    )

                    filtered_cpi_df = filtered_cpi_df[
                        (filtered_cpi_df['Population'] >= population_range_M[0] * 1_000_000) &
                        (filtered_cpi_df['Population'] <= population_range_M[1] * 1_000_000)
                        ].copy()
                    st.info(
                        f"Filtering countries with population between {population_range_M[0]}M and {population_range_M[1]}M.")
                else:
                    st.info(
                        "Population data not available or incomplete for filtering. Displaying stability for all countries with CPI data.")

                # --- Calculate Stability ---
                if 'YoY_change' not in filtered_cpi_df.columns or filtered_cpi_df['YoY_change'].isnull().all():
                    st.warning(
                        "YoY_change data not available or is all null after filtering. Cannot calculate stability.")
                    stability_df = pd.DataFrame()
                else:
                    stability_df = (
                        filtered_cpi_df.groupby('COUNTRY_NAME')['YoY_change']
                        .std()
                        .dropna()
                        .sort_values()
                        .reset_index()
                        .rename(columns={'YoY_change': 'YoY_StdDev'})
                    )

                # --- Display Stability Results ---
                if not stability_df.empty:
                    top_stable = stability_df.head(10)

                    col1, col2 = st.columns([4, 3])
                    with col1:
                        fig_stab = px.bar(
                            top_stable,
                            x='COUNTRY_NAME',
                            y='YoY_StdDev',
                            text=top_stable['YoY_StdDev'].round(2),
                            labels={'YoY_StdDev': 'Std. Dev of YoY % Change', 'COUNTRY_NAME': 'Country'},
                            title='Top 10 CPI Stable Countries',
                            template='plotly_white'
                        )
                        fig_stab.update_traces(marker_color='seagreen')
                        fig_stab.update_layout(xaxis_title_text='')
                        st.plotly_chart(fig_stab, use_container_width=True)

                    with col2:
                        st.write("### Stability Data Table")
                        st.dataframe(top_stable.set_index('COUNTRY_NAME').round(2), use_container_width=True)
                else:
                    st.info("Not enough data to calculate CPI stability for the selected population range.")

                # --- Explore Individual Country CPI ---
                all_countries_merged = sorted(df_cpi_with_population['COUNTRY_NAME'].unique())
                selected_country_agg_explore = st.selectbox('Select a Country to view all its CPI data:',
                                                            all_countries_merged)

                if selected_country_agg_explore:
                    country_df_agg_explore = df_cpi_with_population[
                        df_cpi_with_population['COUNTRY_NAME'] == selected_country_agg_explore
                        ].copy()
                    st.write(f"### Detailed CPI Data for {selected_country_agg_explore}")
                    st.dataframe(country_df_agg_explore.round(2), use_container_width=True)
elif selected_page == 'Categorical CPI':
    st.header("Categorical CPI Data")
    if df_granular_cpi.empty:
        st.warning("Granular CPI data not loaded.")
    else:
        # Map COICOP codes to readable names
        coicop_labels = {
            "CP01": "Food & Non-Alcoholic Beverages",
            "CP04": "Housing",
            "CP06": "Health",
            "CP07": "Transport",
            "CP09": "Recreation & Culture",
            "CP11": "Restaurants & Hotels"
        }

        df_granular_cpi['Category'] = df_granular_cpi['COICOP_1999'].map(coicop_labels).fillna(
            df_granular_cpi['COICOP_1999'])

        # Extract year, quarter, and create datetime
        df_granular_cpi['Year'] = df_granular_cpi['TIME_PERIOD'].str.extract(r'(\d{4})').astype(int)
        df_granular_cpi['Q_Num'] = df_granular_cpi['TIME_PERIOD'].str.extract(r'Q([1-4])').astype(int)
        df_granular_cpi['Time'] = pd.to_datetime(
            df_granular_cpi['Year'].astype(str) + '-Q' + df_granular_cpi['Q_Num'].astype(str))

        df_granular_cpi = df_granular_cpi.sort_values(['COUNTRY_NAME', 'Time'])

        # Country selection
        selected_countries = st.multiselect(
            "Select up to 2 countries to compare CPI breakdown:",
            sorted(df_granular_cpi['COUNTRY_NAME'].unique()),
            default=["United States"],
            max_selections=2
        )

        # Category filter
        all_categories = sorted(df_granular_cpi['Category'].unique())
        selected_categories = st.multiselect(
            "Filter CPI categories to visualize:",
            options=all_categories,
            default=all_categories
        )

        if selected_countries and selected_categories:
            df_compare = df_granular_cpi[
                df_granular_cpi['COUNTRY_NAME'].isin(selected_countries) &
                df_granular_cpi['Category'].isin(selected_categories)
                ].copy()

            grouped = df_compare.groupby(['Time', 'COUNTRY_NAME', 'Category'])['OBS_VALUE'].sum().reset_index()

            # ==== Stacked Bar Chart ====
            fig = px.bar(
                grouped,
                x='Time',
                y='OBS_VALUE',
                color='Category',
                facet_col='COUNTRY_NAME',
                labels={'OBS_VALUE': 'CPI (PPP)', 'Time': 'Quarter'},
                title="CPI Breakdown by Category (Comparison)",
                template='plotly_white'
            )
            fig.update_layout(barmode='stack', title_font_size=20, legend_title_text='Category',
                              hovermode='x unified')
            st.plotly_chart(fig, use_container_width=True)


            # ==== Line Chart by Category ====
            selected_line_category = st.selectbox("Compare specific category across countries:",
                                                  sorted(df_compare['Category'].unique()))
            cat_line_df = df_compare[df_compare['Category'] == selected_line_category]
            fig_line = px.line(
                cat_line_df,
                x='Time',
                y='OBS_VALUE',
                color='COUNTRY_NAME',
                title=f"{selected_line_category} CPI Over Time",
                labels={'OBS_VALUE': 'CPI (PPP)', 'Time': 'Quarter'},
                template='plotly_white'
            )
            st.plotly_chart(fig_line, use_container_width=True)

            # ==== YoY % Change Bar Chart ====
            st.subheader("Year-over-Year Change by Category")

            # 1. Calculate YoY % change (4 quarters back)
            df_compare['YoY_pct'] = df_compare.groupby(['COUNTRY_NAME', 'Category'])['OBS_VALUE'].pct_change(
                periods=4) * 100

            # 2. Get latest quarter shared across both countries
            latest_time = df_compare['Time'].max()

            # 3. Filter to that quarter and drop rows without YoY %
            yoy_df = df_compare[df_compare['Time'] == latest_time].dropna(subset=['YoY_pct'])

            # 4. Optional: apply category filter if you've allowed users to select categories
            # e.g., filtered_yoy_df = yoy_df[yoy_df['Category'].isin(selected_categories)]

            # 5. Plot grouped bar chart
            if not yoy_df.empty:
                fig_yoy = px.bar(
                    yoy_df,
                    x='Category',
                    y='YoY_pct',
                    color='COUNTRY_NAME',
                    barmode='group',
                    title=f"YoY % Change in CPI by Category ({latest_time.strftime('%Y-Q%q')})",
                    labels={'YoY_pct': 'YoY % Change'},
                    template='plotly_white'
                )
                fig_yoy.update_layout(legend_title_text="Country")
                st.plotly_chart(fig_yoy, use_container_width=True)
            else:
                st.info("No YoY data available for the latest quarter and selected categories.")

            # ==== Heatmap (Single Country) ====
            st.subheader("CPI Heatmap")
            st.markdown("Only meant for a single country:smile:")
            if len(selected_countries) == 1:
                heat_df = df_compare[df_compare['COUNTRY_NAME'] == selected_countries[0]].pivot_table(
                    index='Time',
                    columns='Category',
                    values='OBS_VALUE'
                )
                fig_heat = px.imshow(
                    heat_df.T,
                    aspect='auto',
                    color_continuous_scale='YlOrRd',
                    title=f"CPI Heatmap - {selected_countries[0]}"
                )
                st.plotly_chart(fig_heat, use_container_width=True)

            # ==== Raw Table ====
            with st.expander("View Raw CPI Comparison Table"):
                if len(selected_countries) == 1:
                    country = selected_countries[0]
                    pivot = grouped[grouped['COUNTRY_NAME'] == country].pivot_table(
                        index='Time', columns='Category', values='OBS_VALUE'
                    ).round(2)
                    st.markdown(f"**{country}**")
                    st.dataframe(pivot, use_container_width=True)
                elif len(selected_countries) == 2:
                    c1, c2 = selected_countries
                    pivot1 = grouped[grouped['COUNTRY_NAME'] == c1].pivot_table(index='Time',
                                                                                columns='Category',
                                                                                values='OBS_VALUE').round(2)
                    pivot2 = grouped[grouped['COUNTRY_NAME'] == c2].pivot_table(index='Time',
                                                                                columns='Category',
                                                                                values='OBS_VALUE').round(2)
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**{c1}**")
                        st.dataframe(pivot1, use_container_width=True)
                    with col2:
                        st.markdown(f"**{c2}**")
                        st.dataframe(pivot2, use_container_width=True)
                else:
                    st.info("Please select at least one country to view the data.")
elif selected_page == 'NHA Indicators':
    st.header('National Health Accounts Indicators')
    st.write("This section displays National Health Accounts indicators and their trends.")

    if not df_nha_indicators.empty:
        # Filter out rows with NaN in 'Value' for display and selectors
        df_nha_display = df_nha_indicators.dropna(subset=['Value']).copy()

        st.subheader("Raw Data Sample (Non-Null Values)")
        st.dataframe(df_nha_display.head())  # Display head of filtered data

        # Get unique indicators and years from the filtered DataFrame for selection
        nha_indicators_list = sorted(df_nha_display['Indicators'].unique())
        nha_years_list = sorted(df_nha_display['Year'].dropna().unique().tolist())
        all_nha_countries = sorted(df_nha_display['Countries'].unique())

        # --- Visualization 1: Line Chart - Indicator Trend for Selected Countries ---
        st.subheader("1. Health Expenditure Trend for Selected Countries")

        selected_nha_indicator_line = st.selectbox(
            'Select Indicator for Line Chart',
            nha_indicators_list,
            index=nha_indicators_list.index(
                'Current health expenditure (CHE) as percentage of GDP') if 'Current health expenditure (CHE) as percentage of GDP' in nha_indicators_list else 0,
            key='line_indicator_select'  # Unique key for this selectbox
        )

        selected_nha_countries_line = st.multiselect(
            'Select Countries for Line Chart',
            all_nha_countries,
            default=all_nha_countries[:5]  # Default to first 5 countries
        )

        if selected_nha_indicator_line and selected_nha_countries_line:
            filtered_df_line = df_nha_display[  # Use df_nha_display
                (df_nha_display['Indicators'] == selected_nha_indicator_line) &
                (df_nha_display['Countries'].isin(selected_nha_countries_line))
                ].sort_values(by='Year')  # dropna already done by df_nha_display

            if not filtered_df_line.empty:
                fig_line = px.line(
                    filtered_df_line,
                    x='Year',
                    y='Value',
                    color='Countries',
                    title=f'{selected_nha_indicator_line} Trend for Selected Countries',
                    labels={'Value': selected_nha_indicator_line, 'Year': 'Year'},
                    markers=True  # Show markers on the line
                )
                st.plotly_chart(fig_line, use_container_width=True)
            else:
                st.info("No data available for the selected indicator and countries.")

        # --- Visualization 2: Animated Scatter Plot - Relationship between two Indicators over Time ---
        st.subheader("2. Relationship between Two Health Indicators Over Time (Animated)")

        scatter_indicators_list = sorted(df_nha_display['Indicators'].unique())

        col1, col2 = st.columns(2)
        with col1:
            selected_nha_indicator_x = st.selectbox(
                'Select X-axis Indicator',
                scatter_indicators_list,
                index=scatter_indicators_list.index(
                    'Current health expenditure (CHE) as percentage of GDP') if 'Current health expenditure (CHE) as percentage of GDP' in scatter_indicators_list else 0,
                key='scatter_x_indicator'
            )
        with col2:
            selected_nha_indicator_y = st.selectbox(
                'Select Y-axis Indicator',
                scatter_indicators_list,
                index=scatter_indicators_list.index(
                    'Current health expenditure (CHE) per capita') if 'Current health expenditure (CHE) per capita' in scatter_indicators_list else 0,
                key='scatter_y_indicator'
            )

        # CHANGE: Allow multiple countries for animated scatter plot
        selected_nha_countries_scatter = st.multiselect(
            'Select Countries for Animated Scatter Plot',
            all_nha_countries,
            default=all_nha_countries[:3],  # Default to a few countries for demonstration
            key='scatter_countries_select'  # Changed key
        )

        if selected_nha_indicator_x and selected_nha_indicator_y and selected_nha_countries_scatter:
            # Prepare data for scatter plot with multiple countries
            # Filter df_nha_display for selected indicators AND selected countries
            df_filtered_x = df_nha_display[
                (df_nha_display['Indicators'] == selected_nha_indicator_x) &
                (df_nha_display['Countries'].isin(selected_nha_countries_scatter))
                ].rename(columns={'Value': 'X_Value'})[
                ['Year', 'Countries', 'X_Value']]  # Include 'Countries' for animation_group

            df_filtered_y = df_nha_display[
                (df_nha_display['Indicators'] == selected_nha_indicator_y) &
                (df_nha_display['Countries'].isin(selected_nha_countries_scatter))
                ].rename(columns={'Value': 'Y_Value'})[['Year', 'Countries', 'Y_Value']]  # Include 'Countries'

            # Merge on 'Year' and 'Countries'
            df_scatter = pd.merge(df_filtered_x, df_filtered_y, on=['Year', 'Countries'], how='inner').dropna()

            if not df_scatter.empty:
                # Ensure 'Year' is sorted for animation
                df_scatter_sorted = df_scatter.sort_values(by='Year')

                fig_scatter = px.scatter(
                    df_scatter_sorted,
                    x='X_Value',
                    y='Y_Value',
                    animation_frame='Year',
                    animation_group='Countries',  # Now 'Countries' column is present in df_scatter_sorted
                    color='Countries',  # Color by country to distinguish paths
                    size='X_Value',
                    hover_name='Countries',  # Show country name on hover
                    color_discrete_sequence=px.colors.qualitative.Plotly,
                    title=f'Relationship between {selected_nha_indicator_x} and {selected_nha_indicator_y} over Time',
                    labels={'X_Value': selected_nha_indicator_x, 'Y_Value': selected_nha_indicator_y},
                    range_x=[df_scatter_sorted['X_Value'].min() * 0.9, df_scatter_sorted['X_Value'].max() * 1.1],
                    range_y=[df_scatter_sorted['Y_Value'].min() * 0.9, df_scatter_sorted['Y_Value'].max() * 1.1]
                )

                # Set animation speed
                fig_scatter.layout.updatemenus[0].buttons[0].args[1]['frame']['duration'] = 1000
                fig_scatter.layout.updatemenus[0].buttons[0].args[1]['transition']['duration'] = 500

                # --- IMPORTANT: Add the trail effect ---
                fig_scatter.update_traces(
                    mode='lines+markers',  # Ensure lines are drawn
                    line=dict(width=5),  # Adjust line thickness
                    marker=dict(size=10)  # Adjust marker size
                )
                fig_scatter.layout.updatemenus[0].buttons[0].args[1]["frame"]["redraw"] = True  # Force redraw for trail

                st.plotly_chart(fig_scatter, use_container_width=True)
            else:
                st.info(
                    "No common data available for the selected indicators and countries to create the animated scatter plot.")
        else:
            st.info("Please select two indicators and at least one country for the animated scatter plot.")

        # --- Visualization 3: Bar Chart - Indicator by Country for a Specific Year (MOVED TO BOTTOM) ---
        st.subheader("3. Health Expenditure by Country for a Specific Year")  # Renumbered to 3

        selected_nha_indicator_bar = st.selectbox(
            'Select Indicator for Bar Chart',
            nha_indicators_list,
            index=nha_indicators_list.index(
                'Current health expenditure (CHE) as percentage of GDP') if 'Current health expenditure (CHE) as percentage of GDP' in nha_indicators_list else 0,
            key='bar_indicator_select'  # Unique key for this selectbox
        )
        selected_nha_year_bar = st.selectbox(
            'Select Year for Bar Chart',
            nha_years_list,
            index=len(nha_years_list) - 1 if nha_years_list else 0,  # Default to latest year
            key='bar_year_select'  # Unique key for this selectbox
        )

        if selected_nha_indicator_bar and selected_nha_year_bar:
            filtered_df_bar = df_nha_display[  # Use df_nha_display
                (df_nha_display['Indicators'] == selected_nha_indicator_bar) &
                (df_nha_display['Year'] == selected_nha_year_bar)
                ].sort_values(by='Value', ascending=False)  # dropna already done by df_nha_display

            if not filtered_df_bar.empty:
                fig_bar = px.bar(
                    filtered_df_bar,
                    x='Countries',
                    y='Value',
                    title=f'{selected_nha_indicator_bar} by Country in {selected_nha_year_bar}',
                    labels={'Value': selected_nha_indicator_bar, 'Countries': 'Country'}
                )
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.info("No data available for the selected indicator and year.")

    else:
        st.warning("NHA Indicators data is not available or failed to load.")

st.markdown("---")
st.markdown("Dashboard developed using Streamlit and Plotly.")
