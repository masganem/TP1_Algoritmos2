import pandas as pd

# Constants for CSV parsing
CSV_PATH = "data/geocoded_bars_and_restaurants.csv"
COLUMN_NAMES = [
    "full_address",
    "address",
    "name",
    "lat",
    "lng",
]

def load_dataframe():
    """Read and clean the restaurant CSV used by the application."""
    df = pd.read_csv(
        CSV_PATH,
        header=None,
        names=COLUMN_NAMES,
        sep=";",
        skiprows=1,
    )
    df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
    df["lng"] = pd.to_numeric(df["lng"], errors="coerce")
    return df.dropna(subset=["lat", "lng"]).reset_index(drop=True)


