# item_manager.py
import os
from pathlib import Path
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime

import pystac
from pystac import Item, Asset, MediaType
    
import config.settings as settings
from catalog_manager.catalog_extents import GenericExtent
from catalog_manager.stac_metadata import MetaDataExtractor, MetaDataExtractorFactory

class AbstractItemFactory(ABC):

    @abstractmethod
    def create_item(self, data_path : str, **kwargs) -> pystac.Item:
        """Create a STAC Item from a given data source"""
        pass

    @abstractmethod
    def create_assets(self, data_path : str) -> Dict[str, pystac.Asset]:
        """Create assets for the given STAC Item"""
        pass

class RasterItemFactory(AbstractItemFactory):
    """Concrete factory for creating STAC Items from Raster data"""

    def __init__(self, metadata_extractor: MetaDataExtractorFactory):
        self.metadata_extractor = metadata_extractor

    def create_item(self, data_path: str, **kwargs) -> pystac.Item:
        # return super().create_item(data_path, **kwargs)
        extractor = self.metadata_extractor.get_metadata_extractor(data_path)
        metadata = extractor.extract_metadata()
        
        # Create STAC Item
        item_id = kwargs.get("item_id", data_path)
        # item_id = kwargs.get('item_id', str(uuid.uuid4()))
        
        item = pystac.Item(
            id=item_id,
            geometry=metadata.get('geometry'),
            bbox=metadata.get('bbox'),
            datetime=kwargs.get('datetime', datetime.now()),
            properties=kwargs.get('properties', {})
        )

        # add aseets to items
        assets = self.create_assets(data_path)
        for asset_key, asset in assets.items():
            item.add_asset(asset_key, asset)

        return item


    def create_assets(self, data_path: str) -> Dict[str, pystac.Asset]:
        extractor = self.metadata_extractor.get_metadata_extractor(data_path)
        metadata = extractor.extract_metadata()
        
        print(f"create_assets - metadata: {metadata}")
        # Use the filename without extension as the asset key
        # if not possible, just use the data_path
        try:
            asset_key = Path(data_path).stem
        except Exception as e:
            asset_key = data_path
        
        return {
            asset_key: pystac.Asset(
                href=data_path,
                media_type=metadata.get('media_type'),
                roles=['data'],
                title=asset_key  # ooptional, human readable title
            )
        }
    
    # def create_assets(self, data_path: str) -> Dict[str, pystac.Asset]:
    #     extractor = self.metadata_extractor.get_metadata_extractor(data_path)
    #     metadata = extractor.extract_metadata()

    #     return {
    #         'data' : pystac.Asset(
    #             href=data_path,
    #             media_type=metadata.get('media_type'),
    #             roles=['data']
    #         )
    #     }
    #     # return super().create_asset(data_path)

class VRTItemFactory(AbstractItemFactory):
    """Concrete factory for creating STAC Items from VRT data"""
    
    def __init__(self, metadata_extractor: MetaDataExtractorFactory):
        self.metadata_extractor = metadata_extractor

    def create_item(self, data_path: str, **kwargs) -> pystac.Item:
        # Extract metadata using the VRT-specific extractor
        extractor = self.metadata_extractor.get_metadata_extractor(data_path)
        metadata = extractor.extract_metadata()
        # print(f"metadata: {metadata}")
        
        # Create STAC Item
        item_id = kwargs.get("item_id", data_path)
        # item_id = kwargs.get('item_id', str(uuid.uuid4()))
        
        # Create item with VRT-specific properties
        properties = kwargs.get('properties', {})
        properties.update({
            'vrt:source_count': len(metadata.get('vrt_files', [])),
            'vrt:type': 'mosaic'  # Could be parameterized based on VRT type
        })
        
        item = pystac.Item(
            id=item_id,
            geometry=metadata.get('geometry'),
            bbox=metadata.get('bbox'),
            datetime=kwargs.get('datetime', datetime.now()),
            properties=properties
        )
        
        # Add assets to item
        assets = self.create_assets(data_path)
        for asset_key, asset in assets.items():
            item.add_asset(asset_key, asset)
            
        return item

    def create_assets(self, data_path: str) -> Dict[str, pystac.Asset]:
        extractor = self.metadata_extractor.get_metadata_extractor(data_path)
        metadata = extractor.extract_metadata()
        
        assets = {}
        
        # Add the main VRT file as an asset
        assets['vrt'] = pystac.Asset(
            href=data_path,
            media_type=metadata.get('media_type'),
            roles=['data', 'vrt']
        )
        
        # Add source files as separate assets
        vrt_files = metadata.get('vrt_files', [])
        for idx, source_file in enumerate(vrt_files):
            print(f"source_file: {source_file}")
            print(f"idx: {idx}")
            media_type = MetaDataExtractor.get_media_type(source_file)
            print(f"media_type: {media_type}")
            assets[f'source_{idx}'] = Asset(
                href=source_file,
                media_type=media_type,
                roles=['source'],
                title=f'Source {idx + 1}',
                description=f'Source file {idx + 1} referenced by the VRT'
            )
        
        # print(f"assets: {assets}")
        return assets

class ItemFactoryManager:
    """
    Factory manager to create appropriate item factories based on data type.
    Similar pattern to MetaDataExtractorFactory.
    """
    _factory_mapping = {
        "tif": RasterItemFactory,
        "vrt": VRTItemFactory
    }

    def __init__(self, metadata_extractor_factory: MetaDataExtractorFactory):
        self.metadata_extractor_factory = metadata_extractor_factory

    @classmethod
    def register_factory(cls, data_type: str, factory_class: type):
        """Register a new factory class for a data type"""
        cls._factory_mapping[data_type] = factory_class

    def get_item_factory(self, data_type: str) -> AbstractItemFactory:
        """
        Get the appropriate item factory for the given data type.
        
        Args:
            data_type (str): The type of data to create items for
            
        Returns:
            AbstractItemFactory: An instance of the appropriate item factory
            
        Raises:
            ValueError: If the data type is not supported
        """
        factory_class = self._factory_mapping.get(data_type.lower())
        if not factory_class:
            raise ValueError(
                f"Unsupported data type: {data_type}. "
                f"Supported types: {list(self._factory_mapping.keys())}"
            )
        return factory_class(self.metadata_extractor_factory)

    @classmethod
    def get_supported_types(cls) -> List[str]:
        """Get list of supported data types"""
        return list(cls._factory_mapping.keys())
