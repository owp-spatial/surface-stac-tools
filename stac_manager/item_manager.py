# item_manager.py
import os
from os.path import basename, join
from pathlib import Path
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime

import pystac
from pystac import Item, Asset, MediaType
    
import config.settings as settings
from stac_manager.catalog_extents import GenericExtent
from stac_manager.stac_metadata import MetaDataExtractor, MetaDataExtractorFactory

class AbstractItemFactory(ABC):

    @abstractmethod
    def create_item(self, data_path : str, **kwargs) -> pystac.Item:
        """Create a STAC Item from a given data source"""
        pass

    @abstractmethod
    def create_assets(self, data_path : str) -> Dict[str, pystac.Asset]:
        """Create assets for the given STAC Item"""
        pass

    @classmethod
    def _get_file_name(cls, data_path: str) -> str:
        # return Path(data_path).stem
        return basename(data_path).split(".")[0]

class RasterItemFactory(AbstractItemFactory):
    """Concrete factory for creating STAC Items from Raster data"""

    def __init__(self, metadata_extractor: MetaDataExtractorFactory):
        self.metadata_extractor = metadata_extractor

    def create_item(self, data_path: str, **kwargs) -> pystac.Item:
        extractor = self.metadata_extractor.get_metadata_extractor(data_path)
        metadata = extractor.extract_metadata()
        
        # Create STAC Item
        item_id = kwargs.get("item_id", self._get_file_name(data_path))
        # item_id = kwargs.get('item_id', str(uuid.uuid4()))
        
        item = pystac.Item(
            id=item_id,
            geometry=metadata.get('geometry'),
            bbox=metadata.get('bbox'),
            stac_extensions=metadata.get('stac_extensions', []),
            datetime=kwargs.get('datetime', datetime.now()),
            properties={**kwargs.get('properties', {}), **metadata.get('properties', {})}
            # properties=metadata.get('properties', {})
            # properties=kwargs.get('properties', {})
        )

        # add aseets to items
        assets = self.create_assets(data_path)
        for asset_key, asset in assets.items():
            item.add_asset(asset_key, asset)

        return item


    def create_assets(self, data_path: str) -> Dict[str, pystac.Asset]:
        extractor = self.metadata_extractor.get_metadata_extractor(data_path)
        metadata = extractor.extract_metadata()
        
        # Use the filename without extension as the asset key
        # if not possible, just use the data_path
        try:
            asset_key = self._get_file_name(data_path)
            # asset_key = Path(data_path).stem
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
        item_id = kwargs.get("item_id", self._get_file_name(data_path))
        # item_id = kwargs.get('item_id', str(uuid.uuid4()))
        
        # Create item with VRT-specific properties
        properties = metadata.get('properties', {})
        properties.update({
            'vrt:source_count': len(metadata.get('vrt_files', [])),
            'vrt:type': 'mosaic'  # Could be parameterized based on VRT type
        })
        item = pystac.Item(
            id=item_id,
            geometry=metadata.get('geometry'),
            bbox=metadata.get('bbox'),
            stac_extensions=metadata.get('stac_extensions', []),
            datetime=kwargs.get('datetime', datetime.now()),
            properties={**kwargs.get('properties', {}), **properties} 
            # properties=properties
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
            media_type = MetaDataExtractor.get_media_type(source_file)
            
            try:
                asset_key = self._get_file_name(source_file)
                # asset_key = f'source_{idx}'
            except Exception as e:
                asset_key = source_file

            assets[asset_key] = Asset(
                href=source_file,
                media_type=media_type,
                roles=['source'],
                title=f'Source {asset_key}',
                description=f'Source file {asset_key} referenced by the VRT'
                # title=f'Source {idx + 1}',
                # description=f'Source file {idx + 1} referenced by the VRT'
            )
        
        return assets

class ItemFactoryManager:
    """
    Factory manager to create appropriate item factories based on data type.
    Similar pattern to MetaDataExtractorFactory.
    """
    _factory_mapping = {
        "tif": RasterItemFactory,
        "tiff": RasterItemFactory,
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
