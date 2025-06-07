import dash_leaflet as dl
import dash_leaflet.express as dlx
from dash import Dash, html, dash_table, Output, Input, State, no_update
import pandas as pd
from kd_tree import KDTree
from utils import load_dataframe

# We lose about 3000 entries here -- that is, 3000 entries were not geocoded.
df = pd.read_csv('data/geocoded_bars_and_restaurants_with_cdb_idx.csv', sep=";").dropna(subset=["lat", "lng"]).reset_index(drop=True)
df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
df["lng"] = pd.to_numeric(df["lng"], errors="coerce")
# We match 56 of 9471 entries (see comida_di_buteco/align_data.py)
num_matches = (df["cdb_idx"] != -1).sum()
print(f"Matched {num_matches} of {len(df)} PBH entries")

tree = KDTree(df)

features = [
    dict(
        lat=row.lat,
        lon=row.lng,
        name=row.name,
        data=row.data,
        alvara=row.alvara,
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
    superClusterOptions={"radius": 140, "maxZoom": 15},
    options={"style": {"weight": 0}},
)

draw_control = dl.EditControl(
    id="select-control",
    position="topleft",
    draw={
        "rectangle": True,
        "polygon": False,
        "polyline": False,
        "circle": False,
        "circlemarker": False,
        "marker": False,
    },
    edit={"edit": False, "remove": True},
)

map_component = dl.Map(
    [
        dl.TileLayer(
            url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png",
        ),
        geojson_layer,
        dl.FeatureGroup([draw_control]),
        dl.LayerGroup(id="highlight-layer"),
    ],
    center=[-19.918476, -43.9532384],
    zoom=12,
    style={"height": "65vh", "width": "100%"},
    id="map",
    attributionControl=False,
)

table_component = dash_table.DataTable(
    id="selected-bars-table",
    columns=[
        {"name": "Nome", "id": "name"},
        {"name": "Endereço", "id": "full_address"},
        {"name": "Data de Abertura", "id": "data"},
        {"name": "Tem alvará?", "id": "alvara"},
    ],
    data=[],
    page_size=10,
    style_table={"overflowX": "auto", "maxHeight": "25vh", "overflowY": "auto"},
    style_cell={"textAlign": "left", "padding": "4px"},
    style_data_conditional=[
        {
            "if": {"filter_query": "{cdb_idx} != -1"},
            "backgroundColor": "#333333",  
            "color": "#ffffff",            
        },
        {
            "if": {"state": "active"},
            "fontWeight": "bold",
            "color": "inherit",
            "backgroundColor": "revert-layer",
            "outline": "none",
            "borderColor": "inherit",
        },
    ],
)

app.layout = html.Div([
    map_component,
    html.Hr(),
    table_component,
])

@app.callback(
    Output("selected-bars-table", "data"),
    Input("select-control", "geojson"),
    prevent_initial_call=True,
)
def update_selected_table(drawn_geojson):
    """Whenever the user updates the EditControl, update the table."""
    if not drawn_geojson or not drawn_geojson.get("features"):
        return []

    selected_indices = set()

    for feature in drawn_geojson["features"]:
        geometry = feature.get("geometry", {})
        if geometry.get("type") != "Polygon":
            continue

        coords = geometry.get("coordinates", [])
        if not coords:
            continue
        ring = coords[0]
        lons = [pt[0] for pt in ring]
        lats = [pt[1] for pt in ring]
        min_lon, max_lon = min(lons), max(lons)
        min_lat, max_lat = min(lats), max(lats)

        results = tree.query(min_lat, max_lat, min_lon, max_lon)
        for _, _, idx in results:
            selected_indices.add(idx)

    if not selected_indices:
        return []

    selection_df = df.loc[list(selected_indices), ["full_address", "name", "data", "alvara", "lat", "lng", "cdb_idx"]].copy()

    selection_df["full_address"] = selection_df["full_address"].str.replace(", nan", "", regex=False)
    selection_df["full_address"] = selection_df["full_address"].str.replace(", Belo Horizonte, Minas Gerais, Brasil", "", regex=False)

    selection_df.loc[selection_df["cdb_idx"] != -1, "name"] = (
        selection_df.loc[selection_df["cdb_idx"] != -1, "name"] + " 🍽️"
    )

    selection_df["is_restaurant"] = selection_df["cdb_idx"] != -1
    selection_df = selection_df.sort_values(by="is_restaurant", ascending=False).drop(columns="is_restaurant")

    return selection_df.to_dict("records")

@app.callback(
    Output("highlight-layer", "children"),
    Output("map", "center"),
    Input("selected-bars-table", "active_cell"),
    State("selected-bars-table", "data"),
    prevent_initial_call=True,
)
def highlight_selected_marker(active_cell, table_data):
    if not active_cell or active_cell.get("row") is None:
        return [], no_update

    row_idx = active_cell["row"]
    if row_idx >= len(table_data):
        return [], no_update

    row = table_data[row_idx]
    lat = row.get("lat")
    lon = row.get("lng")
    if lat is None or lon is None:
        return [], no_update

    marker = dl.CircleMarker(
        center=[lat, lon],
        radius=10,
        color="#ff0000",
        fill=True,
        fillColor="#ff0000",
        fillOpacity=1.0,
    )

    return [marker], [lat, lon]

if __name__ == "__main__":
    app.run(debug=True)
