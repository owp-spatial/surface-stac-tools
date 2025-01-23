
import pystac

from abc import ABC, abstractmethod
import typing
from typing import Dict, Any, Type

class CatalogDataLoader(ABC):

    """
    Abstract base class for loading STAC catalog json.
    """

    def __init__(self, catalog_path):
        self.catalog_path = catalog_path
    
    @abstractmethod
    def load_catalog(self) -> pystac.Catalog:
        pass

class LocalCatalogDataLoader(CatalogDataLoader):

    def load_catalog(self) -> pystac.Catalog:
        return pystac.Catalog.from_file(self.catalog_path)

class RemoteCatalogDataLoader(CatalogDataLoader):
    """
    Data loader for loading a STAC catalog from a remote URL.
    """
    def load_catalog(self) -> pystac.Catalog:
        """
        Load a STAC catalog from a remote URL.
        :return: An instance of pystac.Catalog.
        """
        # Ensure HTTP requests are allowed (e.g., using settings or additional configurations)
        if not self.catalog_path.startswith("http"):
            raise ValueError("The catalog_path must be a valid URL for a remote catalog.")

        return pystac.Catalog.from_url(self.catalog_path)

class CatalogLoaderFactory:
    """
    Factory class for creating CatalogDataLoader instances, supporting dependency injection and extensibility.
    Allows for the addition of new loader types without modifying this class.
    """
    loader_classes: Dict[str, Type[CatalogDataLoader]] = {
        'http': RemoteCatalogDataLoader,  
        'file': LocalCatalogDataLoader,
        # 's3': S3CatalogDataLoader,
    }

    @staticmethod
    def create_loader(catalog_path: str) -> CatalogDataLoader:
        """
        Create an appropriate CatalogDataLoader instance based on the catalog_path type.
        :param catalog_path: The catalog_path or URL to the catalog.
        :return: An instance of CatalogDataLoader.
        """
        for protocol, loader_class in CatalogLoaderFactory.loader_classes.items():
            if catalog_path.startswith(protocol):
                return loader_class(catalog_path)
    
        return LocalCatalogDataLoader(catalog_path)
     
        # raise ValueError(f"No suitable loader found for catalog_path: {catalog_path}")

# TODO: make this dynamically get the correct CatalogDataLoader
def get_catalog_loader(catalog_path: str) -> CatalogDataLoader:
    """
    Factory method to return the appropriate CatalogDataLoader implementation based on the catalog_path.
    :param catalog_path: The catalog_path or URL to the catalog.
    :return: An instance of CatalogDataLoader.
    """
    # if catalog_path.startswith("http"):
        # return RemoteCatalogDataLoader(catalog_path)
    # else:
    return LocalCatalogDataLoader(catalog_path)