from comida_di_buteco import load, align_data
from utils import load_dataframe

butecos = load()
pbh = load_dataframe('data/geocoded_bars_and_restaurants.csv', ["full_address", "address", "name", "lat", "lng", "data", "alvara"])

data = align_data(butecos, pbh)

data.to_csv('data/geocoded_bars_and_restaurants_with_cdb_idx.csv', sep=';', index=False)
