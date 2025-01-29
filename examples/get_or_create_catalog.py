import os
from os.path import basename
from pathlib import Path
import typing
from typing import Dict, List, Optional, Tuple, Union

from datetime import datetime
import json
from hashlib import md5
from dataclasses import dataclass

import pystac 
from pystac import Catalog, Collection, Item, Asset, MediaType, Extent, SpatialExtent, TemporalExtent
from pystac.extensions.projection import ProjectionExtension

from stac_manager.catalog_manager import setup_catalog_manager, CatalogManager
from stac_manager.catalog_loader import get_catalog_loader, CatalogDataLoader, CatalogLoaderFactory
from stac_manager.collection_manager import CollectionManager
from stac_manager.stac_metadata import Metadata, MetaDataExtractorFactory
from stac_manager.data_models import STACCollectionSource, STACItemSource

import config.settings as settings

# List out desired collections to create/update
collections = [
        STACCollectionSource(
            id = "conus",
            title = "CONUS title",
            description = "CONUS description"
        ),
        STACCollectionSource(
            id = "hawaii",
            title = "Hawaii title",
            description = "Hawaii description"
        ),
        ]

# URLs to Datasources
DATA_SOURCES = [
    "https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/1/TIFF/USGS_Seamless_DEM_1.vrt",
    "https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/13/TIFF/USGS_Seamless_DEM_13.vrt",

    # "https://noaa-nos-coastal-lidar-pds.s3.amazonaws.com/dem/NCEI_ninth_Topobathy_Hawaii_9428/index.html"
    "https://noaa-nos-coastal-lidar-pds.s3.amazonaws.com/dem/NCEI_ninth_Topobathy_Hawaii_9428/tiles/ncei19_n19x00_w156x00_2021v1.tif",
    "https://noaa-nos-coastal-lidar-pds.s3.amazonaws.com/dem/NCEI_ninth_Topobathy_Hawaii_9428/tiles/ncei19_n19x25_w155x50_2021v1.tif",
    ]

HTML_URLS = [
    "https://noaa-nos-coastal-lidar-pds.s3.amazonaws.com/dem/NCEI_ninth_Topobathy_Hawaii_9428/index.html"
]


# List of STAC Items that will be added to the collections specified above
items = [
    STACItemSource(
        collection_id = "conus",
        id = basename([i for i in DATA_SOURCES if "USGS_Seamless_DEM_1.vrt" in i][0]),
        data_path = [i for i in DATA_SOURCES if "USGS_Seamless_DEM_1.vrt" in i][0],
        properties = {"priority": 1}
    ),
    STACItemSource(
        collection_id = "conus",
        id = basename([i for i in DATA_SOURCES if "USGS_Seamless_DEM_13.vrt" in i][0]),
        data_path = [i for i in DATA_SOURCES if "USGS_Seamless_DEM_13.vrt" in i][0],
        properties = {"priority": 1}
    ),
    *(
        STACItemSource(
            collection_id="hawaii",
            id = basename(i),
            data_path= i,
            properties={"priority" : 2}
        ) for i in DATA_SOURCES if "ncei" in i.lower() and "hawaii" in i.lower()
    )
]


# --------------------------------------------------------------------------------------
# ----- Setup initial catalog manager -----
# --------------------------------------------------------------------------------------

catalog_manager = CatalogManager(
    catalog_path=settings.CATALOG_URI,
    id=settings.ROOT_CATALOG_ID,
    title=settings.ROOT_CATALOG_TITLE,
    description=settings.ROOT_CATALOG_DESCRIPTION
)

catalog_manager.describe()

# --------------------------------------------------------------------------------------
# ----- Go through list of collections and create the collection -----
# if it does not exist
# --------------------------------------------------------------------------------------
# manager2 = CatalogManager(
#     catalog_path="https://noaa-nos-coastal-lidar-pds.s3.amazonaws.com/dem/NCEI_ninth_Topobathy_Hawaii_9428/stac/tiles/ncei19_n19x00_w155x75_2021v1.json"
# )
# pystac.Catalog.from_file("https://noaa-nos-coastal-lidar-pds.s3.amazonaws.com/dem/NCEI_ninth_Topobathy_Hawaii_9428/stac/tiles/ncei19_n19x00_w155x75_2021v1.json")
# hawaii_item = pystac.Item.from_file("https://noaa-nos-coastal-lidar-pds.s3.amazonaws.com/dem/NCEI_ninth_Topobathy_Hawaii_9428/stac/tiles/ncei19_n19x00_w155x75_2021v1.json")
# print(json.dumps(hawaii_item.to_dict(), indent=4))

# manager2.describe()

for collection in collections:
    print(f"Collection:\n > {collection}")

    # add a new collection 
    catalog_manager.add_child_collection(
        collection_id=collection.id,
        title=collection.title,
        description=collection.description
        )

    print()

# --------------------------------------------------------------------------------------
# ----- Go through list of items and add the item to respective collection -----
# --------------------------------------------------------------------------------------

for item in items:
    print(f"Item:\n > {item}")

    # add items to collections 
    catalog_manager.add_item_to_collection(
        collection_id=item.collection_id,
        data_path=item.data_path,
        properties = item.properties
        )

    print()

catalog_manager.describe()

# --------------------------------------------------------------------------------------
# ----- Save catalog -----
# --------------------------------------------------------------------------------------
catalog_manager.save_catalog(catalog_type=pystac.CatalogType.SELF_CONTAINED)

catalog_manager.describe()