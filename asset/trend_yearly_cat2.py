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
A = "Men's clothing stores"
B = "Women's clothing stores"
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

# TREND

# Plot the data with seaborn
plt.figure(figsize=(12, 6))
sns.lineplot(x=year_A, y=sales_A, marker='o', color='navy', markerfacecolor='red', markersize=4, linewidth=2, linestyle='-', alpha=0.7, label=A)
sns.lineplot(x=year_B, y=sales_B, marker='o', color='green', markerfacecolor='red', markersize=4, linewidth=2, linestyle='-', alpha=0.7, label=B)
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

sales_dfs = [sales_df_A, sales_df_B]

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

# PERCENTAGE OF CONTRIBUTION

# Divide by the sum of both
plt.figure(figsize=(12, 6))
plt.plot(sales_df_A['Year'], sales_df_A['TotalSales'] / (sales_df_A['TotalSales']+sales_df_B['TotalSales']), marker='o', label="Men's Clothing", color='navy')
plt.plot(sales_df_B['Year'], sales_df_B['TotalSales'] / (sales_df_A['TotalSales']+sales_df_B['TotalSales']), marker='o', label="Women's Clothing", color='green')

plt.xlabel('Year', fontsize=14, labelpad=10, fontweight='bold', color='navy')
plt.ylabel('Percentage of Total Sales', fontsize=14, labelpad=10, fontweight='bold', color='navy')
plt.title('Percentage Contribution of Men\'s and Women\'s Clothing Stores to Total Sales', fontsize=16, pad=20, fontweight='bold', color='navy')
plt.xticks(rotation=45, fontsize=10, ha='right', ticks=dates, labels=[date.strftime('%Y') for date in dates], color='dimgray')
plt.yticks(fontsize=10, color='dimgray')
plt.gca().spines['top'].set_visible(False)
plt.gca().spines['right'].set_visible(False)
plt.grid(axis='y', linestyle='--', alpha=0.5)
plt.legend()

# Set y-axis tick labels to percentage format
formatter = FuncFormatter(lambda y, _: '{:.0%}'.format(y))
plt.gca().yaxis.set_major_formatter(formatter)

plt.tight_layout()
plt.show()

# ROLLING TIME WINDOWS

# Calculate rolling averages for both categories
window_size = 5  # Adjust the window size as needed

sales_df_A['Rolling_Avg'] = sales_df_A['TotalSales'].rolling(window=window_size).mean()
sales_df_B['Rolling_Avg'] = sales_df_B['TotalSales'].rolling(window=window_size).mean()

# Plot the rolling averages
plt.figure(figsize=(12, 6))

plt.plot(sales_df_A['Year'], sales_df_A['Rolling_Avg'], marker='o', label="Men's Clothing", color='navy')
plt.plot(sales_df_B['Year'], sales_df_B['Rolling_Avg'], marker='o', label="Women's Clothing", color='green')

plt.xlabel('Year', fontsize=14, labelpad=10, fontweight='bold', color='navy')
plt.ylabel(f'Rolling Average ({window_size}-Year Window)', fontsize=14, labelpad=10, fontweight='bold', color='navy')
plt.title(f'Rolling Average Sales for Men\'s and Women\'s Clothing Stores', fontsize=16, pad=20, fontweight='bold', color='navy')
plt.xticks(rotation=45, fontsize=10, ha='right', color='dimgray')
plt.yticks(fontsize=10, color='dimgray')
plt.gca().spines['top'].set_visible(False)
plt.gca().spines['right'].set_visible(False)
plt.grid(axis='y', linestyle='--', alpha=0.5)
plt.legend()

plt.tight_layout()
plt.show()