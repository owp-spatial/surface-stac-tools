import os
from pathlib import Path
import typing
from typing import Dict, List, Optional

import pystac 
from pystac import Catalog, Collection, Item, Asset, MediaType, Extent, SpatialExtent, TemporalExtent

from stac_manager.catalog_loader import get_catalog_loader, CatalogDataLoader, CatalogLoaderFactory
from stac_manager.collection_manager import CollectionManager
from stac_manager.item_manager import AbstractItemFactory, ItemFactoryManager, RasterItemFactory, VRTItemFactory
from stac_manager.catalog_extents import GenericExtent
from stac_manager.stac_metadata import Metadata, MetaDataExtractorFactory
from stac_manager.constants import DEFAULT_ROOT_CATALOG_ID, \
        DEFAULT_ROOT_CATALOG_TITLE, \
        DEFAULT_ROOT_CATALOG_DESC

class CatalogManager:
    def __init__(self, 
                 catalog_path: str, 
                 id: Optional[str] = None,
                 title: Optional[str] = None,
                 description: Optional[str] = None,
                 catalog_loader: CatalogDataLoader = None,
                 metadata_extractor_factory: MetaDataExtractorFactory = None
                 ):
        self.catalog_path = catalog_path
        self.catalog_loader = catalog_loader or CatalogLoaderFactory.create_loader(self.catalog_path)
        # self.catalog_loader = catalog_loader
        self.catalog = None
        
        # Initialize factories
        self.metadata_extractor_factory = metadata_extractor_factory or MetaDataExtractorFactory()
        self.item_factory_manager = ItemFactoryManager(self.metadata_extractor_factory)
        
        self._load_or_create_catalog()

        # set any metadata if provided
        # self._set_catalog_metadata(id, title, description)
        self.set_catalog_id(id)
        self.set_catalog_title(title)
        self.set_catalog_description(description)

    def _load_or_create_catalog(self) -> None:
        try:
            self.catalog = self.catalog_loader.load_catalog()
        except:
            self.catalog = self._create_root_catalog()
        return 
                    
    def _create_root_catalog(self) -> pystac.Catalog:
        root_catalog = pystac.Catalog(
            id=DEFAULT_ROOT_CATALOG_ID, 
            description=DEFAULT_ROOT_CATALOG_DESC,
            # href=self.catalog_path,
            catalog_type=pystac.CatalogType.SELF_CONTAINED
        )
        return root_catalog
    
    def get_catalog(self) -> pystac.Catalog:
        return self.catalog

    def set_catalog_id(self, id: str) -> None:
        if self.catalog and id:
            self.catalog.id = id
        return 
    
    def set_catalog_title(self, title: str) -> None:
        if self.catalog and title:
            self.catalog.title = title
        return
    
    def set_catalog_description(self, description: str) -> None:
        if self.catalog and description:
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
            
            # Find the collection and add the item
            collection = self.get_collection_by_id(collection_id)

            if not collection:
                raise ValueError(f"Collection not found: {collection_id}")

            # set collection id for the item
            item.collection = collection.id 

            # Add item to collection and update extent basd on items
            collection.add_item(item)
            collection.update_extent_from_items()

            # return item
            return 
            
        except ValueError as e:
            raise ValueError(f"Error creating item: {str(e)}")

    def remove_collection(self, collection_id: str) -> None:
        """Remove a collection from the catalog by ID"""
        collection = self.get_collection_by_id(collection_id)
        if collection:
            self.catalog.remove_child(collection_id)
        else:
            raise ValueError(f"Collection not found: {collection_id}")
        return

    def remove_item_from_collection(self, collection_id: str, item_id: str) -> None:
        """Remove an item from a collection by ID"""
        collection = self.get_collection_by_id(collection_id)
        if not collection:
            raise ValueError(f"Collection not found: {collection_id}")
        
        item = collection.get_item(item_id)
        if item:
            collection.remove_item(item_id)
            # Update collection extent after removing item
            collection.update_extent_from_items()
        else:
            raise ValueError(f"Item not found: {item_id} in collection {collection_id}")
        return

    def update_item_properties(self, 
                             collection_id: str, 
                             item_id: str, 
                             properties: Dict) -> None:
        """
        Update properties of a specific item in a collection
        
        Args:
            collection_id (str): ID of the collection containing the item
            item_id (str): ID of the item to update
            properties (Dict): Dictionary of properties to update/add
        """
        collection = self.get_collection_by_id(collection_id)
        if not collection:
            raise ValueError(f"Collection not found: {collection_id}")
        
        item = collection.get_item(item_id)
        if not item:
            raise ValueError(f"Item not found: {item_id}")
        
        # Update existing properties and add new ones
        for key, value in properties.items():
            item.properties[key] = value
        
        return
    
    def remove_item_properties(self,
                             collection_id: str,
                             item_id: str,
                             property_keys: List[str]) -> None:
        """
        Remove specified properties from an item
        
        Args:
            collection_id (str): ID of the collection containing the item
            item_id (str): ID of the item to update
            property_keys (List[str]): List of property keys to remove
        """
        collection = self.get_collection_by_id(collection_id)
        if not collection:
            raise ValueError(f"Collection not found: {collection_id}")
        
        item = collection.get_item(item_id)
        if not item:
            raise ValueError(f"Item not found: {item_id}")
        
        for key in property_keys:
            if key in item.properties:
                del item.properties[key]
        
        return

    def update_collection_items_properties(self,
                                         collection_id: str,
                                         properties: Dict,
                                         filter_fn: Optional[typing.Callable] = None) -> None:
        """
        Update properties for all items in a collection, optionally filtered
        
        Args:
            collection_id (str): ID of the collection
            properties (Dict): Dictionary of properties to update/add
            filter_fn (Callable): Optional function that takes an item and returns
                                bool indicating if the item should be updated
        """
        collection = self.get_collection_by_id(collection_id)
        if not collection:
            raise ValueError(f"Collection not found: {collection_id}")
        
        for item in collection.get_items():
            if filter_fn is None or filter_fn(item):
                for key, value in properties.items():
                    item.properties[key] = value
        
        return

    def remove_collection_items_properties(self,
                                         collection_id: str,
                                         property_keys: List[str],
                                         filter_fn: Optional[typing.Callable] = None) -> None:
        """
        Remove specified properties from all items in a collection, optionally filtered
        
        Args:
            collection_id (str): ID of the collection
            property_keys (List[str]): List of property keys to remove
            filter_fn (Callable): Optional function that takes an item and returns
                                bool indicating if the item should be updated
        """
        collection = self.get_collection_by_id(collection_id)
        if not collection:
            raise ValueError(f"Collection not found: {collection_id}")
        
        for item in collection.get_items():
            if filter_fn is None or filter_fn(item):
                for key in property_keys:
                    if key in item.properties:
                        del item.properties[key]
        
        return

    def get_item_by_id(self, collection_id: str, item_id: str) -> Optional[pystac.Item]:
        """Get a specific item from a collection by ID"""
        collection = self.get_collection_by_id(collection_id)
        if collection:
            return collection.get_item(item_id)
        return None

    # def get_collection_by_id(self, collection_id: str) -> Optional[pystac.Collection]:
    #     """Get a collection by ID"""
    #     return self.get_collection_by_id(collection_id)

    def list_collection_items(self, collection_id: str) -> List[pystac.Item]:
        """Get all items in a collection"""
        collection = self.get_collection_by_id(collection_id)
        if collection:
            return list(collection.get_items())
        raise ValueError(f"Collection not found: {collection_id}") 
    
    def get_supported_data_types(self) -> List[str]:
        """Get list of supported data types"""
        return self.item_factory_manager.get_supported_types()

    def _update_all_collection_extents(self) -> None:
        """Update the spatial and temporal extents of all collections"""
        for child in self.catalog.get_children():
            if isinstance(child, pystac.Collection):
                child.update_extent_from_items()
        return

    def get_collection_by_id(self, collection_id: str) -> Optional[pystac.Collection]:
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

    def save_catalog(self, catalog_type : pystac.CatalogType = pystac.CatalogType.SELF_CONTAINED) -> None:
        """Save the catalog to disk"""
        if not isinstance(catalog_type, pystac.CatalogType):
            raise ValueError(f"Invalid catalog type: {catalog_type}, expected pystac.CatalogType")

        self._update_all_collection_extents()

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
#         collection = self.get_collection_by_id(collection_id)
#         if collection is None:
#             raise ValueError(f"Collection not found: {collection_id}")

#         collection.add_item(item)
#         return item

#     def get_collection_by_id(self, collection_id: str) -> Optional[pystac.Collection]:
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
