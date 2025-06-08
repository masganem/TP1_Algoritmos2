import dash_leaflet as dl
import dash_leaflet.express as dlx
from dash import Dash, html, dash_table, Output, Input, State, no_update
import pandas as pd
from kd_tree import KDTree
from utils import load_dataframe
import sys

# We lose about 3000 entries here -- that is, 3000 entries were not geocoded.
df = pd.read_csv('data/geocoded_bars_and_restaurants_with_cdb_idx.csv', sep=";").dropna(subset=["lat", "lng"]).reset_index(drop=True)
df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
df["lng"] = pd.to_numeric(df["lng"], errors="coerce")
# We match 51 of 9012 entries (see comida_di_buteco/align_data.py)
num_matches = (df["cdb_idx"] != -1).sum()
print(f"Matched {num_matches} of {len(df)} PBH entries")

# Fetch url from data/butecos.csv by using the cdb_idx to loc rows. drop cdb_idx -1
cdb_idx = df["cdb_idx"].dropna().astype(int)
cdb_idx = cdb_idx[cdb_idx != -1]  # Exclude -1 entries




butecos_df = pd.read_csv('data/butecos.csv', sep=",")
butecos_df = butecos_df.iloc[cdb_idx] # Header is [name, address, details_url, image_url]

tree = KDTree(df)

# Separate cdb butecos from regular butecos
regular_features = []
buteco_features = []

for _, row in df.iterrows():
    feature_data = dict(
        lat=row.lat,
        lon=row.lng,
        name=row.name,
        data=row.data,
        alvara=row.alvara,
        address=row.address,
        full_address=row.full_address,
    )
    
    if row.cdb_idx != -1:
        # if its in the cdb, add extra information
        buteco_info = butecos_df.loc[butecos_df.index == row.cdb_idx]
        if not buteco_info.empty:
            feature_data['image_url'] = buteco_info.iloc[0]['image_url']
            feature_data['details_url'] = buteco_info.iloc[0]['details_url']
            buteco_features.append(feature_data)
        else:
            regular_features.append(feature_data)
    else:
        regular_features.append(feature_data)



# Create GeoJSON for regular features
regular_geojson = dlx.dicts_to_geojson(regular_features) if regular_features else {"type": "FeatureCollection", "features": []}

# Create special markers for butecos
buteco_markers = []
for feature in buteco_features:
    # Create popup HTML with image and link
    popup_html = f"""
    <div style="width: 200px; text-align: center;">
        <h4 style="margin: 5px 0;">{feature['name']}</h4>
        <img src="{feature['image_url']}" style="width: 180px; height: auto; margin: 5px 0;" alt="Prato do buteco"/>
        <br/>
        <a href="{feature['details_url']}" target="_blank" style="color: #1f77b4; text-decoration: underline;">
            Ver mais detalhes
        </a>
        <br/>
        <small style="color: #666; margin-top: 5px; display: block;">
            {feature['full_address']}
        </small>
    </div>
    """
    
    marker = dl.Marker(
        position=[feature['lat'], feature['lon']],
        children=[
            dl.Tooltip(
                html.Div([
                    html.H4(feature['name'], style={'margin': '5px 0', 'text-align': 'center'}),
                    html.Img(
                        src=feature['image_url'],
                        style={'width': '180px', 'height': 'auto', 'margin': '5px 0', 'display': 'block', 'margin-left': 'auto', 'margin-right': 'auto'}
                    ),
                    html.A(
                        "Ver mais detalhes",
                        href=feature['details_url'],
                        target="_blank",
                        style={'color': '#1f77b4', 'text-decoration': 'underline', 'display': 'block', 'text-align': 'center', 'margin': '5px 0'}
                    ),
                    html.Small(
                        feature['full_address'],
                        style={'color': '#666', 'margin-top': '5px', 'display': 'block', 'text-align': 'center'}
                    )
                ], style={'width': '200px', 'text-align': 'center'})
            ),
            dl.Popup(
                html.Div([
                    html.H4(feature['name'], style={'margin': '5px 0', 'text-align': 'center'}),
                    html.Img(
                        src=feature['image_url'], 
                        style={'width': '180px', 'height': 'auto', 'margin': '5px 0', 'display': 'block', 'margin-left': 'auto', 'margin-right': 'auto'}
                    ),
                    html.A(
                        "Ver mais detalhes", 
                        href=feature['details_url'], 
                        target="_blank",
                        style={'color': '#1f77b4', 'text-decoration': 'underline', 'display': 'block', 'text-align': 'center', 'margin': '5px 0'}
                    ),
                    html.Small(
                        feature['full_address'],
                        style={'color': '#666', 'margin-top': '5px', 'display': 'block', 'text-align': 'center'}
                    )
                ], style={'width': '200px', 'text-align': 'center'})
            )
        ],
        icon={
            "iconUrl": "https://cdn.jsdelivr.net/gh/pointhi/leaflet-color-markers@master/img/marker-icon-2x-red.png",
            "shadowUrl": "https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png",
            "iconSize": [25, 41],
            "iconAnchor": [12, 41],
            "popupAnchor": [1, -34],
            "shadowSize": [41, 41]
        }
    )
    buteco_markers.append(marker)

app = Dash()

# Layer for regular establishments  (with clustering)
regular_geojson_layer = dl.GeoJSON(
    data=regular_geojson,
    id="bars-geojson",
    cluster=True,
    zoomToBoundsOnClick=True,
    superClusterOptions={"radius": 140, "maxZoom": 15},
    options={"style": {"weight": 0}},
)

# Layer for comida de buteco (without clustering, but close to clusters)
butecos_layer = dl.LayerGroup(
    buteco_markers,
    id="butecos-layer"
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
        regular_geojson_layer,
        butecos_layer,  # Adicionar layer dos butecos
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
    app.run(host='0.0.0.0', port=8000, debug=False)
