import pandas as pd

def load_dataframe(path, names):
    return pd.read_csv(
        path,
        header=None,
        names=names,
        sep=";",
        skiprows=1,
    )

