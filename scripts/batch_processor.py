# Import relevant dependencies
import pandas as pd
from glob import glob
import os

# Step 3 ----------------------------------------------------------------------------


# Find all CSV files in crop directory
crop_files = glob(f"data/crop_splits/*.csv")

# Process each crop dataset


def batch_processing(crop_files=crop_files):
    """
    Batch processes the CSV files in determined path.

    Parameters:
    crop_file = This is a glob instance that retrieves all files from a given path.
    """

    print('-'*50)
    print('Step 3 initiated: Data cleaning ✅\n')

    for index, file in enumerate(crop_files, start=1):
        df = pd.read_csv(file)
        print(f"Processed file no. {index}: {file}\n")

        # Drop price_type, price_flag, and market_id columns
        df.drop(['price_type', 'price_flag', 'market_id',
                'market_sold_at'], axis=1, inplace=True)  # don't assign

        # Fill missing values with 1KG
        df['unit(KG)'] = df['unit(KG)'].fillna(1)

        # Standardize price per KG
        df['cedi_price/(KG)'] = (df['cedi_price'] / df['unit(KG)']).round(2)

        # Drop unit(KG) and cedi_price after standardizing
        df.drop(['unit(KG)', 'cedi_price'], axis=1, inplace=True)

        # File name
        base = os.path.splitext(os.path.basename(file))[0]

        # Save to same path
        df.to_csv(f'data/crop_splits/{base}.csv', index=False)

    print('Report: Data cleaning successful.')
