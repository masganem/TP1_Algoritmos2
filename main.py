import dash_leaflet as dl
import dash_leaflet.express as dlx
from dash import Dash, html, dash_table, Output, Input, State

from util import load_dataframe, build_kdtree, query_kdtree

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
    attributionControl=False,
)

table_component = dash_table.DataTable(
    id="selected-bars-table",
    columns=[
        {"name": "Nome", "id": "name"},
        {"name": "Endereço", "id": "full_address"},
    ],
    data=[],
    page_size=10,
    style_table={"overflowX": "auto", "maxHeight": "25vh", "overflowY": "auto"},
    style_cell={"textAlign": "left", "padding": "4px"},
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

        results = query_kdtree(tree, min_lat, max_lat, min_lon, max_lon)
        for _, _, idx in results:
            selected_indices.add(idx)

    if not selected_indices:
        return []

    selection_df = df.loc[list(selected_indices), ["full_address", "name", "lat", "lng"]].copy()

    selection_df["full_address"] = selection_df["full_address"].str.replace(", nan", "", regex=False)
    selection_df["full_address"] = selection_df["full_address"].str.replace(", Belo Horizonte, Minas Gerais, Brasil", "", regex=False)

    return selection_df.to_dict("records")

@app.callback(
    Output("highlight-layer", "children"),
    Input("selected-bars-table", "active_cell"),
    State("selected-bars-table", "data"),
    prevent_initial_call=True,
)
def highlight_selected_marker(active_cell, table_data):
    if not active_cell or active_cell.get("row") is None:
        return []

    row_idx = active_cell["row"]
    if row_idx >= len(table_data):
        return []

    row = table_data[row_idx]
    lat = row.get("lat")
    lon = row.get("lng")
    if lat is None or lon is None:
        return []

    marker = dl.CircleMarker(
        center=[lat, lon],
        radius=10,
        color="#ff0000",
        fill=True,
        fillColor="#ff0000",
        fillOpacity=1.0,
    )

    return [marker]

if __name__ == "__main__":
    app.run(debug=True)
