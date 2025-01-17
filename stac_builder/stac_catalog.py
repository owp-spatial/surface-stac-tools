from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Dict, List, Optional, Union
import pystac
from pystac import Catalog, Collection, Item, Asset, MediaType, Extent, SpatialExtent, TemporalExtent

import os

from stac_builder.stac_metadata import MetaDataExtractorFactory
import os
from abc import ABC, abstractmethod
import json
import urllib.request
from datetime import datetime, timezone
from dataclasses import dataclass
from typing import List, Optional, Dict, Any

import rasterio
import pystac
from pystac import MediaType
from pathlib import Path
import uuid

from shapely.geometry import Polygon, mapping
from tempfile import TemporaryDirectory
from stac_builder.constants import BASE_DIR, DEM_PATH, CATALOG_DIR, FILE_EXT_TO_MEDIA_TYPE

class STACAsset:
    """
    Wrapper class for PYSTAC Asset with additional functionality.
    """
    def __init__(self, href: str, title: Optional[str] = None, 
                 description: Optional[str] = None, media_type: Optional[str] = None,
                 roles: Optional[List[str]] = None):
        self.asset = pystac.Asset(
            href=href,
            title=title,
            description=description,
            media_type=media_type,
            roles=roles
        )
        self.metadata_extractor = MetaDataExtractorFactory.get_metadata_extractor(href)
        
    def extract_metadata(self):
        """Extract metadata from the asset file."""
        return self.metadata_extractor.extract_metadata()

class STACItem:
    """
    Wrapper class for PYSTAC Item with additional functionality.
    """
    def __init__(self, id: str, geometry: dict, bbox: List[float], 
                 datetime: datetime, properties: Dict):
        self.item = pystac.Item(
            id=id,
            geometry=geometry,
            bbox=bbox,
            datetime=datetime,
            properties=properties
        )
        self.assets: Dict[str, STACAsset] = {}

    def add_asset(self, key: str, asset: STACAsset) -> None:
        """Add an asset to the item."""
        self.assets[key] = asset
        self.item.add_asset(key, asset.asset)

    def remove_asset(self, key: str) -> None:
        """Remove an asset from the item."""
        if key in self.assets:
            self.item.assets.pop(key)
            self.assets.pop(key)

    def get_assets(self) -> Dict[str, STACAsset]:
        """Get all assets associated with this item."""
        return self.assets

class STACCollection:
    """
    Wrapper class for PYSTAC Collection with additional functionality.
    """
    def __init__(self, id: str, 
                 description: str, 
                 extent: dict, 
                 title: Optional[str] = None, 
                 license: str = "proprietary"):
        self.collection = pystac.Collection(
            id=id,
            description=description,
            extent=extent,
            title=title,
            license=license
        )
        self.items: Dict[str, STACItem] = {}

    def add_item(self, item: STACItem) -> None:
        """Add an item to the collection."""
        self.items[item.item.id] = item
        self.collection.add_item(item.item)

    def remove_item(self, item_id: str) -> None:
        """Remove an item from the collection."""
        if item_id in self.items:
            item = self.items.pop(item_id)
            self.collection.remove_item(item.item)

    def get_items(self) -> Dict[str, STACItem]:
        """Get all items in the collection."""
        return self.items

class STACCatalog:
    """
    Wrapper class for PYSTAC Catalog with additional functionality.
    """
    def __init__(self, id: str, description: str, title: Optional[str] = None):
        self.catalog = pystac.Catalog(
            id=id,
            description=description,
            title=title
        )
        self.collections: Dict[str, STACCollection] = {}

    def add_collection(self, collection: STACCollection) -> None:
        """Add a collection to the catalog."""
        self.collections[collection.collection.id] = collection
        self.catalog.add_child(collection.collection)

    def remove_collection(self, collection_id: str) -> None:
        """Remove a collection from the catalog."""
        if collection_id in self.collections:
            collection = self.collections.pop(collection_id)
            self.catalog.remove_child(collection.collection)

    def get_collections(self) -> Dict[str, STACCollection]:
        """Get all collections in the catalog."""
        return self.collections

    def save(self, catalog_dir: str) -> None:
        """Save the STAC catalog to disk."""
        self.catalog.normalize_and_save(
            root_href=os.path.join(catalog_dir, "catalog.json"),
            catalog_type=pystac.CatalogType.SELF_CONTAINED
        )
