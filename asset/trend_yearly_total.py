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
SELECT YEAR(Date) AS Year, SUM(Sales) AS TotalSales
FROM mrts
WHERE LENGTH(NAICS) = 3
GROUP BY YEAR(Date);
    """
    ))

# Initialize lists to store data
A = 'Total sales'
year_A = []
sales_A = []


# Fetch and process the results
for row in result:
    year_A.append(datetime(int(row[0]), 1, 1))
    sales_A.append(row[1])

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
sales_df = pd.DataFrame({'Year': year_A, 'TotalSales': sales_A})
sales_df.sort_values(by='Year', ascending=True, inplace=True)
sales_df['Sales_Pct_Change'] = sales_df['TotalSales'].pct_change()

# Plot the data with seaborn
plt.figure(figsize=(12, 6))
sns.lineplot(data=sales_df, x='Year', y='Sales_Pct_Change', marker='o', color='navy', markerfacecolor='red', markersize=4, linewidth=2, linestyle='-', alpha=0.7)
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

plt.tight_layout()
plt.show()