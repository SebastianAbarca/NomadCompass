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
    st.header(f"Aggregate CPI Data")

    if df_aggregate_cpi.empty:
        st.warning("Aggregate CPI data not loaded.")
    else:

        # Extract unique countries for selection
        countries = df_aggregate_cpi['COUNTRY_NAME'].unique()
        selected_countries = st.multiselect(
            "Select one or more countries to visualize CPI over time:",
            options=sorted(countries),
            default=['Aruba']  # adjust default as needed
        )

        # Prepare for both plotting and stability
        df_cpi = df_aggregate_cpi.copy()
        df_cpi['Year'] = df_cpi['TIME_PERIOD'].str.extract(r'(\d{4})').astype(int)
        df_cpi['Q_Num'] = df_cpi['TIME_PERIOD'].str.extract(r'Q([1-4])').astype(int)
        df_cpi['Time'] = pd.to_datetime(df_cpi['Year'].astype(str) + '-Q' + df_cpi['Q_Num'].astype(str))
        df_cpi = df_cpi.sort_values(['COUNTRY_NAME', 'Time'])

        # Calculate YoY % change (Q1 2020 vs Q1 2019, etc.)
        df_cpi['YoY_change'] = df_cpi.groupby('COUNTRY_NAME')['OBS_VALUE'].pct_change(periods=4) * 100

        # ==== Visualization of CPI Over Time ====
        if selected_countries:
            df_filtered = df_cpi[df_cpi['COUNTRY_NAME'].isin(selected_countries)].copy()

            fig = px.line(
                df_filtered,
                x='Time',
                y='OBS_VALUE',
                color='COUNTRY_NAME',
                markers=True,
                labels={'Time': 'Quarter', 'OBS_VALUE': 'CPI Value'},
                title='Aggregate CPI Over Time by Country',
                template='plotly_white'
            )
            fig.update_layout(hovermode='x unified', title_font_size=20)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Please select at least one country to display the chart.")

        # ==== Stability Analysis ====
        st.subheader("Top 10 Most Stable Countries (Lowest CPI Volatility)")

        stability_df = (
            df_cpi.groupby('COUNTRY_NAME')['YoY_change']
            .std()
            .dropna()
            .sort_values()
            .reset_index()
            .rename(columns={'YoY_change': 'YoY_StdDev'})
        )

        top_stable = stability_df.head(10)

        col1, col2 = st.columns([4, 3]) ##DONT CHANGE RATIO
        with col1:
            fig_stab = px.bar(
                top_stable,
                x='COUNTRY_NAME',
                y='YoY_StdDev',
                text=top_stable['YoY_StdDev'].round(2),
                labels={'YoY_StdDev': 'Std. Dev of YoY % Change'},
                title='Top 10 CPI Stable Countries',
                template='plotly_white'
            )
            fig_stab.update_traces(marker_color='seagreen')
            st.plotly_chart(fig_stab, use_container_width=True)  # <--- make sure this is here

        with col2:
            st.dataframe(top_stable.set_index('COUNTRY_NAME').round(2), use_container_width=True)  # <--- this helps too

        with st.expander("See Full Country Stability Table"):
            st.dataframe(stability_df.set_index('COUNTRY_NAME').round(2))
elif selected_page == 'Categorical CPI':
    st.header("Categorical CPI Data")

    if df_granular_cpi.empty:
        st.warning("Granular CPI data not loaded.")
    else:
        # Map COICOP codes to readable names (expand as needed)
        coicop_labels = {
            "CP01": "Food & Non-Alcoholic Beverages",
            "CP04": "Housing",
            "CP06": "Health",
            "CP07": "Transport",
            "CP09": "Recreation & Culture",
            "CP11": "Restaurants & Hotels"
        }

        df_granular_cpi
        # Add readable category name
        df_granular_cpi['Category'] = df_granular_cpi['COICOP_1999'].map(coicop_labels).fillna(
            df_granular_cpi['COICOP_1999'])

        # Extract year and quarter, convert to datetime
        df_granular_cpi['Year'] = df_granular_cpi['TIME_PERIOD'].str.extract(r'(\d{4})').astype(int)
        df_granular_cpi['Q_Num'] = df_granular_cpi['TIME_PERIOD'].str.extract(r'Q([1-4])').astype(int)
        df_granular_cpi['Time'] = pd.to_datetime(
            df_granular_cpi['Year'].astype(str) + '-Q' + df_granular_cpi['Q_Num'].astype(str))

        # Sort for plotting
        df_granular_cpi = df_granular_cpi.sort_values(['COUNTRY_NAME', 'Time'])

        # Country selection
        selected_countries = st.multiselect(
            "Select up to 2 countries to compare CPI breakdown:",
            sorted(df_granular_cpi['COUNTRY_NAME'].unique()),
            default=["United States"],  # adjust default as needed
            max_selections=2
        )

        if selected_countries:
            df_compare = df_granular_cpi[df_granular_cpi['COUNTRY_NAME'].isin(selected_countries)].copy()

            # Group and sum CPI values per Time, Country, Category
            grouped = (
                df_compare.groupby(['Time', 'COUNTRY_NAME', 'Category'])['OBS_VALUE']
                .sum()
                .reset_index()
            )

            # Faceted stacked bar chart
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

            fig.update_layout(
                barmode='stack',
                title_font_size=20,
                legend_title_text='Category',
                hovermode='x unified'
            )

            st.plotly_chart(fig, use_container_width=True)

            with st.expander("View Raw CPI Comparison Table"):
                if len(selected_countries) == 1:
                    country = selected_countries[0]
                    pivot = grouped[grouped['COUNTRY_NAME'] == country].pivot_table(
                        index='Time',
                        columns='Category',
                        values='OBS_VALUE'
                    ).round(2)
                    st.markdown(f"**{country}**")
                    st.dataframe(pivot, use_container_width=True)

                elif len(selected_countries) == 2:
                    country_1 = selected_countries[0]
                    country_2 = selected_countries[1]

                    pivot_1 = grouped[grouped['COUNTRY_NAME'] == country_1].pivot_table(
                        index='Time',
                        columns='Category',
                        values='OBS_VALUE'
                    ).round(2)

                    pivot_2 = grouped[grouped['COUNTRY_NAME'] == country_2].pivot_table(
                        index='Time',
                        columns='Category',
                        values='OBS_VALUE'
                    ).round(2)

                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**{country_1}**")
                        st.dataframe(pivot_1, use_container_width=True)

                    with col2:
                        st.markdown(f"**{country_2}**")
                        st.dataframe(pivot_2, use_container_width=True)

                    st.markdown(f"**Note: both of these are in PPP")

                else:
                    st.info("Please select at least one country to view the data.")