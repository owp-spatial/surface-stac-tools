import os
from os.path import basename
from pathlib import Path
import typing
from typing import Dict, List, Optional, Tuple, Union
from datetime import datetime
import json
from hashlib import md5

import pystac 
from pystac import Catalog, Collection, Item, Asset, MediaType, Extent, SpatialExtent, TemporalExtent
from pystac.extensions.projection import ProjectionExtension

from stac_manager.catalog_manager import setup_catalog_manager, CatalogManager
from stac_manager.catalog_loader import get_catalog_loader, CatalogDataLoader, CatalogLoaderFactory

from stac_manager.collection_manager import CollectionManager
from stac_manager.item_manager import AbstractItemFactory, ItemFactoryManager, RasterItemFactory, VRTItemFactory
from stac_manager.catalog_extents import GenericExtent
from stac_manager.stac_metadata import Metadata, MetaDataExtractorFactory

import config.settings as settings

# --------------------------------------------------------------------------------------
# ----- Input variables -----
# --------------------------------------------------------------------------------------
COLLECTION_ID_1 = "tif-1"
COLLECTION_ID_2 = "tif-2"
COLLECTION_ID_3 = "vrt-1"

# --------------------------------------------------------------------------------------
# ----- Get data loader and meta data extractor factory -----
# --------------------------------------------------------------------------------------

# catalog_loader = CatalogLoaderFactory.create_loader(settings.CATALOG_URI)
# metadata_extractor_factory = MetaDataExtractorFactory()

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

# catalog_loader = CatalogLoaderFactory.create_loader(settings.CATALOG_URI)
# metadata_extractor_factory = MetaDataExtractorFactory()
# catalog_manager = CatalogManager(
#     catalog_path=settings.CATALOG_URI,
#     catalog_loader=catalog_loader,
#     metadata_extractor_factory=metadata_extractor_factory
# )

# # Set the catalog title and description
# catalog_manager.set_catalog_title(settings.ROOT_CATALOG_TITLE)
# catalog_manager.set_catalog_description(settings.ROOT_CATALOG_DESCRIPTION)
# vars(catalog_manager.get_catalog())

catalog_manager.describe()
catalog_manager.get_supported_data_types()

# --------------------------------------------------------------------------------------
# ----- Example usage 1 (remote TIFs) -----
# --------------------------------------------------------------------------------------

# Summary:
# - ADD 3 collections with 1 item each

# # add a new collection 1
catalog_manager.add_child_collection(collection_id=COLLECTION_ID_1, 
                                     title=f"{COLLECTION_ID_1}-title", 
                                     description=f"{COLLECTION_ID_1}-desc"
                                     )

catalog_manager.describe() 

# Add TIF 1 item to collection 1
catalog_manager.add_item_to_collection(
    collection_id=COLLECTION_ID_1,
    data_path=settings.TIF_URI_1,
    properties={"priority": 2}
)

for children in catalog_manager.get_children():
    print(children)
    for item in children.get_all_items():
        print(f" > {item}")
        print(json.dumps(item.to_dict(), indent=4)) 

catalog_manager.describe()

# add new collection 2
catalog_manager.add_child_collection(collection_id=COLLECTION_ID_2, 
                                     title=f"{COLLECTION_ID_2}-title", 
                                     description=f"{COLLECTION_ID_2}-desc"
                                     )

catalog_manager.describe()

# Add TIF 2 item to collection 2
catalog_manager.add_item_to_collection(
    collection_id=COLLECTION_ID_2,
    data_path=settings.TIF_URI_2,
    properties={"priority": 1}
)


# add new collection 3
catalog_manager.add_child_collection(collection_id=COLLECTION_ID_3, 
                                     title=f"{COLLECTION_ID_3}-title", 
                                     description=f"{COLLECTION_ID_3}-desc"
                                     )

catalog_manager.describe()

# Add TIF 2 item to collection 2
catalog_manager.add_item_to_collection(
    collection_id=COLLECTION_ID_3,
    data_path=settings.VRT_URI,
    properties={"priority": 0}
)

catalog_manager.describe()

# TODO: Save

catalog_manager.save_catalog(catalog_type=pystac.CatalogType.SELF_CONTAINED)