import os
from pathlib import Path
import typing
from typing import Dict, List, Optional

import pystac 
from pystac import Catalog, Collection, Item, Asset, MediaType, Extent, SpatialExtent, TemporalExtent

from catalog_manager.catalog_loader import get_catalog_loader, CatalogDataLoader
from catalog_manager.collection_manager import CollectionManager
from catalog_manager.item_manager import AbstractItemFactory, ItemFactoryManager, RasterItemFactory, VRTItemFactory
from catalog_manager.catalog_extents import GenericExtent
from catalog_manager.stac_metadata import Metadata, MetaDataExtractorFactory

import config.settings as settings

class CatalogManager:
    def __init__(self, 
                 catalog_path: str, 
                 catalog_loader: CatalogDataLoader,
                 metadata_extractor_factory: MetaDataExtractorFactory = None
                 ):
        self.catalog_path = catalog_path
        self.catalog_loader = catalog_loader
        self.catalog = None
        
        # Initialize factories
        self.metadata_extractor_factory = metadata_extractor_factory or MetaDataExtractorFactory()
        self.item_factory_manager = ItemFactoryManager(self.metadata_extractor_factory)
        
        self._load_or_create_catalog()

    def _load_or_create_catalog(self) -> None:
        try:
            self.catalog = self.catalog_loader.load_catalog()
        except:
            self.catalog = self._create_root_catalog()
        return 
                    
    def _create_root_catalog(self) -> pystac.Catalog:
        root_catalog_id   = "root-catalog"
        root_catalog_desc = "STAC Root Catalog description" 
        root_catalog = pystac.Catalog(
            id=root_catalog_id, 
            description=root_catalog_desc,
            # href=self.catalog_path,
            catalog_type=pystac.CatalogType.SELF_CONTAINED
        )
        return root_catalog
    
    def get_catalog(self) -> pystac.Catalog:
        return self.catalog
    
    def set_catalog_title(self, title: str) -> None:
        self.catalog.title = title
        return
    
    def set_catalog_description(self, description: str) -> None:
        self.catalog.description = description
        return

    def describe(self) -> None:
        self.catalog.describe()
        return 
    

    def get_children(self):
        return self.catalog.get_children()
    
    def get_items(self):
        return self.catalog.get_items()
    
    def add_child_collection(self, 
                           collection_id: str, 
                           title: str,
                           description: str,
                           extent: Extent = None
                           ) -> None:
        collection = CollectionManager(
            collection_id=collection_id,
            title=title,
            description=description,
            extent=extent
        )

        # check if collection is already present
        if not self._collection_exists(collection_id): 
            self.catalog.add_child(collection.get_collection())

        return 

    def add_item_to_collection(self, 
                   collection_id: str,
                   data_path: str,
                   **kwargs) -> None:
        """
        Create a STAC Item and add it to the specified collection.
        Data type is inferred from the file extension.
        
        Args:
            collection_id (str): ID of the collection to add the item to
            data_path (str): Path to the data file
            **kwargs: Additional arguments to pass to the item factory
            
        Returns:
            None
        """
        # Infer data type from file extension
        data_type = Path(data_path).suffix.lower().lstrip('.')
        
        try:
            # Get the appropriate factory
            factory = self.item_factory_manager.get_item_factory(data_type)
            
            # Create the item
            item = factory.create_item(data_path, **kwargs)
            
            print(f"Item created: {item}")
            # Find the collection and add the item
            collection = self._find_collection(collection_id)
            print(f"Collection found: {collection}")
            print(f"Type of collection: {type(collection)}")

            if not collection:
                raise ValueError(f"Collection not found: {collection_id}")

            item.collection = collection.id 
            # Add item to collection and update extent basd on items
            collection.add_item(item)
            collection.update_extent_from_items()

            # return item
            return 
            
        except ValueError as e:
            raise ValueError(f"Error creating item: {str(e)}")

    def update_all_collection_extents(self) -> None:
        """Update the spatial and temporal extents of all collections"""
        for child in self.catalog.get_children():
            if isinstance(child, pystac.Collection):
                child.update_extent_from_items()
        return

    def _find_collection(self, collection_id: str) -> Optional[pystac.Collection]:
        """Find a collection in the catalog by ID"""
        for child in self.catalog.get_children():
            if isinstance(child, pystac.Collection) and child.id == collection_id:
                return child
        return None

    def _collection_exists(self, collection_id: str) -> bool:
        """Check if a collection exists in the catalog"""
        for child in self.catalog.get_children():
            if isinstance(child, pystac.Collection) and child.id == collection_id:
                return True
        return False

    def get_supported_data_types(self) -> List[str]:
        """Get list of supported data types"""
        return self.item_factory_manager.get_supported_types()

    def save_catalog(self, catalog_type : pystac.CatalogType = pystac.CatalogType.SELF_CONTAINED) -> None:
        """Save the catalog to disk"""
        if not isinstance(catalog_type, pystac.CatalogType):
            raise ValueError(f"Invalid catalog type: {catalog_type}, expected pystac.CatalogType")

        self.update_all_collection_extents()

        self.catalog.normalize_hrefs(self.catalog_path)
        self.catalog.save(catalog_type=catalog_type)
        return

