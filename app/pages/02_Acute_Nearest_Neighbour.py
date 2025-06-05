import streamlit as st
import pandas as pd
from pyvis.network import Network
import streamlit.components.v1 as components
from pathlib import Path
from math import radians, sin, cos, sqrt, atan2
import matplotlib.pyplot as plt

# Page config
st.set_page_config(page_title="Facility → Nearest Acute Hospital", page_icon="🏥")
st.markdown("# Nearest Acute Hospital per Facility")
st.sidebar.header("Facility Type Selection")

# File paths
DATA_DIR = Path("data/processed/Health Infrastructure/enriched")
ACUTE_FILE = DATA_DIR / "NHS_SW_Acute_Hospitals_enriched.csv"

FACILITY_FILES = {
    "CDC": "NHS_SW_ Community_Diagnostic_Centres_enriched.csv",
    "GP Practice": "NHS_SW_ GP_Practices_and_Polyclinics_enriched.csv",
    "Ambulance Station": "NHS_SW_Ambulance_Stations_enriched.csv",
    "Community and Outreach": "NHS_SW_Community_and_Outreach_Facilities_enriched.csv",
    "Community Hospital": "NHS_SW_Community_Hospitals_enriched.csv",
    "Specialist Hospital": "NHS_SW_Specialist_Hospitals_enriched.csv",
}

@st.cache_data
def load_dataset(file_path: Path) -> pd.DataFrame:
    return pd.read_csv(file_path)

def load_facilities(selected_types):
    frames = []
    for t in selected_types:
        path = DATA_DIR / FACILITY_FILES[t]
        df = load_dataset(path)
        df["facility_type"] = t
        frames.append(df)
    if frames:
        return pd.concat(frames, ignore_index=True)
    else:
        return pd.DataFrame(columns=["latitude", "longitude", "Name", "facility_type"])

def haversine(lon1, lat1, lon2, lat2):
    R = 6371.0
    phi1, phi2 = radians(lat1), radians(lat2)
    dphi = radians(lat2 - lat1)
    dlambda = radians(lon2 - lon1)
    a = sin(dphi / 2) ** 2 + cos(phi1) * cos(phi2) * sin(dlambda / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

def compute_nearest(facility_df, acute_df):
    if facility_df.empty or acute_df.empty:
        return []
    edges = []
    for _, fac in facility_df.iterrows():
        distances = acute_df.apply(
            lambda row: haversine(
                fac["longitude"], fac["latitude"], row["longitude"], row["latitude"]
            ),
            axis=1,
        )
        idx = distances.idxmin()
        target = acute_df.loc[idx]
        edges.append(
            {
                "source": fac["Name"],
                "target": target["Name"],
                "type": fac["facility_type"],
            }
        )
    return edges

def build_network(edges, acute_df, facility_df):
    net = Network(height="1800px", width="100%", directed=True, notebook=False, bgcolor="#f9f9f9")

    def scale(val, min_val, max_val, target_min, target_max):
        return ((val - min_val) / (max_val - min_val)) * (target_max - target_min) + target_min

    all_lats = pd.concat([facility_df["latitude"], acute_df["latitude"]])
    all_lons = pd.concat([facility_df["longitude"], acute_df["longitude"]])
    min_lat, max_lat = all_lats.min(), all_lats.max()
    min_lon, max_lon = all_lons.min(), all_lons.max()

    for _, fac in facility_df.iterrows():
        x = scale(fac["longitude"], min_lon, max_lon, -1000, 1000)
        y = scale(fac["latitude"], max_lat, min_lat, -1000, 1000)
        net.add_node(
            fac["Name"], label=fac["Name"], color="#4e79a7",
            title=fac["facility_type"], x=x, y=y, physics=False, shape="dot", size=12
        )

    for _, ac in acute_df.iterrows():
        x = scale(ac["longitude"], min_lon, max_lon, -1000, 1000)
        y = scale(ac["latitude"], max_lat, min_lat, -1000, 1000)
        net.add_node(
            ac["Name"], label=ac["Name"], color="#e15759",
            title="Acute Hospital", x=x, y=y, physics=False, shape="star", size=20
        )

    for edge in edges:
        net.add_edge(edge["source"], edge["target"], arrows="to", title=edge["type"], color="#555")

    net.set_options("""
    var options = {
      "nodes": { "font": {"size": 14}, "borderWidth": 1 },
      "edges": { "smooth": true, "color": {"inherit": false} },
      "interaction": { "dragNodes": true, "hover": true },
      "physics": { "enabled": false }
    }
    """)
    return net

def plot_static_geo_network(facilities, acute_df, edges):
    fig, ax = plt.subplots(figsize=(12, 14))

    for ftype in facilities["facility_type"].unique():
        sub = facilities[facilities["facility_type"] == ftype]
        ax.scatter(sub["longitude"], sub["latitude"], label=ftype, s=30, alpha=0.8)

    ax.scatter(acute_df["longitude"], acute_df["latitude"], color="red", label="Acute Hospital", s=60, marker="X")

    for edge in edges:
        src = facilities[facilities["Name"] == edge["source"]].iloc[0]
        dst = acute_df[acute_df["Name"] == edge["target"]].iloc[0]
        ax.plot([src["longitude"], dst["longitude"]], [src["latitude"], dst["latitude"]],
                linestyle="--", color="gray", linewidth=1, alpha=0.6)

    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.set_title("Geospatial Network: Facilities → Nearest Acute Hospital")
    ax.set_aspect('equal', adjustable='box')
    ax.legend(loc='best')
    ax.grid(True)
    return fig

# Sidebar input
selected = st.multiselect(
    "Select facility type(s) to connect to their nearest acute hospital:",
    options=list(FACILITY_FILES.keys()),
)

# Streamlit visualisation logic
if selected:
    acute_df = load_dataset(ACUTE_FILE)
    facilities = load_facilities(selected)
    edges = compute_nearest(facilities, acute_df)

    if edges:
        # PyVis interactive graph
        net = build_network(edges, acute_df, facilities)
        net.save_graph("graph.html")
        with open("graph.html", "r", encoding="utf-8") as f:
            html = f.read()
        components.html(html, height=1800, width=2200)

        # Static geographic plot
        st.markdown("### 📍 Geospatial Scatter View (Lat/Lon)")
        fig = plot_static_geo_network(facilities, acute_df, edges)
        st.pyplot(fig)
    else:
        st.info("No edges were created between facilities and acute hospitals.")
else:
    st.info("Please select at least one facility type from the sidebar to begin.")
