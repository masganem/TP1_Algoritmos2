import dash_leaflet as dl
import dash_leaflet.express as dlx
from dash import Dash

from util import load_dataframe, build_kdtree

df = load_dataframe()

tree = build_kdtree(df)

features = [
    dict(
        lat=row.lat,
        lon=row.lng,
        name=row.name,
        address=row.address,
        full_address=row.full_address,
    )
    for _, row in df.iterrows()
]

geojson_data = dlx.dicts_to_geojson(features)

app = Dash()

geojson_layer = dl.GeoJSON(
    data=geojson_data,
    id="bars-geojson",
    cluster=True,
    zoomToBoundsOnClick=True,
    superClusterOptions={"radius": 140, "maxZoom": 14},
    options={"style": {"weight": 0}},
)

app.layout = dl.Map(
    [
        dl.TileLayer(
            url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png",
        ),
        geojson_layer,
    ],
    center=[-19.918476, -43.9532384],
    zoom=12,
    style={"height": "95vh"},
    attributionControl=False,
)

if __name__ == "__main__":
    app.run(debug=True)
