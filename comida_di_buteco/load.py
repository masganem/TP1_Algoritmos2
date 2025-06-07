import pandas as pd

def load():
    """Read and clean the data scraped from Comida di Buteco"""
    return pd.read_csv(
        "data/butecos.csv",
        sep=",",
    )

