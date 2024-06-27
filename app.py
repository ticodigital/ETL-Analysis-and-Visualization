from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Date, Float, Index, text
import yaml
import pandas as pd

#FUNCTIONS

# Define a function to calculate the length of each NAICS code
def calculate_length(naics_code):
    return len(naics_code)

# Define a function to extract the year from the 'Year' column
def extract_year(sheet_name):
    return int(sheet_name)

#EXTRACT

# Open the Excel file
xlsx = pd.ExcelFile('asset/mrtssales92-present.xlsx')

#TRANSFORM

# Initialize starting and ending indices
start_index = None
end_index = None

# List to store raw datasets from each sheet
raw_datasets = []

# Loop over all the sheets in the Excel file
for sheet_name in xlsx.sheet_names:
    if sheet_name == '2021':
        continue  # Skip the sheet named '2021'
    
    # Read data from the current sheet
    df = pd.read_excel(xlsx, sheet_name=sheet_name, dtype={'NAICS': str})
    
    # Rename columns
    df.columns = ['NAICS', 'Description', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12','total']
    
    # Convert the NAICS column to string data type
    df['NAICS'] = df['NAICS'].astype(str)
    
    # Find the starting index where 'code' is equal to '441'
    if start_index is None:
        start_index = df.index[df['NAICS'] == '441'][0]
    
    # Find the ending index where 'code' is equal to '722513, 722514, 722515'
    if end_index is None:
        end_index = df.index[df['NAICS'] == '722513, 722514, 722515'][0]
    
    # Get the raw_dataset using iloc
    raw_dataset = df.iloc[start_index:end_index + 1]

    # Add a column with the length of NAICS at index 0
    raw_dataset.insert(0, 'NAICS_LEN', raw_dataset['NAICS'].apply(calculate_length))
    
    # Add a column with the NOT ADJUSTED label at index 0
    raw_dataset.insert(0, 'Adjusted', False)
    
    # Add a column with the sheet name at index 0
    raw_dataset.insert(0, 'Year', sheet_name)
    
    # Append the raw_dataset to the list
    raw_datasets.append(raw_dataset)

# Concatenate all raw datasets into one DataFrame
consolidated_df = pd.concat(raw_datasets, ignore_index=True)

# Drop the 'total' column
consolidated_df.drop(columns=['total'], inplace=True)

# Replace "(S)"and "(NA)" with 0 in all numeric columns
consolidated_df.iloc[:, 5:] = consolidated_df.iloc[:, 5:].replace({'(S)': 0,'(NA)':0})

# Export to CSV
# consolidated_df.to_csv('consolidated_data.csv', index=False)

# Melt the DataFrame to transform month columns into rows
melted_df = pd.melt(consolidated_df, id_vars=['Year', 'Adjusted', 'NAICS', 'NAICS_LEN', 'Description'],
                    var_name='Month', value_name='Sales')

# Extract the year from the 'Year' column
melted_df['Year'] = melted_df['Year'].apply(extract_year)

# Create a date stamp using the year and month
melted_df['Date'] = pd.to_datetime(melted_df['Year'].astype(str) + '-' + melted_df['Month'], format='%Y-%m')

# Drop the 'Year' and 'Month' columns
melted_df.drop(columns=['Year', 'Month'], inplace=True)

# Export the melted DataFrame to CSV
melted_df.to_csv('melted_data.csv', index=False)

#LOAD
# Load database configuration from YAML file
db = yaml.safe_load(open('db.yaml'))
db_url = f"mysql+mysqlconnector://{db['user']}:{db['pwrd']}@{db['host']}"

# Create engine and connect to MySQL database using SQLAlchemy
engine = create_engine(db_url)

# Create a connection to the MySQL server
conn = engine.connect()

# Execute the SQL statement to create the new database
conn.execute(text("DROP DATABASE IF EXISTS mrts"))
conn.execute(text("CREATE DATABASE IF NOT EXISTS mrts"))

# Close the connection to the MySQL server
conn.close()

# Update the db_url to include the new database
db_url = f"mysql+mysqlconnector://{db['user']}:{db['pwrd']}@{db['host']}/{db['db']}"

# Create a new engine with the updated db_url
engine = create_engine(db_url)

# Define table schema using SQLAlchemy
metadata = MetaData()
mrts = Table('mrts', metadata,
                     Column('mrtsID', Integer, primary_key=True, autoincrement=True),
                     Column('Adjusted', String(99), nullable=False),
                     Column('NAICS', String(99)),
                     Column('NAICS_LEN', String(99)),
                     Column('Description', String(200)),
                     Column('Sales', Float),
                     Column('Date', Date))

# Define indexes
mrtsID_index = Index('mrtsID', mrts.c.mrtsID, unique=False)
NAICS_index = Index('NAICS', mrts.c.NAICS, unique=False)
Date_index = Index('Date', mrts.c.Date, unique=False)

# Create table in the database with indexes and options
metadata.create_all(engine, checkfirst=True)

# Insert data into the table
melted_df.to_sql(name='mrts', con=engine, if_exists='append', index=False)

# Commit changes and close the connection
conn.commit()
conn.close()
engine.dispose()

print("Melted DataFrame exported to CSV and MySQL.")