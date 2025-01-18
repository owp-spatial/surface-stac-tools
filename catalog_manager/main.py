import os
from pathlib import Path
import typing
from typing import Dict, List, Optional
from datetime import datetime

import pystac 
from pystac import Catalog, Collection, Item, Asset, MediaType, Extent, SpatialExtent, TemporalExtent

from catalog_manager.catalog_manager import setup_catalog_manager, CatalogManager
from catalog_manager.catalog_loader import get_catalog_loader, CatalogDataLoader, CatalogLoaderFactory

from catalog_manager.collection_manager import CollectionManager
from catalog_manager.item_manager import AbstractItemFactory, ItemFactoryManager, RasterItemFactory, VRTItemFactory
from catalog_manager.catalog_extents import GenericExtent
from catalog_manager.stac_metadata import Metadata, MetaDataExtractorFactory

import config.settings as settings


# Create and use the catalog manager
# settings.CATALOG_URI 

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

# --------------------------------------------------------------------------------------
# ----- Example usage -----
# --------------------------------------------------------------------------------------

catalog_manager.get_catalog().describe()
# catalog_manager.

catalog_manager.get_supported_data_types()
# VRT_URI="/Volumes/T7SSD/lynker-spatial/dem/vrt/USGS_1/ned_USGS_1.vrt"
# add a new collection
catalog_manager.add_child_collection(collection_id="3dep-usgs-30m", 
                                     title="USGS 3DEP 30m DEM", 
                                     description="USGS 3DEP 30m DEM"
                                     )

# add a VRT item to previously created collection (VRT_URI)
item = catalog_manager.add_item_to_collection(
    collection_id="3dep-usgs-30m",
    data_path=settings.VRT_URI,
    properties={"datetime": datetime.now()}
)

catalog_manager.add_child_collection(collection_id="coast-bathy", 
                                        title="Coastal Bathymetry",
                                        description="Coastal Bathymetry"
                                     )

# add a VRT item to previously created collection (VRT_URI)
item = catalog_manager.add_item_to_collection(
    collection_id="coast-bathy",
    data_path=settings.TIF_URI,
    properties={"datetime": datetime.now()}
)


cat = catalog_manager.get_catalog()

catalog_path = catalog_manager.catalog_path
cat.normalize_and_save(root_href=catalog_path, 
                           catalog_type=pystac.CatalogType.SELF_CONTAINED)
cat.normalize_hrefs(catalog_path)
cat.describe()
cat.save(catalog_type=pystac.CatalogType.SELF_CONTAINED, dest_href=catalog_path)

cata

catalog_manager.get_catalog().describe()
catalog_manager.get_catalog().get_all_collections()

# save the catalog
cat.normalize_and_save(root_href=catalog_path, 
                           catalog_type=pystac.CatalogType.SELF_CONTAINED)
catalog_manager.save_catalog()










# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------


# catalog_loader.load_catalog()

# catalog_manager = setup_catalog_manager(settings.CATALOG_URI, catalog_loader)
# catalog_manager.get_catalog()


# # Create a collection
# collection = catalog_manager.add_child_collection(
#     collection_id="my-collection",
#     title="My Collection",
#     description="Description"
# )

# # Create items (data type is inferred from extension)
# item = catalog_manager.create_item(
#     collection_id="my-collection",
#     data_path="path/to/data.tif",
#     properties={"datetime": datetime.now()}
# )

# # Check supported types
# supported_types = catalog_manager.get_supported_data_types()
# print(f"Supported data types: {supported_types}")