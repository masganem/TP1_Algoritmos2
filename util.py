import pandas as pd
from kd_tree import KDTree

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
    # Keep only valid coordinates
    df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
    df["lng"] = pd.to_numeric(df["lng"], errors="coerce")
    return df.dropna(subset=["lat", "lng"]).reset_index(drop=True)


def build_kdtree(df):
    """Convert a DataFrame to a KDTree using (lat, lon, id)."""
    points = [(row.lat, row.lng, int(idx)) for idx, row in df.iterrows()]
    return KDTree(points)

def query_kdtree(tree, min_lat, max_lat, min_lon, max_lon):
    """Query the KDTree for points within the given bounding box."""
    return tree.range_search(min_lat, max_lat, min_lon, max_lon)