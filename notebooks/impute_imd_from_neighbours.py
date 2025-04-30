#%%
from sklearn.neighbors import NearestNeighbors
import numpy as np

def impute_imd_from_neighbours(gdf: gpd.GeoDataFrame, imd_col: str = 'IMD_Rank', k: int = 5) -> gpd.GeoDataFrame:
    """
    Impute missing IMD scores using k-nearest neighbours based on spatial centroid proximity.

    Parameters
    ----------
    gdf : GeoDataFrame
        Must contain 'geometry' and IMD column.
    imd_col : str
        Column containing IMD values to impute.
    k : int
        Number of neighbours to use for averaging.

    Returns
    -------
    GeoDataFrame
        Updated with imputed IMD scores and 'imd_imputed' indicator.
    """
    gdf = gdf.copy()
    gdf['centroid'] = gdf.geometry.centroid

    missing_mask = gdf[imd_col].isna()
    coords_all = np.array(list(gdf['centroid'].apply(lambda geom: (geom.x, geom.y))))
    coords_valid = coords_all[~missing_mask]
    coords_missing = coords_all[missing_mask]

    nn = NearestNeighbors(n_neighbors=k)
    nn.fit(coords_valid)

    distances, indices = nn.kneighbors(coords_missing)
    imd_values = gdf.loc[~missing_mask, imd_col].values
    estimated = imd_values[indices].mean(axis=1)

    gdf.loc[missing_mask, imd_col] = estimated
    gdf['imd_imputed'] = False
    gdf.loc[missing_mask, 'imd_imputed'] = True

    return gdf.drop(columns='centroid')

#%%
# Apply imputation to missing IMD values
lsoa_sw = impute_imd_from_neighbours(lsoa_sw, imd_col='IMD_Rank', k=5)

# Summary output
n_imputed = lsoa_sw['imd_imputed'].sum()
print(f"IMD scores imputed using k-NN: {n_imputed}")
