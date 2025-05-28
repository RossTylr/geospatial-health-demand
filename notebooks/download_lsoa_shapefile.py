import os
import gdown
import zipfile
import geopandas as gpd

# ----------------------------------------
# CONFIGURATION
# ----------------------------------------
BASE_DIR = "/Users/rosstaylor/Downloads/Research Project/Code Folder/Research Project - Geospatial Health Demand"
DATA_DIR = os.path.join(BASE_DIR, "data", "raw")

# LSOA Shapefile Paths
FILE_ID = "14FHvLwE8_KH747ngdJWAH_v58Zmi2G8Y"  # Confirmed working file ID
ZIP_PATH = os.path.join(DATA_DIR, "Lower_Layer_LSOA_2021.zip")
EXTRACT_DIR = os.path.join(DATA_DIR, "lsoa_shapefile")
SHP_FILENAME = "Lower_layer_Super_Output_Areas_(December_2021)_Boundaries_EW_BFC_(V10).shp"
LSOA_PATH = os.path.join(EXTRACT_DIR, SHP_FILENAME)

# NHS England Regions Shapefile Path
NHS_SHAPEFILE_PATH = os.path.join(DATA_DIR, "NHS_England_(Regions)_(December_2023)_EN_BGC.shp")


# ----------------------------------------
# FUNCTION: DOWNLOAD ZIP IF NEEDED
# ----------------------------------------
def download_zip_if_needed():
    if not os.path.exists(ZIP_PATH):
        os.makedirs(os.path.dirname(ZIP_PATH), exist_ok=True)
        url = f"https://drive.google.com/uc?id={FILE_ID}"
        print(f"Downloading LSOA shapefile zip from: {url}")
        gdown.download(url, ZIP_PATH, quiet=False)
    else:
        print("Zip file already exists — skipping download.")


# ----------------------------------------
# FUNCTION: EXTRACT ZIP IF NEEDED
# ----------------------------------------
def extract_zip():
    if not os.path.exists(EXTRACT_DIR):
        print("Extracting LSOA shapefile zip...")
        with zipfile.ZipFile(ZIP_PATH, 'r') as zip_ref:
            zip_ref.extractall(EXTRACT_DIR)
    else:
        print("Shapefile already extracted — skipping.")


# ----------------------------------------
# FUNCTION: LOAD LSOA SHAPEFILE
# ----------------------------------------
def load_lsoa_shapefile():
    if not os.path.exists(LSOA_PATH):
        raise FileNotFoundError(f"LSOA shapefile not found at: {LSOA_PATH}")

    lsoa_gdf = gpd.read_file(LSOA_PATH)
    lsoa_gdf = lsoa_gdf[lsoa_gdf.is_valid]

    print(f"Loaded {len(lsoa_gdf)} valid LSOA polygons.")
    return lsoa_gdf


# ----------------------------------------
# FUNCTION: LOAD NHS REGIONS AND FILTER SOUTH WEST
# ----------------------------------------
def load_nhs_sw_region():
    if not os.path.exists(NHS_SHAPEFILE_PATH):
        raise FileNotFoundError(f"NHS regions shapefile not found at: {NHS_SHAPEFILE_PATH}")

    nhs_gdf = gpd.read_file(NHS_SHAPEFILE_PATH)
    sw_region = nhs_gdf[nhs_gdf["NHSER23NM"] == "South West"]

    print(f"Loaded {len(sw_region)} region(s) for NHS South West.")
    print(sw_region[['NHSER23CD', 'NHSER23NM']].drop_duplicates())
    return sw_region


# ----------------------------------------
# MAIN WORKFLOW
# ----------------------------------------
if __name__ == "__main__":
    download_zip_if_needed()
    extract_zip()
    lsoa_gdf = load_lsoa_shapefile()
    sw_region = load_nhs_sw_region()
