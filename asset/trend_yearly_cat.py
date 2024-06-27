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
A = 'Sporting goods stores'
B = 'Book stores'
C = 'Hobby, toy, and game stores'
year_A = []
sales_A = []
year_B = []
sales_B = []
year_C = []
sales_C = []

# Fetch and process the results
for row in result:
    if row[1] == A:
        year_A.append(datetime(int(row[0]), 1, 1))
        sales_A.append(row[2])
    if row[1] == B:
        year_B.append(datetime(int(row[0]), 1, 1))
        sales_B.append(row[2])
    if row[1] == C:
        year_C.append(datetime(int(row[0]), 1, 1))
        sales_C.append(row[2])

# Close the connection to the MySQL server
conn.close()
engine.dispose()

# Set x ticks
dates = [datetime(year, 1, 1) for year in range(1992, 2022)]

# Set seaborn style
sns.set_style("whitegrid")

# TREND

# Plot the data with seaborn
plt.figure(figsize=(12, 6))
sns.lineplot(x=year_A, y=sales_A, marker='o', color='navy', markerfacecolor='red', markersize=4, linewidth=2, linestyle='-', alpha=0.7, label=A)
sns.lineplot(x=year_B, y=sales_B, marker='o', color='green', markerfacecolor='red', markersize=4, linewidth=2, linestyle='-', alpha=0.7, label=B)
sns.lineplot(x=year_C, y=sales_C, marker='o', color='orange', markerfacecolor='red', markersize=4, linewidth=2, linestyle='-', alpha=0.7, label=C)
plt.xlabel('Year', fontsize=14, labelpad=10, fontweight='bold', color='navy')
plt.ylabel('Sales', fontsize=14, labelpad=10, fontweight='bold', color='navy')
plt.title('Sales Over Time', fontsize=16, pad=20, fontweight='bold', color='navy')
plt.xticks(rotation=45, fontsize=10, ha='right', ticks=dates, labels=[date.strftime('%Y') for date in dates], color='dimgray')
plt.yticks(fontsize=10, color='dimgray')
plt.gca().spines['top'].set_visible(False)
plt.gca().spines['right'].set_visible(False)
plt.grid(axis='y', linestyle='--', alpha=0.5)

# Add thousands separator to y-axis labels
formatter = FuncFormatter(lambda x, _: '{:,.0f}'.format(x))
plt.gca().yaxis.set_major_formatter(formatter)

plt.tight_layout()
plt.show()

# PERCENTAGE CHANGE

# Calculate percentage change for total sales
sales_df_A = pd.DataFrame({'Year': year_A, 'TotalSales': sales_A})
sales_df_B = pd.DataFrame({'Year': year_B, 'TotalSales': sales_B})
sales_df_C = pd.DataFrame({'Year': year_C, 'TotalSales': sales_C})

sales_dfs = [sales_df_A, sales_df_B, sales_df_C]

for df in sales_dfs:
    df.sort_values(by='Year', ascending=True, inplace=True)
    df['Sales_Pct_Change'] = df['TotalSales'].pct_change()

# Plot the data with seaborn
plt.figure(figsize=(12, 6))

# Sales A
sales_df_A.sort_values(by='Year', ascending=True, inplace=True)
sales_df_A['Sales_Pct_Change'] = sales_df_A['TotalSales'].pct_change()
sns.lineplot(data=sales_df_A, x='Year', y='Sales_Pct_Change', marker='o', label=A, color='navy')

# Sales B
sales_df_B.sort_values(by='Year', ascending=True, inplace=True)
sales_df_B['Sales_Pct_Change'] = sales_df_B['TotalSales'].pct_change()
sns.lineplot(data=sales_df_B, x='Year', y='Sales_Pct_Change', marker='o', label=B, color='green')

# Sales C
sales_df_C.sort_values(by='Year', ascending=True, inplace=True)
sales_df_C['Sales_Pct_Change'] = sales_df_C['TotalSales'].pct_change()
sns.lineplot(data=sales_df_C, x='Year', y='Sales_Pct_Change', marker='o', label=C, color='orange')

plt.xlabel('Year', fontsize=14, labelpad=10, fontweight='bold', color='navy')
plt.ylabel('Sales Percentage Change', fontsize=14, labelpad=10, fontweight='bold', color='navy')
plt.title('Percentage Change in Sales Over Time', fontsize=16, pad=20, fontweight='bold', color='navy')
plt.xticks(rotation=45, fontsize=10, ha='right', ticks=dates, labels=[date.strftime('%Y') for date in dates], color='dimgray')
plt.yticks(fontsize=10, color='dimgray')
plt.gca().spines['top'].set_visible(False)
plt.gca().spines['right'].set_visible(False)
plt.grid(axis='y', linestyle='--', alpha=0.5)

# Set y-axis tick labels to percentage format
formatter = FuncFormatter(lambda y, _: '{:.0%}'.format(y))
plt.gca().yaxis.set_major_formatter(formatter)

plt.legend()
plt.tight_layout()
plt.show()