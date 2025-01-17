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
from stac_builder.stac_catalog import STACBuilder, STACCatalog, STACAsset, STACCollection, STACItem, \
    MetaDataExtractorFactory, ExtentBuilder
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

# load vrt from file
pystac.Item.from_file(COLLECTION_VRT_PATH)
