import streamlit as st
import pandas as pd
from pyvis.network import Network
import streamlit.components.v1 as components
from pathlib import Path

st.set_page_config(page_title="Nearest Facilities", page_icon="🏥")
st.markdown("# Acute Hospitals Nearest Facilities")
st.sidebar.header("Nearest Facilities")

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

from math import radians, sin, cos, sqrt, atan2

def haversine(lon1, lat1, lon2, lat2):
    R = 6371.0
    phi1, phi2 = radians(lat1), radians(lat2)
    dphi = radians(lat2 - lat1)
    dlambda = radians(lon2 - lon1)
    a = sin(dphi / 2) ** 2 + cos(phi1) * cos(phi2) * sin(dlambda / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c


def compute_nearest(acute_df, facility_df):
    if facility_df.empty:
        return []
    edges = []
    for _, ac in acute_df.iterrows():
        distances = facility_df.apply(
            lambda row: haversine(
                ac["longitude"], ac["latitude"], row["longitude"], row["latitude"]
            ),
            axis=1,
        )
        idx = distances.idxmin()
        target = facility_df.loc[idx]
        edges.append(
            {
                "source": ac["Name"],
                "target": target["Name"],
                "type": target["facility_type"],
            }
        )
    return edges

def build_network(edges):
    net = Network(height="600px", width="100%", directed=True)
    for edge in edges:
        src = edge["source"]
        dst = edge["target"]
        if src not in net.get_nodes():
            net.add_node(src, label=src, color="red")
        if dst not in net.get_nodes():
            net.add_node(dst, label=dst, color="blue")
        net.add_edge(src, dst, label=edge["type"])
    return net

selected = st.multiselect(
    "Select facility type(s) to connect with acute hospitals:",
    options=list(FACILITY_FILES.keys()),
)

if selected:
    acute_df = load_dataset(ACUTE_FILE)
    facilities = load_facilities(selected)
    edges = compute_nearest(acute_df, facilities)
    if edges:
        net = build_network(edges)
        net.save_graph("graph.html")
        with open("graph.html", "r", encoding="utf-8") as f:
            html = f.read()
        components.html(html, height=650, width=800)
    else:
        st.info("No facilities selected.")
else:
    st.info("Choose one or more facility types from the sidebar.")
