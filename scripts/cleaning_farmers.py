# Import relevant dependencies
from urllib.parse import quote_plus
import pandas as pd
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine


def clean_northern_farmer_names(path: str = 'data/original_dataset/farmer_data.xlsx'):
    """
    Clean Northern farmers' data for ingestion.
    Dumps csv.
    Returns Pandas Dataframe.    
    """
    # Load Excel file
    df = pd.read_excel(path)

    # Rename columns
    df.columns = ['name',
                  'telephone_no',
                  'crops_planted',
                  'yet_to_plant',
                  'harvest_date',
                  'location',
                  'district',
                  'region']
    # Select object data types
    object_columns = df.select_dtypes(include='object').columns.to_list()

    # Clean and standardize
    for column in object_columns:
        missing = 'Nothing'
        df[column] = df[column].fillna(missing)
        df[column] = df[column].apply(lambda x: x.title())

    # Remove those planting nothing
    df = df[df['crops_planted'] != 'Nothing']

    # Remove spaces
    df['crops_planted'] = df['crops_planted'].apply(
        lambda x: x.replace(' ', ''))

    # Change onion to onions
    df['crops_planted'] = df['crops_planted'].apply(
        lambda x: x.replace('Onion', 'Onions'))

    # Change pepper to peppers(fresh)
    df['crops_planted'] = df['crops_planted'].apply(
        lambda x: x.replace('Pepper', 'Peppers (fresh)'))

    # Change rice to rice(local)
    df['crops_planted'] = df['crops_planted'].apply(
        lambda x: x.replace('Rice', 'Rice (local)'))

    # Change tomatoes to tomatoes(local)
    df['crops_planted'] = df['crops_planted'].apply(
        lambda x: x.replace('Tomatoes', 'Tomatoes (local)'))

    # Change tomatoes to tomatoes(local)
    df['crops_planted'] = df['crops_planted'].apply(
        lambda x: x.replace('Tomato', 'Tomatoes (local)') if x == 'Tomato' else x)

    # Remove spaces from regions
    df['region'] = df['region'].apply(
        lambda x: x.replace('Greater Accra ', 'Greater Accra') if x == 'Greater Accra ' else x)

    # Save the file
    df.to_csv('data/original_dataset/farmer_data.csv')
    return df


def ingest_northern_farmer_names(df: pd.DataFrame = None) -> None:
    """
    Cleans farmer names and ingests the dataframe into MySQL.
    """

    # Load environment variables
    load_dotenv()

    # Generate dataframe if not provided
    if df is None:
        df = clean_northern_farmer_names()

    # Database configuration
    username = os.getenv("DB_USERNAME")
    password = os.getenv("DB_PASSWORD")
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "3306")
    database = os.getenv("DB_DATABASE_F")

    # Validate credentials
    if not all([username, password, host, database]):
        raise ValueError(
            "Missing database credentials. Check your .env file."
        )

    # Encode password to handle special characters
    password = quote_plus(password)

    # Create connection
    connection_string = (
        f"mysql+pymysql://{username}:{password}"
        f"@{host}:{port}/{database}"
    )

    engine = create_engine(
        connection_string,
        pool_pre_ping=True
    )

    # Test connection
    with engine.connect() as connection:
        print("MySQL connection successful ✅")

    # Upload dataframe
    df.to_sql(
        name="new_farmers",
        con=engine,
        if_exists="replace",
        index=False
    )

    print("Ingestion done. ✅")


ingest_northern_farmer_names()
