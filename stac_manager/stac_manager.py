import os
from typing import Dict, Optional, List, Union
from pathlib import Path

import pystac
from pystac import Catalog, Collection, Item, Asset, MediaType, Extent, SpatialExtent, TemporalExtent

from stac_manager.catalog_manager import CatalogManager
from stac_manager.constants import (
    DEFAULT_ROOT_CATALOG_ID
)


# TODO: Still work in progress
# TODO: Remove does not work as expected
class STACManager:
    # Class-level defaults and counter
    _DEFAULT_ROOT_CATALOG_ID = DEFAULT_ROOT_CATALOG_ID
    _CATALOG_COUNTER = 0

    def __init__(self):
        # store multiple CatalogManager instances by catalog ID
        self.catalog_managers: Dict[str, CatalogManager] = {}

    def get_catalog(self, 
                    catalog_path: str, 
                    catalog_id: Optional[str] = None, 
                    title: Optional[str] = None, 
                    description: Optional[str] = None) -> CatalogManager:
        """
        Get an existing catalog by its ID or create a new one if it doesn't exist.

        Args:
            catalog_path (str): Path to the catalog on disk.
            catalog_id (Optional[str]): Unique identifier for the catalog. If not provided, a default ID is generated.
            title (Optional[str]): Title of the catalog.
            description (Optional[str]): Description of the catalog.

        Returns:
            CatalogManager: The existing or newly created CatalogManager instance.
        """
        # auto increment default catalog ID if none is provided
        if catalog_id is None:
            catalog_id = f"{self._DEFAULT_ROOT_CATALOG_ID}-{self._CATALOG_COUNTER}"
            self._CATALOG_COUNTER += 1

        # if catalog exists, return it
        if catalog_id in self.catalog_managers:
            return self.catalog_managers[catalog_id]

        # otherwise, create catalog and store it
        catalog_manager = CatalogManager(
            catalog_path=catalog_path,
            id=catalog_id,
            title=title,
            description=description
        )
        self.catalog_managers[catalog_id] = catalog_manager
        return catalog_manager

    def list_catalogs(self) -> List[str]:
        """
        List all catalog IDs managed by the STACManager.

        Returns:
            List[str]: A list of catalog IDs.
        """
        return list(self.catalog_managers.keys())

    # TODO: Implement remove_catalog (probably needs to remove from disk as well)
    def remove_catalog(self, catalog_id: str) -> None:
        """
        Remove a CatalogManager by its ID.

        Args:
            catalog_id (str): The ID of the catalog to remove.
        """
        if catalog_id not in self.catalog_managers:
            raise ValueError(f"Catalog with ID '{catalog_id}' does not exist.")

        catalog = self.catalog_managers[catalog_id]

        # Clear all chidren and items
        catalog.catalog.clear_items() 
        catalog.catalog.clear_children()

        # resave the removed catalog to disk
        catalog.save_catalog()

        # remove the catalog from the manager
        del self.catalog_managers[catalog_id]

    def describe_catalog(self, catalog_id: str) -> None:
        """
        Print a description of a specific catalog.

        Args:
            catalog_id (str): The ID of the catalog to describe.
        """
        catalog_manager = self.catalog_managers.get(catalog_id)
        if not catalog_manager:
            raise ValueError(f"Catalog with ID '{catalog_id}' does not exist.")
        catalog_manager.describe()

    def add_collection_to_catalog(self, 
                                   catalog_id: str, 
                                   collection_id: str, 
                                   title: str, 
                                   description: str, 
                                   extent: Extent = None) -> None:
        """
        Add a collection to a specific catalog.

        Args:
            catalog_id (str): The ID of the catalog to add the collection to.
            collection_id (str): The ID of the new collection.
            title (str): The title of the collection.
            description (str): The description of the collection.
            extent (Extent): Spatial and temporal extent of the collection.
        """
        catalog_manager = self.catalog_managers.get(catalog_id)
        if not catalog_manager:
            raise ValueError(f"Catalog with ID '{catalog_id}' does not exist.")
        catalog_manager.add_child_collection(
            collection_id=collection_id,
            title=title,
            description=description,
            extent=extent
        )

    def add_item_to_collection_in_catalog(self, 
                                          catalog_id: str, 
                                          collection_id: str, 
                                          data_path: str, 
                                          **kwargs) -> None:
        """
        Add an item to a collection within a specific catalog.

        Args:
            catalog_id (str): The ID of the catalog.
            collection_id (str): The ID of the collection.
            data_path (str): The path to the data file for the item.
            **kwargs: Additional arguments for item creation.
        """
        catalog_manager = self.catalog_managers.get(catalog_id)
        if not catalog_manager:
            raise ValueError(f"Catalog with ID '{catalog_id}' does not exist.")
        catalog_manager.add_item_to_collection(
            collection_id=collection_id,
            data_path=data_path,
            **kwargs
        )

    def remove_collection_from_catalog(self, catalog_id: str, collection_id: str) -> None:
        """
        Remove a collection from a catalog.

        Args:
            catalog_id (str): The ID of the catalog.
            collection_id (str): The ID of the collection to remove.
        """
        catalog_manager = self.catalog_managers.get(catalog_id)
        if not catalog_manager:
            raise ValueError(f"Catalog with ID '{catalog_id}' does not exist.")
        catalog_manager.remove_collection(collection_id)

    def list_catalog_collections(self, catalog_id: str) -> List[str]:
        """
        List all collections in a catalog.

        Args:
            catalog_id (str): The ID of the catalog.

        Returns:
            List[str]: A list of collection IDs.
        """
        catalog_manager = self.catalog_managers.get(catalog_id)
        if not catalog_manager:
            raise ValueError(f"Catalog with ID '{catalog_id}' does not exist.")
        return [child.id for child in catalog_manager.get_children()]

    def save_catalog(self, catalog_id: str) -> None:
        """
        Save the catalog to its file path.

        Args:
            catalog_id (str): The ID of the catalog to save.
        """
        catalog_manager = self.catalog_managers.get(catalog_id)
        if not catalog_manager:
            raise ValueError(f"Catalog with ID '{catalog_id}' does not exist.")
        catalog_manager.catalog.save(catalog_manager.catalog_path)
    
    def save_all_catalogs(self, 
                          catalog_type : pystac.CatalogType = pystac.CatalogType.SELF_CONTAINED
                          ) -> None: 
        """Save all managed catalogs."""
        for catalog_manager in self.catalog_managers.values():
            catalog_manager.save_catalog(catalog_type=catalog_type)
