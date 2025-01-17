import os
from pystac import MediaType

# BASE_DIR = "/Volumes/T7SSD/"
# DEM_PATH = os.path.join(BASE_DIR, "lynker-spatial", "dem", "vrt", "USGS_1/ned_USGS_1.vrt")
# VRT_URI = "/vsicurl/https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/1/TIFF/USGS_Seamless_DEM_1.vrt"
# CATALOG_DIR = os.path.join(BASE_DIR, "hydrofabric-stac")

# mapping common file extensions to PySTAC MediaType enums
FILE_EXT_TO_MEDIA_TYPE = {
    ".tif": MediaType.COG,  
    ".cog": MediaType.COG,
    ".fgb": MediaType.FLATGEOBUF,
    ".geojson": MediaType.GEOJSON,
    ".gpkg": MediaType.GEOPACKAGE,
    ".geotiff": MediaType.GEOTIFF,
    ".tiff": MediaType.TIFF,
    ".tif": MediaType.TIFF,
    ".hdf": MediaType.HDF,
    ".h5": MediaType.HDF5,
    ".html": MediaType.HTML,
    ".jpg": MediaType.JPEG,
    ".jpeg": MediaType.JPEG,
    ".jp2": MediaType.JPEG2000,
    ".json": MediaType.JSON,
    ".parquet": MediaType.PARQUET,
    ".png": MediaType.PNG,
    ".txt": MediaType.TEXT,
    ".kml": MediaType.KML,
    ".xml": MediaType.XML,
    ".pdf": MediaType.PDF,
    ".zarr": MediaType.ZARR,
    ".nc": MediaType.NETCDF,  
}