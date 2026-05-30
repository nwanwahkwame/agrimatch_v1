# Import relevant dependencies
import pandas as pd
import numpy as np
from glob import glob
import os

# Step 2 -----------------------------------------------------------------

# Find all CSV files in region directory
region_files = glob(f'data/region_splits/*.csv')

# Main function


def crop_splitter_from_region():
    """
    Splits CVSs into smaller, sub-section CSV.
    For every region, sub-split into crop.
    Exclude crops that are not chosen.
    """

    print('-'*50)
    print('Step 2 initiated: Splitting data further into crops per region ✅\n')

    chosen_crops = ['Cassava',
                    'Cowpeas',
                    'Cowpeas (white)',
                    'Eggplants',
                    'Maize',
                    'Maize (yellow)',
                    'Millet',
                    'Onions',
                    'Peppers (dried)',
                    'Peppers (fresh)',
                    'Rice (local)',
                    'Rice (paddy)',
                    'Sorghum',
                    'Soybeans',
                    'Tomatoes (local)',
                    'Tomatoes (navrongo)',
                    'Yam',
                    'Yam (puna)']

    # Track file count
    n = 0

    for region in region_files:

        # Outlawed metric measurements
        outlawed_words = ['KG', ' KG', 'Tubers',
                          ' Tubers', 'Bunch', ' Bunch', 'pcs', ' pcs']

        # Match column names with more appropriate ones
        column_matching = {
            'date': 'date',
            # 'admin1': 'region',
            'admin2': 'ISO',
            'market': 'city',
            'market_id': 'market_id',
            'latitude': 'latitude',
            'longitude': 'longitude',
            'category': 'crop_category',
            'commodity': 'crop',
            'commodity_id': 'crop_id',
            'unit': 'unit(KG)',
            'priceflag': 'price_flag',
            'pricetype': 'price_type',
            'currency': 'currency',
            'price': 'cedi_price',
            'usdprice': 'dollar_price'
        }

        df = pd.read_csv(region, parse_dates=['date'], dayfirst=False)

        # Implement column matching
        df = df.rename(columns=column_matching)

        # Drop specific columns
        df = df.drop(columns=['currency', 'dollar_price'], axis=1)

        # Extract the year
        if 'year' not in df.columns:
            df.insert(loc=1, column=[
                      'year'], value=df['date'].dt.year, allow_duplicates=True)

        # Extract the month
        if 'month' not in df.columns:
            df.insert(loc=2, column=[
                      'month'], value=df['date'].dt.month, allow_duplicates=True)

        # Extract the day
        if 'day' not in df.columns:
            df.insert(loc=3, column=[
                      'day'], value=df['date'].dt.day, allow_duplicates=True)

        # Set data frame to redenomination baseline year
        df = df[df['year'] >= 2007]

        # Redenomination year condition
        condition_1 = df['year'] == 2007

        # Redenomination month condition
        condition_2 = df['month'] <= 6

        # Extract undesired period
        redenomination = df[(condition_1) & (condition_2)]

        # Drop undesired period
        df.drop(redenomination.index, inplace=True)

        # Create an array of crops from the dataframe
        unique_crop = list(df['crop'].unique())

        # Split data frame into smaller data frames according to crops
        for unique in unique_crop:

            if unique in chosen_crops:

                # Retrieve original data frame and subset crop
                unique_df = df[df['crop'] == unique]
                unique_df = unique_df.drop(
                    ['crop_category', 'crop', 'crop_id'], axis=1)

                # Retrieve outlawed words and iterate
                for outlaw in outlawed_words:

                    if unique_df['unit(KG)'].str.contains(outlaw, na=False).any():
                        unique_df['unit(KG)'] = unique_df['unit(KG)'].str.replace(
                            outlaw, '')
                    else:
                        continue

                # Naming convention
                unique = unique.replace(' ', '').lower()
                region = os.path.basename(region).lower().replace('.csv', '')
                delimiter = '_'
                unique_region_name = region+delimiter+unique

                # Save split data frame to folder
                unique_df.to_csv(
                    f'data/crop_splits/{unique_region_name}.csv', index=False)

        n += 1

    # Return number of split files
    print(f'Report: {n} region-crop splits were created.')