class ExtentBuilder:
    """
    Helper class to build STAC extent dictionaries from geospatial files.
    """
    def __init__(self):
        self.bbox = None
        self.temporal_interval = None
        
    def update_bbox(self, new_bbox: List[float]) -> None:
        """
        Update the current bbox with a new bbox, expanding if necessary.
        """
        if self.bbox is None:
            self.bbox = new_bbox
        else:
            self.bbox = [
                min(self.bbox[0], new_bbox[0]),  # min x
                min(self.bbox[1], new_bbox[1]),  # min y
                max(self.bbox[2], new_bbox[2]),  # max x
                max(self.bbox[3], new_bbox[3])   # max y
            ]
    
    def update_temporal_interval(self, datetime_value: datetime) -> None:
        """
        Update the temporal interval with a new datetime value.
        Ensures datetime is timezone-aware.
        """
        # Make datetime timezone-aware if it isn't already
        if datetime_value.tzinfo is None:
            datetime_value = datetime_value.replace(tzinfo=timezone.utc)
            
        if self.temporal_interval is None:
            self.temporal_interval = [datetime_value, datetime_value]
        else:
            self.temporal_interval = [
                min(self.temporal_interval[0], datetime_value),
                max(self.temporal_interval[1], datetime_value)
            ]

    @classmethod
    def from_files(cls, file_paths: List[str]) -> Dict:
        """
        Create an extent dictionary from a list of files.
        
        Args:
            file_paths: List of paths to geospatial files
            
        Returns:
            Dict containing STAC-compliant extent information
        """
        builder = cls()
        
        for file_path in file_paths:
            extractor = MetaDataExtractorFactory.get_metadata_extractor(file_path)
            metadata = extractor.extract_metadata()
            
            # Update spatial extent
            if metadata.get('bbox'):
                builder.update_bbox(metadata.get('bbox'))
            
            # Update temporal extent if available
            # Note: You might want to extract this from file metadata
            # For now, using current time as an example
            builder.update_temporal_interval(datetime.utcnow())
        
        return builder.build()

    @classmethod
    def from_file(cls, file_path: str) -> Dict:
        """
        Create an extent dictionary from a file path.
        
        Args:
            file_path: str path to geospatial files
            
        Returns:
            Dict containing STAC-compliant extent information
        """
        builder = cls()
        
        extractor = MetaDataExtractorFactory.get_metadata_extractor(file_path)
        metadata = extractor.extract_metadata()
        
        # Update spatial extent
        if metadata.get('bbox'):
            builder.update_bbox(metadata.get('bbox'))
        
        # Update temporal extent if available
        # Note: You might want to extract this from file metadata
        # For now, using current time as an example
        builder.update_temporal_interval(datetime.utcnow())
        
        return builder.build()

    @classmethod
    def from_vrt(cls, vrt_path: str) -> Dict:
        """
        Create an extent dictionary from a VRT file and its sources.
        
        Args:
            vrt_path: Path to VRT file
            
        Returns:
            Dict containing STAC-compliant extent information
        """
        builder = cls()
        
        # First process the VRT file itself
        extractor = MetaDataExtractorFactory.get_metadata_extractor(vrt_path)
        metadata = extractor.extract_metadata()
        
        if metadata.get('bbox'):
            builder.update_bbox(metadata.get('bbox'))
        
        # Process all files referenced in the VRT
        # print(f"metadata: {metadata}")

        # vrt_files = metadata.get('vrt_files', {})
        vrt_files = metadata.get('vrt_files', {}).get("files", [])
        for file_path in vrt_files:
            if os.path.exists(file_path):
                file_extractor = MetaDataExtractorFactory.get_metadata_extractor(file_path)
                file_metadata = file_extractor.extract_metadata()
                
                if file_metadata.get('bbox'):
                    builder.update_bbox(file_metadata.get('bbox'))
                
                # Update temporal extent if available
                builder.update_temporal_interval(datetime.utcnow())
        
        return builder.build()

    def build(self) -> Extent:
        """
        Build a PySTAC Extent object.
        
        If bbox is None, uses global extent [-180, -90, 180, 90].
        If temporal_interval is None, uses [current_time, current_time].
        
        Returns:
            pystac.Extent object containing spatial and temporal extent information
        """
        # Default to global extent if no bbox is available
        if self.bbox is None:
            self.bbox = [-180.0, -90.0, 180.0, 90.0]
        
        # Default to current time for both start and end if no temporal interval
        if self.temporal_interval is None:
            current_time = datetime.now(timezone.utc)
            self.temporal_interval = [current_time, current_time]
            
        # Create and return a proper PySTAC Extent object
        return Extent(
            spatial=SpatialExtent(
                bboxes=[self.bbox]
            ),
            temporal=TemporalExtent(
                intervals=[[
                    self.temporal_interval[0],  # Pass datetime objects directly
                    self.temporal_interval[1]   # Pass datetime objects directly
                ]]
            )
        )

