"""
geospatial_utils.py

Utility functions for processing UK LSOA boundaries by NHS England regions.

Author: [Your Name]
Created: 2025-04-11
"""

import geopandas as gpd


def prepare_region_lsoas(lsoa_path: str, nhs_path: str, region_name: str) -> gpd.GeoDataFrame:
    """
    Load and clip UK LSOA boundaries to a specified NHS England region.

    This function extracts LSOAs that fall within the geographical boundary of a
    given NHS England region by spatially clipping them to that region.

    Parameters
    ----------
    lsoa_path : str
        Path to LSOA boundary file (e.g., Shapefile or GeoPackage).
    nhs_path : str
        Path to NHS England regional boundary file (Shapefile).
    region_name : str
        The exact NHS region name to filter by. Valid options include:
            - 'London'
            - 'South East'
            - 'South West'
            - 'East of England'
            - 'North West'
            - 'Midlands'
            - 'North East and Yorkshire'

    Returns
    -------
    GeoDataFrame
        A clipped GeoDataFrame containing only the LSOAs in the selected NHS region.

    Raises
    ------
    ValueError
        If the provided region_name is not found in the NHS region shapefile.

    Example
    -------
    >>> lsoa_path = "../data/lsoa_boundaries.shp"
    >>> nhs_path = "../data/nhs_regions.shp"
    >>> gdf = prepare_region_lsoas(lsoa_path, nhs_path, "South West")
    >>> print(gdf.head())
    """

    # Load spatial datasets
    lsoa_gdf = gpd.read_file(lsoa_path)
    nhs_gdf = gpd.read_file(nhs_path)

    # Validate region name
    valid_regions = nhs_gdf["NHSER23NM"].unique().tolist()
    if region_name not in valid_regions:
        raise ValueError(
            f"❌ Region '{region_name}' not found in NHS shapefile.\n"
            f"✅ Available regions are:\n- " + "\n- ".join(valid_regions)
        )

    # Filter NHS boundary to specified region
    target_region = nhs_gdf[nhs_gdf["NHSER23NM"] == region_name]

    # Check and match CRS
    if lsoa_gdf.crs != target_region.crs:
        print("ℹ️ CRS mismatch detected. Reprojecting LSOAs to match NHS region...")
        lsoa_gdf = lsoa_gdf.to_crs(target_region.crs)

    # Clip LSOAs to the region boundary
    clipped = gpd.clip(lsoa_gdf, target_region)

    # Keep only relevant fields
    clipped = clipped[["LSOA21CD", "LSOA21NM", "geometry"]]

    return clipped


# 🧪 Manual test block for script-based use
if __name__ == "__main__":
    print("🧭 Testing prepare_region_lsoas() for selected NHS regions...")

    lsoa_path = "../data/raw/Lower_layer_Super_Output_Areas_(December_2021)_Boundaries_EW_BFC_(V10).shp"
    nhs_path = "../data/raw/NHS_England_(Regions)_(December_2023)_EN_BGC.shp"

    try:
        # Load NHS boundary and preview available regions
        nhs_regions = gpd.read_file(nhs_path)
        region_names = nhs_regions["NHSER23NM"].unique().tolist()

        print("\n✅ Available NHS England Regions:")
        for r in region_names:
            print(f" - {r}")

        # Try a few known valid regions
        for region in ["London", "South West", "North East and Yorkshire"]:
            print(f"\n🔍 Processing region: {region}")
            result = prepare_region_lsoas(lsoa_path, nhs_path, region)
            print(f"   ✅ Clipped {len(result)} LSOAs for region: {region}")

    except Exception as e:
        print(f"❌ Error occurred: {e}")
