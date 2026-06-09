import pandas as pd
import os
import urllib.parse
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

DB_USERNAME = os.getenv('DB_USERNAME')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_DATABASE = os.getenv('DB_DATABASE_F')   # keep your existing env var name

# Validate that all required env vars were actually loaded
missing = [k for k, v in {
    'DB_USERNAME': DB_USERNAME, 'DB_PASSWORD': DB_PASSWORD,
    'DB_HOST': DB_HOST, 'DB_PORT': DB_PORT, 'DB_DATABASE_F': DB_DATABASE,
}.items() if not v]
if missing:
    raise EnvironmentError(f"Missing environment variables: {missing}")

# Percent-encode the password so special characters (@, :, /, %) don't
# break the SQLAlchemy connection URL parser
DB_PASSWORD_ENCODED = urllib.parse.quote_plus(DB_PASSWORD)

# 1. Load the DataFrame
df = pd.read_excel('data/original_dataset/farmer_data.xlsx')

# 2. Build the engine
path_format = f'mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD_ENCODED}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}'

engine = create_engine(path_format)

data_folder = r"data/original_dataset/"

xlsx_files = [file for file in os.listdir(
    data_folder) if file.endswith("data.xlsx")]

for file in xlsx_files:
    # Full path to dataset
    file_path = os.path.join(data_folder, file)

    # Read dataset
    df = pd.read_excel(file_path)

    # Create table name from filename
    table_name = os.path.splitext(file)[0].lower()

    # Load into MySQL,  Options: fail, replace, append
    df.to_sql(name=table_name, con=engine,
              if_exists="replace", index=False)

    print(f"Loaded '{file}' into table '{table_name}'")

print('\nReport: All MySQL tables created successfully.')
