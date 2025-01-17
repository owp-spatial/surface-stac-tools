import os
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime

import pystac
from pystac import Item, Asset, MediaType
    
import config.settings as settings
from catalog_manager.catalog_extents import GenericExtent
from catalog_manager.stac_metadata import MetaDataExtractorFactory

class AbstractItemFactory(ABC):

    @abstractmethod
    def create_item(self, path : str, **kwargs) -> pystac.Item:
        """Create a STAC Item from a given data source"""
        pass

    @abstractmethod
    def create_assets(self, path : str) -> Dict[str, pystac.Asset]:
        """Create assets for the given STAC Item"""
        pass

class RasterItemFactory(AbstractItemFactory):
    """Concrete factory for creating STAC Items from Raster data"""

    def __init__(self, metadata_extractor: MetaDataExtractorFactory):
        self.metadata_extractor = metadata_extractor

    def create_item(self, path: str, **kwargs) -> pystac.Item:
        # return super().create_item(path, **kwargs)
        extractor = self.metadata_extractor.get_metadata_extractor(path)
        metadata = extractor.extract_metadata()
    
        # Create STAC Item
        item_id = kwargs.get("item_id", path)
        # item_id = kwargs.get('item_id', str(uuid.uuid4()))
        
        item = Item(
            id=item_id,
            geometry=metadata.get('geometry'),
            bbox=metadata.get('bbox'),
            datetime=kwargs.get('datetime', datetime.now()),
            properties=kwargs.get('properties', {})
        )

        # add aseets to items
        assets = self.create_assets(path)
        for asset_key, asset in asse


    def create_assets(self, path: str) -> Dict[str, pystac.Asset]:
        extractor = self.metadata_extractor.get_metadata_extractor(path)
        metadata = extractor.extract_metadata()

        return {
            'data' : pystac.Asset(
                href=path,
                media_type=metadata.get('media_type'),
                roles=['data']
            )
        }
        # return super().create_asset(path)