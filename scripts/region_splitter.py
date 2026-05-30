# Import relevant dependencies
import pandas as pd
import numpy as np

# Step 1------------------------------------------------------------

# Load CSV


def load_CSV(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Load original wfp dataset to start process.
    """

    # Match column names with more appropriate ones
    column_matching = {
        'date': 'date',
        'admin1': 'region',
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

    df = pd.read_csv(dataframe, parse_dates=['date'], dayfirst=True)

    # Implement column matching
    df = df.rename(columns=column_matching)

    return df

# Unique regions


def unique_region(df: pd.DataFrame = load_CSV('data/original_dataset/wfp_food_prices_gha.csv')) -> np.array:
    """
    Create an array of unique regions from the dataframe.
    """

    unique_region = list(df['region'].unique())

    print('-'*50)
    print('Step 1 initiated: Ingesting data ✅\n')

    return unique_region

# Split data frame


def split_dataframe(df: pd.DataFrame = load_CSV('data/original_dataset/wfp_food_prices_gha.csv')) -> pd.DataFrame:
    """
    Split data frame into unique regions.
    """

    # Count number of regions
    n = 0

    # Retrieve list of unique items
    for unique in unique_region():

        # Retrieve original data frame and subset crop
        unique_df = df[df['region'] == unique]
        unique_df = unique_df.drop(['region'], axis=1)

        unique = unique.replace(' ', '_')

        # Save split data frame to folder
        unique_df.to_csv(f'data/region_splits/{unique}.csv', index=False)

        n += 1

    # Return number of split files
    return n

# Main function


def main():
    """
    Main function to begin split process
    """
    number_of_splits = split_dataframe()

    print(
        f"Report: {number_of_splits} data frames were created for {number_of_splits} regions.")

    if __name__ == "__main__":
        main()
