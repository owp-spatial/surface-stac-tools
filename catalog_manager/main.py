import os
from os.path import basename
from pathlib import Path
import typing
from typing import Dict, List, Optional, Tuple, Union
from datetime import datetime

import pystac 
from pystac import Catalog, Collection, Item, Asset, MediaType, Extent, SpatialExtent, TemporalExtent
from pystac.extensions.projection import ProjectionExtension

# from rasterio.io import DatasetReader, DatasetWriter, MemoryFile
# from rasterio.vrt import WarpedVRT

from catalog_manager.catalog_manager import setup_catalog_manager, CatalogManager
from catalog_manager.catalog_loader import get_catalog_loader, CatalogDataLoader, CatalogLoaderFactory

from catalog_manager.collection_manager import CollectionManager
from catalog_manager.item_manager import AbstractItemFactory, ItemFactoryManager, RasterItemFactory, VRTItemFactory
from catalog_manager.catalog_extents import GenericExtent
from catalog_manager.stac_metadata import Metadata, MetaDataExtractorFactory

import config.settings as settings

# --------------------------------------------------------------------------------------
# ----- Input variables -----
# --------------------------------------------------------------------------------------
COLLECTION_ID_1 = "tif-1"
COLLECTION_ID_2 = "tif-2"
# COLLECTION_ID_3 = basename(settings.VRT_URI).split(".")[0]
COLLECTION_ID_3 = "vrt-1"

# --------------------------------------------------------------------------------------
# ----- Get data loader and meta data extractor factory -----
# --------------------------------------------------------------------------------------

catalog_loader = CatalogLoaderFactory.create_loader(settings.CATALOG_URI)
metadata_extractor_factory = MetaDataExtractorFactory()

# --------------------------------------------------------------------------------------
# ----- Setup initial catalog manager -----
# --------------------------------------------------------------------------------------

catalog_manager = CatalogManager(
    catalog_path=settings.CATALOG_URI,
    catalog_loader=catalog_loader,
    metadata_extractor_factory=metadata_extractor_factory
)

# Set the catalog title and description
catalog_manager.set_catalog_title(settings.ROOT_CATALOG_TITLE)
catalog_manager.set_catalog_description(settings.ROOT_CATALOG_DESCRIPTION)

vars(catalog_manager.get_catalog())
# catalog_manager.get_catalog()
# catalog_manager.describe()
# print(list(catalog_manager.get_items()))

# --------------------------------------------------------------------------------------
# ----- Example usage 1 (remote TIFs) -----
# --------------------------------------------------------------------------------------

# ADD 3 collections with 1 item each

catalog_manager.describe()
catalog_manager.get_supported_data_types()

# # add a new collection 1
catalog_manager.add_child_collection(collection_id=COLLECTION_ID_1, 
                                     title=f"{COLLECTION_ID_1}-title", 
                                     description=f"{COLLECTION_ID_1}-desc"
                                     )

catalog_manager.describe() 

# Add TIF 1 item to collection 1
catalog_manager.add_item_to_collection(
    collection_id=COLLECTION_ID_1,
    data_path=settings.TIF_URI_1
    # properties={"datetime": datetime.now()}
)

# import json 
# print(json.dumps(list(catalog_manager._find_collection(COLLECTION_ID_1).get_items())[0].to_dict(), indent = 4))
# list(catalog_manager._find_collection(COLLECTION_ID_1).get_items())[0].assets.get('ned04b').to_dict()

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
    data_path=settings.TIF_URI_2
    # properties={"datetime": datetime.now()}
)


# add new collection 3
catalog_manager.add_child_collection(collection_id=COLLECTION_ID_3, 
                                     title=f"{COLLECTION_ID_3}-title", 
                                     description=f"{COLLECTION_ID_3}-desc"
                                     )

catalog_manager.describe()
# settings.VRT_URI
# Add TIF 2 item to collection 2
catalog_manager.add_item_to_collection(
    collection_id=COLLECTION_ID_3,
    data_path=settings.VRT_URI
    # properties={"datetime": datetime.now()}
)


catalog_manager.describe()
# import json
# print(json.dumps(list(catalog_manager._find_collection(COLLECTION_ID_3).get_all_items())[0].to_dict(), indent=4))

# TODO: Save
catalog_manager.save_catalog(catalog_type=pystac.CatalogType.SELF_CONTAINED)
# catalog_manager.save_catalog(catalog_type=pystac.CatalogType.ABSOLUTE_PUBLISHED)
# catalog_manager.save_catalog(catalog_type=pystac.CatalogType.RELATIVE_PUBLISHED)

# catalog_manager.save_catalog()

# list(pystac.CatalogType)

# catalog_type = pystac.CatalogType.SELF_CONTAINED
# catalog_type = None
# type(catalog_type)
# isinstance(catalog_type, pystac.CatalogType)
# catalog_type in pystac.CatalogType

# cat = catalog_manager.get_catalog()


# cat.normalize_and_save(root_href=settings.CATALOG_URI, 
#                            catalog_type=pystac.CatalogType.SELF_CONTAINED)
# cat.normalize_hrefs(settings.CATALOG_URI)
# cat.describe()
# cat.save(catalog_type=pystac.CatalogType.SELF_CONTAINED, dest_href=settings.CATALOG_URI)

# catalog_manager.get_catalog().describe()
# catalog_manager.get_catalog().get_all_collections()

# # save the catalog
# cat.normalize_and_save(root_href=settings.CATALOG_URI, 
#                            catalog_type=pystac.CatalogType.SELF_CONTAINED)
# catalog_manager.save_catalog()
