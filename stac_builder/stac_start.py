import os
import json
import typing
from typing import List, Dict, Any, Tuple

import rasterio
import rasterio.vrt 

import urllib.request
import pystac

from datetime import datetime, timezone
from shapely.geometry import Polygon, mapping
from tempfile import TemporaryDirectory

from stac_builder.stac_utils import get_bbox_and_footprint, get_vrt_metadata, get_media_type
from stac_builder.stac_catalog import STACBuilder, STACCatalog, STACAsset, STACCollection, STACItem, MetaDataExtractorFactory, ExtentBuilder
from stac_builder.constants import BASE_DIR, DEM_PATH, VRT_URI, CATALOG_DIR

# ----------------------------------------------    
# ---- STAC Builder ----
# ----------------------------------------------    
CATALOG_DIR
CATALOG_ID = "hydrofabric-surface-catalog"
CATALOG_TITLE = "Hydrofabric Surface STAC Catalog"
CATALOG_DESCRIPTION = 'Comprehensive STAC catalog of relevent Hydrofabric Surfaces'

COLLECTION_ID = "3dep-usgs-1"
COLLECTION_DESCRIPTION = "3DEP 30m DEM STAC collection description"
COLLECTION_VRT_PATH = DEM_PATH 
# COLLECTION_VRT_PATH = VRT_URI


builder = STACBuilder()
builder = builder.create_catalog(CATALOG_ID, CATALOG_DESCRIPTION, CATALOG_TITLE)
builder = builder.add_collection_from_vrt(COLLECTION_ID, COLLECTION_DESCRIPTION, COLLECTION_VRT_PATH)
builder.catalog.catalog.describe()
catalog = builder.build()
catalog.catalog.describe()
# Save the catalog

catalog.save(CATALOG_DIR)

catalog = pystac.Catalog.from_file(f"{CATALOG_DIR}/catalog.json")
catalog.get_child("3dep-usgs-1").describe()

os.listdir("/Users/anguswatters/Desktop/lynker-spatial/domain_with_fema/dem/bathy_texas_ncei_5.tif")
TIF_FILE_LIST = [
    "/Users/anguswatters/Desktop/lynker-spatial/domain_with_fema/dem/bathy_texas_ncei_5.tif"
]

builder = builder.add_collection_from_files("coastal-bathy", "Other coastal-bathy TIFs STAC Collection", TIF_FILE_LIST)
catalog = builder.build()
catalog.save(CATALOG_DIR)
CATALOG_DIR

type(catalog.catalog)

catalog.catalog.normalize_hrefs("/vsicurl/https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/1/TIFF/")
VRT_URI
catalog.catalog
# builder
# src = rasterio.open(DEM_PATH)
# src.files[1]

# ExtentBuilder.from_file(src.files[1])


catalog = (builder
    .create_catalog("my-catalog", "A test catalog", "Test Catalog")
    .add_collection_from_files(
        "collection-1",
        "First collection",
        ["/path/to/file1.tif", "/path/to/file2.tif"],
        {"spatial": {"bbox": [[-180, -90, 180, 90]]},
         "temporal": {"interval": [["2020-01-01T00:00:00Z", None]]}}
    )
    .build())

# ----------------------------------------------    
# ---- Root catalog ----
# ----------------------------------------------    

catalog = pystac.Catalog(id='hydrofabric-surface', 
                         description='Comprehensive STAC catalog of relevent Hydrofabric Surfaces'
                         )


# ----------------------------------------------    
# ---- 3DEP Item ----
# ----------------------------------------------    
src = rasterio.open(VRT_URI)
src = rasterio.open(DEM_PATH)
src.files[1]



src.files
src.close()
DEM_PATH

metadata_extractor = MetaDataExtractorFactory.get_metadata_extractor(VRT_URI)
metadata_extractor.extract_metadata()

MetaDataExtractorFactory.get_metadata_extractor(src.files[1]).extract_metadata().get("dfgs")

src
src.close()
dir(src)
src.files
src.xy
src.crs
src.bounds
# src.read(1)

def create_item_from_vrt(vrt):

    bbox, footprint, vrt_files = get_vrt_metadata(vrt)
    datetime_utc = datetime.now(tz=timezone.utc)

    item = pystac.Item(id=vrt,
                 geometry=footprint,
                 bbox=bbox,
                 datetime=datetime_utc,
                 properties={}
                 )

    for i, file_path in enumerate(vrt_files):
        # print(f"i: {i}\nfilepath: {file_path}")

        # skip over the actual ".vrt" file if its in the list of files 
        if file_path.endswith(".vrt"):
            continue 

        item.add_asset(
            key = os.path.basename(file_path), 
            asset = pystac.Asset(href = file_path, media_type=get_media_type(file_path))
            )

    return item 


vars(pystac.MediaType )

def create_add_asset_kwargs(path, key=None, media_type:pystac.MediaType = None) -> Dict:
    if not key:
        key = os.path.basename(path)

    if not media_type:
        media_type = get_media_type(path)

    return {
        "key" : key,
        "asset" : pystac.Asset(
            href = path,
            media_type=media_type
            )
        }





    
with rasterio.open(DEM_PATH) as src:
    if isinstance(src, rasterio.vrt.WarpedVRT):
        # for warped vrts, get the source dataset
        sources = [src.src_dataset.name]
        sources
        type(src)

    else:
        # for regular vrts, get all source paths
        sources = [src_path for src_path in src.files if src_path != DEM_PATH]


def extract_vrt_sources(vrt_path: str) -> List[str]:
    """extract source files from a vrt"""
    with rasterio.open(vrt_path) as src:
        if isinstance(src, rasterio.vrt.WarpedVRT):
            # for warped vrts, get the source dataset
            sources = [src.src_dataset.name]
        else:
            # for regular vrts, get all source paths
            sources = [src_path for src_path in src.files if src_path != vrt_path]
    
    return sources


# ----------------------------------------------    
# ---- Root catalog ----
# ----------------------------------------------    

# Set temporary directory to store source data
tmp_dir = TemporaryDirectory()
img_path = os.path.join(tmp_dir.name, 'image.tif')
img_path


# Fetch and store data
url = ('https://spacenet-dataset.s3.amazonaws.com/'
       'spacenet/SN5_roads/train/AOI_7_Moscow/MS/'
       'SN5_roads_train_AOI_7_Moscow_MS_chip996.tif')
urllib.request.urlretrieve(url, img_path)


catalog = pystac.Catalog(id='tutorial-catalog', 
                         description='This catalog is a basic demonstration catalog utilizing a scene from SpaceNet 5.'
                         )
list(catalog.get_children())
list(catalog.get_all_collections())
list(catalog.get_all_items())


print(json.dumps(catalog.to_dict(), indent=4))

# def create_raster_item_metadata(path):


# Run the function and print out the results
bbox, footprint = get_bbox_and_footprint(img_path)
datetime_utc = datetime.now(tz=timezone.utc)


print("bbox: ", bbox, "\n")
print("footprint: ", footprint)

item = pystac.Item(id='local-image',
                 geometry=footprint,
                 bbox=bbox,
                 datetime=datetime_utc,
                 properties={})


