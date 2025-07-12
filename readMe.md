# 🌍 NomadCompass

NomadCompass is a data visualization tool designed to help users — especially digital nomads, expats, and policy researchers — explore and compare economic and health metrics across countries. It combines interactive dashboards, visual insights, and powerful indicators such as Consumer Price Index (CPI), Out-of-Pocket Health Expenditure (OOPS), and healthcare programs.

🔗 **Live App:**  
[Explore the Dashboard](https://sebastianabarca-nomadcompass-appapp-fairyn.streamlit.app/)

---

# Digital Nomad Cost of Living & Health Insights Dashboard

## Project Overview

This project presents a comprehensive **data analysis dashboard** built to assist digital nomads in making informed decisions about their next international destinations. It integrates various macroeconomic and social datasets to offer a granular view of living costs and critical healthcare indicators, essential for a sustainable nomadic lifestyle.

## Purpose

The core purpose of this dashboard is to **demystify the complexities of global relocation for digital nomads**. By providing data-driven comparisons of potential locations based on financial and health metrics, it enables users to accurately budget, plan for healthcare needs, and ultimately select destinations that align with their personal and financial well-being.

## Key Data Sources & Their Relevance

1.  **Consumer Price Index (CPI) Data (IMF - Aggregate & Granular):**
    * **Relevance:** Directly addresses the primary concern of "cost of living."
    * **Aggregate CPI:** Offers an overall snapshot of inflation and general price levels within a country.
    * **Granular CPI (COICOP 1999 Categories):** Provides an in-depth breakdown of expenditures across specific categories (e.g., Food & Non-Alcoholic Beverages, Housing, Health, Transport, Recreation & Culture, Restaurants & Hotels, Miscellaneous Goods & Services). This granularity is vital for nomads to understand how their typical spending patterns will translate in different global contexts.

2.  **Population Data:**
    * **Relevance:** While not a direct cost driver, population data provides crucial demographic context. It can indirectly influence the availability and cost of services, market size, and overall infrastructure, all of which are relevant to a digital nomad's experience.

3.  **National Health Accounts (NHA) Indicator Data:**
    * **Relevance:** Addresses a frequently overlooked but critical aspect of nomadic life: healthcare.
    * NHA indicators offer insights into national health expenditure, funding mechanisms (e.g., public vs. private contributions), and resource distribution within the health system. This information is invaluable for nomads planning for medical access, understanding potential out-of-pocket costs, and assessing a country's commitment to public health.

## Core Functionalities & Features

* **Interactive Country Comparison:** Side-by-side analysis of CPI trends and category-specific costs for selected countries.
* **Granular Expense Visualization:** Detailed charts showing the contribution of individual COICOP categories to the overall CPI.
* **Inflation Trend Analysis (YoY CPI):** Tools to visualize Year-over-Year percentage changes in CPI, both in aggregate and by specific categories.
* **Healthcare Expenditure Insights:** Visualizations and data points derived from NHA indicators to assess healthcare costs and system characteristics.
* **Time-Series Tracking:** Ability to observe and compare how economic and health indicators evolve over various time periods.
* **User-Friendly Interface:** An intuitive and interactive dashboard built with Streamlit, designed for ease of data exploration.

## Target Audience

* **Prospective Employers / Hiring Managers (for Data Analyst roles):** This project serves as a robust portfolio piece, showcasing comprehensive skills in:
    * **Data Acquisition & ETL:** Sourcing and processing data from external APIs (e.g., IMF).
    * **Data Cleaning & Transformation:** Preparing raw data for analysis.
    * **Statistical Analysis:** Deriving insights like YoY changes.
    * **Interactive Dashboard Development:** Building a user-friendly and dynamic data visualization application (Streamlit).
    * **Problem-Solving:** Applying data analysis to a tangible, real-world challenge.
* **Digital Nomads:** Individuals leveraging remote work to travel, who require data-driven assistance for selecting their next temporary or long-term residence.
* **Expatriates & Relocation Planners:** Anyone in the process of moving internationally who needs detailed insights into living expenses and healthcare systems.
* **Economic Researchers & Analysts:** Professionals interested in cross-country comparisons of consumer prices, inflation, and health economics.

## Overall Value

This project bridges the gap between complex global economic data and practical decision-making for digital nomads. By transforming raw indicators into clear, actionable intelligence, it helps reduce uncertainty, facilitates more accurate

## 🛠️ Tech Stack

- **Frontend**: [Streamlit](https://streamlit.io/)
- **Visualization**: [Plotly](https://plotly.com/python/)
- **Data Processing**: `pandas`, `numpy`
- **Deployment**: [Streamlit Community Cloud](https://streamlit.io/cloud)

---

## 📁 Project Structure

NomadCompass/
├── app/
│ └── app.py # Main Streamlit application
├── data/
│ └── *.csv # Economic and health data files
├── .streamlit/
│ └── config.toml # Optional Streamlit config
├── requirements.txt # Python dependencies
└── README.md # This file

## ⚙️ Installation & Running Locally

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/NomadCompass.git
   cd NomadCompass
2. **(Optional) Create a virtual environment:**

    python3 -m venv .venv
    source .venv/bin/activate
3. 
3. **Install dependencies:**
    
    pip install -r requirements.txt

4.**Run the app:**

    streamlit run app/app.py


## 📌 Future Improvements
--Add map-based visualizations for global snapshots
--Enable bookmarking or saving custom country comparisons
--Incorporate nomad-specific indices like remote work friendliness or visa access
--Support monthly CPI and longer time-series analytics
--Create a system to allow the user to rank and or give weight to certain factors and give every country a score based
on factors

## 🧠 Inspiration & Purpose
As a global traveler with nomadic dreams, and a penchant for data. I want to create a system to help myself and other
choose their next stay

## 🤝 Contributing
Feel free to fork the project, suggest improvements, or submit PRs. Whether it's adding data sources, refining UI/UX, or improving performance — all contributions are welcome!

## 📄 License
MIT License. See LICENSE for details.

##🧭 Made with ❤️ by Sebastian Abarca
