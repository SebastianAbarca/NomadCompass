# 🌍 NomadCompass

NomadCompass is a data visualization tool designed to help users — especially digital nomads, expats, and policy researchers — explore and compare economic and health metrics across countries. It combines interactive dashboards, visual insights, and powerful indicators such as Consumer Price Index (CPI), Out-of-Pocket Health Expenditure (OOPS), and healthcare programs.

🔗 **Live App:**  
[Explore the Dashboard](https://sebastianabarca-nomadcompass-appapp-fairyn.streamlit.app/)

---

## 🚀 Features

- **Interactive CPI Explorer**
  - View **Aggregate CPI trends** over time by country
  - Analyze inflation volatility and rank countries by CPI **stability**
  - Select multiple countries and visualize comparative CPI evolution

- **Categorical CPI Viewer**
  - Drill down into CPI components like **housing**, **transport**, and **health**
  - Learn about the **COICOP** classification used in international statistics

- **Health Spending Dashboard**
  - Explore **National Health Account (NHA)** indicators
  - Understand **Out-of-Pocket Expenditure (OOPS)** per capita (PPP-adjusted)
  - Get detailed descriptions and context for health categories (e.g. curative care, immunizations)

- **Educational Tooltips & Expanders**
  - Embedded definitions and “learn more” sections
  - Designed to explain economic concepts like **Purchasing Power Parity (PPP)** for broader audiences

---

## 📊 Data Sources

- **IMF CPI Data**: Quarterly consumer price index data for aggregate and categorized consumption  
- **National Health Accounts (NHA)**: Per capita health expenditure data by category and country  
- **PPP Adjustment**: Uses World Bank/IMF conversion factors for standardizing comparisons

---

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
