#%%
def backmap_imd_from_2011(lsoa_gdf_2021: gpd.GeoDataFrame, imd_df_2011: pd.DataFrame, lookup_path: str) -> gpd.GeoDataFrame:
    """
    Fill remaining IMD gaps by mapping LSOA21CD to LSOA11CD using ONS lookup,
    then merging 2011-based IMD values.

    Parameters
    ----------
    lsoa_gdf_2021 : GeoDataFrame
        2021 LSOAs with possible IMD gaps.
    imd_df_2011 : DataFrame
        Original IMD data keyed by LSOA11CD.
    lookup_path : str
        CSV with LSOA11CD to LSOA21CD mappings.

    Returns
    -------
    GeoDataFrame
        Updated with backfilled IMD_Rank values.
    """
    # Load and prepare lookup
    lookup_df = pd.read_csv(lookup_path)[['LSOA11CD', 'LSOA21CD']].dropna().astype(str)
    imd_df_2011 = imd_df_2011.astype(str)

    # Identify missing IMD rows
    missing = lsoa_gdf_2021[lsoa_gdf_2021['IMD_Rank'].isna()].copy()
    backmatch = missing.merge(lookup_df, on='LSOA21CD', how='left')

    # Merge on 2011-based IMD
    imd_merged = backmatch.merge(imd_df_2011[['LSOA11CD', 'IMD19']], on='LSOA11CD', how='left')
    imd_merged['IMD19'] = pd.to_numeric(imd_merged['IMD19'], errors='coerce')

    updated_rows = imd_merged['IMD19'].notna().sum()
    print(f"Backmapped IMD values for {updated_rows} additional LSOAs")

    # Inject back into original GeoDataFrame
    lsoa_gdf_2021.loc[imd_merged.index, 'IMD_Rank'] = imd_merged['IMD19'].values

    return lsoa_gdf_2021

#%%
# Apply backmapping
lsoa_sw = backmap_imd_from_2011(lsoa_sw, imd_df, lookup_path)

# Final diagnostic
remaining_missing = lsoa_sw['IMD_Rank'].isna().sum()
print(f"Remaining missing IMD values after backmapping: {remaining_missing}")
