import pandas as pd


def sanitize_mofa(dataframe: pd.DataFrame = '../data/original_dataset/commodity_prices_04.11.25.csv') -> pd.DataFrame:
    """
    Standardize the MoFa data with HDX data.
    """

    # Load data
    df = pd.read_csv(dataframe)

    # Reindex to suit HDX
    df = df.reindex(columns=['date',
                             'region',
                             'Market',
                             'district',
                             '_geolocation',
                             'commodity',
                             'source',
                             'Price',
                             'market_day',
                             'Year',
                             'month',
                             'week',
                             'Type'])

    # Change column names
    df.columns = ['date', 'region', 'city', 'market_sold_at', '_geolocation', 'commodity',
                  'pricetype', 'price', 'market_day', 'Year', 'month', 'week', 'Type']

    # Retrieve HDX columns
    wfp_columns = """date	region	city	market_sold_at	market_id	latitude	longitude	commodity	category	commodity_id	unit	priceflag	pricetype	currency	price	usdprice"""
    wfp_columns = wfp_columns.split()

    # Assign scalar 0 to new columns
    for column in wfp_columns:
        if column not in df.columns:
            df[column] = 0

    # Drop columns that are not needed
    for column in df.columns.to_list():
        if column not in wfp_columns:
            df = df.drop(column, axis=1)

    # Final index
    final_index = ['date',
                   'region',
                   'city',
                   'market_sold_at',
                   'market_id',
                   'latitude',
                   'longitude',
                   'commodity',
                   'category',
                   'commodity_id',
                   'unit',
                   'priceflag',
                   'pricetype',
                   'currency',
                   'price',
                   'usdprice']

    # Reindex final time
    df = df.reindex(columns=final_index)

    # Map old regions to new regions
    region_dictionary = {
        'Central':      'Central',
        'Greater Accra': 'Greater Accra',
        'Western North': 'Western',
        'Bono':         'Brong Ahafo',
        'Bono East':    'Brong Ahafo',
        'Ahafo':        'Brong Ahafo',
        'Ashanti':      'Ashanti',
        'Eastern':      'Eastern',
        'Volta':        'Volta',
        'Oti':          'Volta',
        'Upper West':   'Upper West',
        'Upper East':   'Upper East',
        'Northern':     'Northern',
        'North East':   'Northern',
        'Savannah':     'Northern',
    }

    # Replace region names
    df['region'] = df['region'].str.strip().map(
        region_dictionary).fillna(df['region'].str.strip())

    # Load HDX data
    df_new = pd.read_csv('../data/original_dataset/wfp_food_prices_gha.csv')

    # Concatenate HDX and MoFA
    df = pd.concat([df, df_new], ignore_index=True)

    # Sort according to date
    df = df.sort_values('date')

    # Save aligned dataset
    df.to_csv(
        '../data/original_dataset/wfp_food_prices_gha_merged.csv', index=False)
    print('Data cleaned. ✅')


# sanitize_mofa()

if __name__ == '__main__':
    sanitize_mofa()
