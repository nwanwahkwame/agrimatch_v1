# Steps:

#     1. Connect Python to `crop_database` MySQL database.
#     2. Load crop table datasets from crop_table folder.
#     3. Automatically detect CSV files.
#     4. Store each dataset as a table in MySQL using SQLAlchemy.
#     5. Ensure MySQL server is running.

# Dependencies:

#     1. pandas
#     2. sqlalchemy
#     3. pymysql if saving to MySQL
#     4. mysqlclient if saving to MariaDB


# Import relevant dependencies
import os
import pandas as pd
from sqlalchemy import create_engine

# Step 4-----------------------------------------------------------------


def sql_processor():
    """
    Retrieves all crop tables from folder and stores them in MySQL database.
    """

    # MySQL database configuration: local
    USERNAME = "root"
    PASSWORD = "root"
    HOST = "localhost"
    PORT = "3306"
    DATABASE = "crop_database"

    # SQLAlchemy connection
    connection_string = (
        f"mysql+pymysql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}")

    # Create SQLAlchemy engine
    engine = create_engine(connection_string)

    print('-'*50)
    print('Step 4 initiated: Storing data in MySQL ✅\n')
    print(f"Connected to {DATABASE} successfully.\n")

    # Crop data path
    data_folder = r"data/crop_splits/"

    # List all CSV files in the folder
    csv_files = [file for file in os.listdir(
        data_folder) if file.endswith(".csv")]

    print("Datasets found:")
    for file in csv_files:
        print("-", file)

    print('')

    # Load each dataset into MySQL
    for file in csv_files:

        # Full path to dataset
        file_path = os.path.join(data_folder, file)

        # Read dataset
        df = pd.read_csv(file_path)

        # Create table name from filename
        table_name = os.path.splitext(file)[0].lower()

        # Load into MySQL,  Options: fail, replace, append
        df.to_sql(name=table_name, con=engine,
                  if_exists="replace", index=False)

        print(f"Loaded '{file}' into table '{table_name}'")

    print('\nReport: All MySQL tables created successfully.')
