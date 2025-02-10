import os
from pystac import MediaType

DEFAULT_ROOT_CATALOG_ID    = "root-catalog"
DEFAULT_ROOT_CATALOG_TITLE = f"{DEFAULT_ROOT_CATALOG_ID}-title"
DEFAULT_ROOT_CATALOG_DESC  = f"{DEFAULT_ROOT_CATALOG_ID}-desc" 

# mapping common file extensions to PySTAC MediaType enums
FILE_EXT_TO_MEDIA_TYPE = {
    # ".tif": MediaType.COG,  
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