def setup_catalog_manager(catalog_path: str, catalog_loader: CatalogDataLoader):
    """Setup a catalog manager with default configurations"""
    metadata_extractor_factory = MetaDataExtractorFactory()
    
    catalog_manager = CatalogManager(
        catalog_path=catalog_path,
        catalog_loader=catalog_loader,
        metadata_extractor_factory=metadata_extractor_factory
    )
    
    return catalog_manager

# class CatalogManager:

#     def __init__(self, 
#                  catalog_path :str, 
#                  catalog_loader : CatalogDataLoader,
#                  metadata_extractor_factory: MetaDataExtractorFactory = None
#                  ):
#         self.catalog_path = catalog_path
#         self.catalog_loader = catalog_loader
#         self.catalog = None
        
#         # initialize factories
#         self.metadata_extractor_factory = metadata_extractor_factory or MetaDataExtractorFactory()
#         self._item_factories = self._init_item_factories()
        
#         # Load or create catalog
#         self._load_or_create_catalog()

#     def _init_item_factories(self) -> Dict[str, AbstractItemFactory]:
#         """Initialize the item factories for different data types"""
#         return {
#             'raster': RasterItemFactory(self.metadata_extractor_factory),
#             'vrt': VRTItemFactory(self.metadata_extractor_factory)
#         }
    
#     # Initializes catalog (Loads or creates catalog)
#     def _load_or_create_catalog(self) -> None:

#         try:
#             self.catalog = self.catalog_loader.load_catalog()
#         except:
#             self.catalog = self._create_root_catalog()
        
#         return 
                    
#     def _create_root_catalog(self) -> pystac.Catalog:
#         root_catalog_id   = "root-catalog"
#         root_catalog_desc = "STAC Root Catalog description" 
#         root_catalog      = pystac.Catalog(
#             id=root_catalog_id, 
#             description=root_catalog_desc,
#             href=self.catalog_path
#             )
#         return root_catalog
    
#     def get_catalog(self) -> pystac.Catalog:
#         return self.catalog
    
#     def add_child_collection(self, 
#                             collection_id:str, 
#                             title: str ,
#                             description : str,
#                             extent : Extent = None
#                             ) -> None:
#         collection = CollectionManager(
#             collection_id=collection_id,
#             title=title,
#             description=description,
#             extent=extent
#             )
#         self.catalog.add_child(collection.get_collection())
#         return 
    
#     def create_item(self, 
#                     collection_id: str,
#                     data_type: str,
#                     data_path: str,
#                     **kwargs) -> pystac.Item:
#         """
#         Create a new STAC Item and add it to the specified collection
        
#         Args:
#             collection_id (str): ID of the collection to add the item to
#             data_type (str): Type of data ('raster', 'vrt', etc.)
#             data_path (str): Path to the data file
#             **kwargs: Additional arguments to pass to the item factory
        
#         Returns:
#             pystac.Item: The created STAC Item
#         """

#         # validate data type
#         if data_type not in self._item_factories:
#             raise ValueError(f"Unsupported data type: {data_type}. Supported types: {list(self._item_factories.keys())}")

#         # Get the appropriate factory
#         factory = self._item_factories[data_type]

#         # Create the item
#         item = factory.create_item(data_path, **kwargs)

#         # Find the collection and add the item
#         collection = self._find_collection(collection_id)
#         if collection is None:
#             raise ValueError(f"Collection not found: {collection_id}")

#         collection.add_item(item)
#         return item

#     def _find_collection(self, collection_id: str) -> Optional[pystac.Collection]:
#         """Find a collection in the catalog by ID"""
#         # Search through all children of the catalog
#         for child in self.catalog.get_children():
#             if isinstance(child, pystac.Collection) and child.id == collection_id:
#                 return child
#         return None

#     def register_item_factory(self, data_type: str, factory: AbstractItemFactory) -> None:
#         """
#         Register a new item factory for a specific data type
        
#         Args:
#             data_type (str): The type of data this factory handles
#             factory (AbstractItemFactory): The factory instance
#         """
#         self._item_factories[data_type] = factory

#     def get_supported_data_types(self) -> List[str]:
#         """Get a list of supported data types"""
#         return list(self._item_factories.keys())
