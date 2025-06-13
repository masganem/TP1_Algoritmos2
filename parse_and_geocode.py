import pandas as pd
from geopy.geocoders import Nominatim
from time import sleep

SOURCE_DATA_PATH = "data/20250401_atividade_economica.csv"

economic_data = pd.read_csv(SOURCE_DATA_PATH, sep = ";")
cnaes = economic_data["DESCRICAO_CNAE_PRINCIPAL"].unique()
#5611 é o código inicial de estabelecimentos alimentícios
#Dentro desse código possuimos apenas 4 códigos, e desse 4, 3 se relacionam a bares e restaurantes.
#A filtragem abaixo é feita para manter apenas os 3 códigos
bars_and_restaurants_data = economic_data[economic_data["CNAE_PRINCIPAL"].astype(str).str.startswith("5611")]
filtered_bars_and_restaurants_data = economic_data[economic_data["CNAE_PRINCIPAL"].astype(float).isin([
   5611201.0,
   5611204.0,
   5611205.0,
])]

for index, row in filtered_bars_and_restaurants_data.iterrows():
   address = f"{row['DESC_LOGRADOURO']} {row['NOME_LOGRADOURO']}, {row['NUMERO_IMOVEL']}, {row['COMPLEMENTO']}, {row['NOME_BAIRRO']}, Belo Horizonte, Minas Gerais, Brasil"
   useful_address = f"{row['DESC_LOGRADOURO']} {row['NOME_LOGRADOURO']}, {row['NUMERO_IMOVEL']}, {row['NOME_BAIRRO']}, Belo Horizonte, Minas Gerais, Brasil"
   filtered_bars_and_restaurants_data.at[index, "address"] = address
   filtered_bars_and_restaurants_data.at[index, "useful_address"] = useful_address

bars_and_restaurants = filtered_bars_and_restaurants_data[["DATA_INICIO_ATIVIDADE", "IND_POSSUI_ALVARA", "address", "useful_address", "NOME", "NOME_FANTASIA"]]
bars_and_restaurants["NOME"] = bars_and_restaurants["NOME_FANTASIA"].fillna(
    bars_and_restaurants["NOME"]
)
useful_bars_dataset = bars_and_restaurants.drop(["NOME_FANTASIA"], axis = 1)
geolocator = Nominatim(user_agent="my_geocoder_app")

def geocode_address(address):
    try:
        location = geolocator.geocode(address)
        if location:
            return pd.Series([location.latitude, location.longitude])
    except:
        return pd.Series([None, None])
    return pd.Series([None, None])

latitudes = []
longitudes = []

useful_bars_dataset.to_csv("data/not_geocoded_bars_and_restaurants.csv", index=False, sep=";")

for i, address in enumerate(useful_bars_dataset["useful_address"]):
    print(f"Geocoding {i+1}/{len(useful_bars_dataset)}: {address}")
    lat, lon = geocode_address(address)
    latitudes.append(lat)
    longitudes.append(lon)
    sleep(1)

useful_bars_dataset["latitude"] = latitudes
useful_bars_dataset["longitude"] = longitudes

useful_bars_dataset.to_csv("data/geocoded_bars_and_restaurants.csv", index=False, sep=";")
