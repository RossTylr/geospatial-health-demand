import os
import gdown
import zipfile
import geopandas as gpd

# -----------------------------
# CONFIGURATION
# -----------------------------
FILE_ID = "1sIKAOZHAEhYfwEjDomEnpiYupSeFe6i"  # Corrected file ID from your Google Drive
ZIP_PATH = "data/raw/Lower_Layer_LSOA_2021.zip"
EXTRACT_DIR = "data/raw/lsoa_shapefile"
SHP_FILENAME = "Lower_layer_Super_Output_Areas_(December_2021)_Boundaries_EW_BFC_(V10).shp"


# -----------------------------
# DOWNLOAD IF NOT EXISTS
# -----------------------------
def download_zip_if_needed():
    if not os.path.exists(ZIP_PATH):
        os.makedirs(os.path.dirname(ZIP_PATH), exist_ok=True)
        url = f"https://drive.google.com/uc?id={FILE_ID}"
        print(f"Downloading shapefile zip from: {url}")
        gdown.download(url, ZIP_PATH, quiet=False)
    else:
        print("Zip file already exists — skipping download.")


# -----------------------------
# EXTRACT IF NOT ALREADY DONE
# -----------------------------
def extract_zip():
    if not os.path.exists(EXTRACT_DIR):
        print("Extracting shapefile zip...")
        with zipfile.ZipFile(ZIP_PATH, 'r') as zip_ref:
            zip_ref.extractall(EXTRACT_DIR)
    else:
        print("Shapefile already extracted — skipping.")


# -----------------------------
# LOAD SHAPEFILE WITH GEOPANDAS
# -----------------------------
def load_lsoa_shapefile():
    shapefile_path = os.path.join(EXTRACT_DIR, SHP_FILENAME)
    if not os.path.exists(shapefile_path):
        raise FileNotFoundError(f"Shapefile not found at {shapefile_path}")

    gdf = gpd.read_file(shapefile_path)
    print("Shapefile successfully loaded.")
    return gdf


# -----------------------------
# MAIN EXECUTION
# -----------------------------
if __name__ == "__main__":
    download_zip_if_needed()
    extract_zip()
    gdf = load_lsoa_shapefile()
    print(gdf.head())
