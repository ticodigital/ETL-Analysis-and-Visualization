# ETL, Analysis, and Visualization

## Abstract
This project aimed to extract insights from a complex, multi-sheet Excel file using ETL (Extract, Transform, Load) and analysis techniques in one integrated ETL and analysis process in Python code. Data was loaded into a MySQL database and analyzed to identify business resilience during global events like COVID-19 and the 2008 financial crisis, understand seasonal trends across different business lines, and uncover relationships between businesses. The project employed pandas for data manipulation, SQLAlchemy for database interaction, and the MySQL connector for database access. Key findings included the identification of resilient and vulnerable business lines, the presence of seasonality within specific sectors, and potential relationships among businesses. These insights can inform strategic decision-making and risk mitigation strategies.

## Introduction
This project transforms raw data from an Excel file into a structured format, analyzes its trends, and visualizes the key insights. I followed an ETL (Extract, Transform, Load) approach to prepare the data for analysis and visualization.

Extraction involves converting the original .xls file to a more manageable .xlsx format and loading it into a Python environment using pandas. Transformation cleanses and restructures the data to fit the defined database entities. It includes consolidating data from multiple sheets into a single dataframe, adding and removing columns, handling missing values, and rearranging the data structure to facilitate analysis by transforming the monthly data structure into date-stamped rows.

The Load stage utilizes Python libraries like pandas, SQLAlchemy, YAML, and the MySQL connector to create a database and import the prepared dataframe. Then, define the database schema and indexes to ensure efficient data storage and retrieval.

Finally, analysis and visualization leverage SQL queries facilitated by Seaborn and matplotlib visualization libraries, SQLAlchemy, and MySQL connector to extract meaningful insights from the prepared data. These insights include visualizing trends, percentage changes, percentage contributions, rolling window analysis, and communicating the findings.

This project demonstrates how data can be transformed from a raw state into a valuable resource for informed decision-making through an efficient ETL process and insightful analysis and visualization techniques.
