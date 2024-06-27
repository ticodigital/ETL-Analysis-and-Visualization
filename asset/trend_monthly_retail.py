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
SELECT date, Description, CAST(sum(sales) as UNSIGNED) as sales
FROM mrts
WHERE 
Description IN ('Sporting goods stores','Book stores','Hobby, toy, and game stores')
AND Date >= '2000-01-01'
GROUP BY 1, 2
ORDER BY 1, 2;
    """
    ))

# Initialize lists to store data
A = 'Sporting goods stores'
B = 'Book stores'
C = 'Hobby, toy, and game stores'
D = None

month_A = []
sales_A = []
month_B = []
sales_B = []
month_C = []
sales_C = []
month_D = []
sales_D = []

# Fetch and process the results
"""
for row in result:
    print(row)
"""
for row in result:
    if row[1] == A:
        month_A.append(row[0])
        sales_A.append(row[2])
    if row[1] == B:
        month_B.append(row[0])
        sales_B.append(row[2])
    if row[1] == C:
        month_C.append(row[0])
        sales_C.append(row[2])

# Close the connection to the MySQL server
conn.close()
engine.dispose()

# Set x ticks
dates = [datetime(year, 1, 1) for year in range(2000, 2022)]

# Set seaborn style
sns.set_style("whitegrid")

# Plot the data with seaborn
plt.figure(figsize=(12, 6))
sns.lineplot(x=month_A, y=sales_A, marker='o', color='navy', markerfacecolor='red', markersize=4, linewidth=2, linestyle='-', alpha=0.7, label=A)
sns.lineplot(x=month_B, y=sales_B, marker='o', color='green', markerfacecolor='darkgreen', markersize=4, linewidth=2, linestyle='-', alpha=0.7, label=B)
sns.lineplot(x=month_C, y=sales_C, marker='o', color='orange', markerfacecolor='darkorange', markersize=4, linewidth=2, linestyle='-', alpha=0.7, label=C)

plt.xlabel('Date', fontsize=14, labelpad=10, fontweight='bold', color='navy')
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