class STACBuilder:
    """
    Builder class to facilitate creating STAC catalogs from files.
    """
    def __init__(self):
        self.catalog: Optional[STACCatalog] = None
        
    def create_catalog(self, 
                       id: str, 
                       description: str, 
                       title: Optional[str] = None
                       ) -> 'STACBuilder':
        """Create a new STAC catalog."""
        self.catalog = STACCatalog(id, description, title)
        return self
    
    def _process_file(self, file_path: str) -> STACItem:
        """Helper method to create a STAC item from a file."""
        extractor = MetaDataExtractorFactory.get_metadata_extractor(file_path)
        metadata = extractor.extract_metadata()
        
        item = STACItem(
            id=os.path.basename(file_path),
            geometry=metadata.get('geometry'),
            bbox=metadata.get('bbox'),
            datetime=datetime.utcnow(),  # You might want to extract this from the file
            properties={}
        )
        
        asset = STACAsset(
            href=file_path,
            media_type=extractor.get_media_type(file_path)
        )
        item.add_asset('data', asset)
        
        return item

    def _get_vrt_files(self, vrt_path: str) -> List[str]:
        """Extract list of files from VRT metadata."""
        extractor = MetaDataExtractorFactory.get_metadata_extractor(vrt_path)
        metadata = extractor.extract_metadata()
        return metadata.get('vrt_files', {}).get('files', [])   
        # return metadata.get('vrt_files', {})
    
    def add_collection_from_files(self, 
                                  collection_id: str, 
                                  description: str, 
                                  file_paths: List[str], 
                                  extent: Optional[Dict] = None) -> 'STACBuilder':
        """
        Create a collection from a list of files and add it to the catalog.
        """
        if not self.catalog:
            raise ValueError("Catalog must be created first")
        
        # try and get extent if one is not given 
        if extent is None:
            extent = ExtentBuilder.from_files(file_paths)

        collection = STACCollection(collection_id, description, extent)
        
        for file_path in file_paths:
            item = self._process_file(file_path)
            collection.add_item(item)
            
        self.catalog.add_collection(collection)
        return self

    def add_collection_from_vrt(self, 
                                collection_id: str, 
                                description: str, 
                                vrt_path: str, 
                                extent: Optional[Dict] = None
                                ) -> 'STACBuilder':
        """
        Create a collection from a VRT file and add it to the catalog.
        If extent is not provided, it will be calculated from the VRT and its source files.
        """
        if not self.catalog:
            raise ValueError("Catalog must be created first")
        # extent = None
        # catalog = catalog.catalog
        # vrt_path = COLLECTION_VRT_PATH
        # try and get extent if one is not given 
        if extent is None:
            extent = ExtentBuilder.from_vrt(vrt_path)
        
        collection = STACCollection(collection_id, description, extent)
        
        # First, add the VRT itself as an item
        vrt_item = self._process_file(vrt_path)
        # extractor = MetaDataExtractorFactory.get_metadata_extractor(vrt_path)
        # metadata = extractor.extract_metadata()
        # metadata.get("vrt_files").keys()
        collection.add_item(vrt_item)
        
        # Then process all the files referenced in the VRT
        vrt_files = self._get_vrt_files(vrt_path)
        print(f"vrt_files: {vrt_files}")
        for file_path in vrt_files:
            # if os.path.exists(file_path):  # Only process if file exists
            print(f"Processing {file_path}")
            item = self._process_file(file_path)
            collection.add_item(item)
            # else:
                # print(f"{file_path} does NOT exist")
        
        self.catalog.add_collection(collection)
        return self
    
    def build(self) -> STACCatalog:
        """Return the built catalog."""
        if not self.catalog:
            raise ValueError("Catalog must be created first")
        return self.catalog

# builder = STACBuilder()
# catalog = (builder
#     .create_catalog("my-catalog", "A test catalog", "Test Catalog")
#     .add_collection_from_files(
#         "collection-1",
#         "First collection",
#         ["/path/to/file1.tif", "/path/to/file2.tif"],
#         {"spatial": {"bbox": [[-180, -90, 180, 90]]},
#          "temporal": {"interval": [["2020-01-01T00:00:00Z", None]]}}
#     )
#     .build())
