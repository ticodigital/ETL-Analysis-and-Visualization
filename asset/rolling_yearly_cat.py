from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float, Index, text
import yaml
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from matplotlib.ticker import FuncFormatter


# Load database configuration from YAML file
db = yaml.safe_load(open('db.yaml'))
db_url = f"mysql+mysqlconnector://{db['user']}:{db['pwrd']}@{db['host']}/{db['db']}"

# Create an engine
engine = create_engine(db_url)

# Create a connection to the MySQL server
conn = engine.connect()

# Execute the SQL statement
result = conn.execute(text(
    """
SELECT YEAR(Date) AS Year, Description, SUM(Sales) AS TotalSales
FROM mrts
GROUP BY YEAR(Date),Description;
    """
    ))

# Initialize lists to store data
A = "Food services and drinking places"
B = "Food and beverage stores"
C = None
year_A = []
sales_A = []
year_B = []
sales_B = []


# Fetch and process the results
for row in result:
    if row[1] == A:
        year_A.append(datetime(int(row[0]), 1, 1))
        sales_A.append(row[2])
    if row[1] == B:
        year_B.append(datetime(int(row[0]), 1, 1))
        sales_B.append(row[2])

# Close the connection to the MySQL server
conn.close()
engine.dispose()

# Set x ticks
dates = [datetime(year, 1, 1) for year in range(1992, 2022)]

# Set seaborn style
sns.set_style("whitegrid")


sales_df_A = pd.DataFrame({'Year': year_A, 'TotalSales': sales_A})
sales_df_B = pd.DataFrame({'Year': year_B, 'TotalSales': sales_B})

# ROLLING TIME WINDOWS

# Calculate rolling averages for both categories
window_size = 4  # Adjust the window size as needed

sales_df_A['Rolling_Avg'] = sales_df_A['TotalSales'].rolling(window=window_size).mean()
sales_df_B['Rolling_Avg'] = sales_df_B['TotalSales'].rolling(window=window_size).mean()
sales_df_A['Rolling_Max'] = sales_df_A['TotalSales'].rolling(window=window_size).max()
sales_df_B['Rolling_Max'] = sales_df_B['TotalSales'].rolling(window=window_size).max()
sales_df_A['Rolling_Min'] = sales_df_A['TotalSales'].rolling(window=window_size).min()
sales_df_B['Rolling_Min'] = sales_df_B['TotalSales'].rolling(window=window_size).min()
sales_df_A['Rolling_Std'] = sales_df_A['TotalSales'].rolling(window=window_size).std()
sales_df_B['Rolling_Std'] = sales_df_B['TotalSales'].rolling(window=window_size).std()

# Plot the rolling averages
plt.figure(figsize=(12, 6))

plt.plot(sales_df_A['Year'], sales_df_A['Rolling_Max'], marker='<', label= f'Max {A}', color='navy')
plt.plot(sales_df_B['Year'], sales_df_B['Rolling_Max'], marker='<', label= f'Max {B}', color='green')
plt.plot(sales_df_A['Year'], sales_df_A['Rolling_Avg'], marker='o', label= f'Avg {A}', color='navy')
plt.plot(sales_df_B['Year'], sales_df_B['Rolling_Avg'], marker='o', label= f'Avg {B}', color='green')
plt.plot(sales_df_A['Year'], sales_df_A['Rolling_Min'], marker='>', label= f'Min {A}', color='navy')
plt.plot(sales_df_B['Year'], sales_df_B['Rolling_Min'], marker='>', label= f'Min {B}', color='green')

plt.xlabel('Year', fontsize=14, labelpad=10, fontweight='bold', color='navy')
plt.ylabel(f'Rolling Max, Average, and Min ({window_size}-Year Window)', fontsize=14, labelpad=10, fontweight='bold', color='navy')
plt.title(f'Rolling Max, Average, and Min Sales', fontsize=16, pad=20, fontweight='bold', color='navy')
plt.xticks(rotation=45, fontsize=10, ha='right', color='dimgray')
plt.yticks(fontsize=10, color='dimgray')
plt.gca().spines['top'].set_visible(False)
plt.gca().spines['right'].set_visible(False)
plt.grid(axis='y', linestyle='--', alpha=0.5)
plt.legend()

# Add thousands separator to y-axis labels
formatter = FuncFormatter(lambda x, _: '{:,.0f}'.format(x))
plt.gca().yaxis.set_major_formatter(formatter)

plt.tight_layout()
plt.show()

# Plot the rolling averages
plt.figure(figsize=(12, 6))

plt.plot(sales_df_A['Year'], sales_df_A['Rolling_Std'], marker='*', label= f'Std {A}', color='navy')
plt.plot(sales_df_B['Year'], sales_df_B['Rolling_Std'], marker='*', label= f'Std {B}', color='green')


plt.xlabel('Year', fontsize=14, labelpad=10, fontweight='bold', color='navy')
plt.ylabel(f'Rolling Standard Deviation ({window_size}-Year Window)', fontsize=14, labelpad=10, fontweight='bold', color='navy')
plt.title(f'Rolling Standard Deviation Sales', fontsize=16, pad=20, fontweight='bold', color='navy')
plt.xticks(rotation=45, fontsize=10, ha='right', color='dimgray')
plt.yticks(fontsize=10, color='dimgray')
plt.gca().spines['top'].set_visible(False)
plt.gca().spines['right'].set_visible(False)
plt.grid(axis='y', linestyle='--', alpha=0.5)
plt.legend()

# Add thousands separator to y-axis labels
formatter = FuncFormatter(lambda x, _: '{:,.0f}'.format(x))
plt.gca().yaxis.set_major_formatter(formatter)

plt.tight_layout()
plt.show()

'''
# Exponential Moving Averages (EMA) for smoothing
sales_df_A['EMA'] = sales_df_A['TotalSales'].ewm(span=window_size, adjust=False).mean()
sales_df_B['EMA'] = sales_df_B['TotalSales'].ewm(span=window_size, adjust=False).mean()

# Interactive plotting with Plotly
import plotly.graph_objs as go

fig = go.Figure()

fig.add_trace(go.Scatter(x=sales_df_A['Year'], y=sales_df_A['EMA'], mode='lines+markers', name=A, line=dict(color='navy')))
fig.add_trace(go.Scatter(x=sales_df_B['Year'], y=sales_df_B['EMA'], mode='lines+markers', name=B, line=dict(color='green')))

fig.update_layout(
    title=f'Rolling Average Sales (Window: {window_size} Years)',
    xaxis=dict(title='Year', tickangle=-45),
    yaxis=dict(title='Rolling Average Sales', tickformat=','),
    legend=dict(x=0.02, y=0.98),
    plot_bgcolor='rgba(0,0,0,0)'
)

fig.show()
'''