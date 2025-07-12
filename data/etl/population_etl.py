import pandas as pd
import os


df = pd.read_csv('../world_population.csv')
print(df.columns)
id_vars = [
    'Rank', 'CCA3', 'Country/Territory', 'Capital', 'Continent',
    'Area (km²)', 'Density (per km²)', 'Growth Rate', 'World Population Percentage'
]

year_columns = [
    '2022 Population', '2020 Population', '2015 Population',
    '2010 Population', '2000 Population', '1990 Population',
    '1980 Population', '1970 Population'
]

# Melt the DataFrame
df_melted = pd.melt(df,
                    id_vars=id_vars,
                    value_vars=year_columns,
                    var_name='Year',
                    value_name='Population')

# Extract the year from the 'Year' column (e.g., '2022 Population' becomes '2022')
df_melted['Year'] = df_melted['Year'].str.replace(' Population', '')

print(df_melted.columns)
df_melted = df_melted.drop(columns=['Capital', 'Continent'])
print(df_melted.columns)

#df_melted.to_csv('world_population_data.csv', index=False)