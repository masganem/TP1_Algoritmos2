from comida_di_buteco import load, align_data
from utils import load_dataframe

butecos = load()
pbh = load_dataframe()

data = align_data(butecos, pbh)

data.to_csv('abc.csv', sep=';', index=False)
