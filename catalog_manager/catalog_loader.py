
import pystac

from abc import ABC, abstractmethod
import typing
from typing import Dict, Any, Type

import config.settings as settings

class CatalogDataLoader(ABC):

    """
    Abstract base class for loading STAC catalog json.
    """

    def __init__(self, path):
        self.path = path
    
    @abstractmethod
    def load_catalog(self) -> pystac.Catalog:
        pass

class LocalCatalogDataLoader(CatalogDataLoader):

    def load_catalog(self) -> pystac.Catalog:
        return pystac.Catalog.from_file(self.path)

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
        if not self.path.startswith("http"):
            raise ValueError("The path must be a valid URL for a remote catalog.")

        return pystac.Catalog.from_url(self.path)

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
    def create_loader(path: str) -> CatalogDataLoader:
        """
        Create an appropriate CatalogDataLoader instance based on the path type.
        :param path: The path or URL to the catalog.
        :return: An instance of CatalogDataLoader.
        """
        for protocol, loader_class in CatalogLoaderFactory.loader_classes.items():
            if path.startswith(protocol):
                return loader_class(path)
        
        raise ValueError(f"No suitable loader found for path: {path}")

# TODO: make this dynamically get the correct CatalogDataLoader
def get_catalog_loader(path: str) -> CatalogDataLoader:
    """
    Factory method to return the appropriate CatalogDataLoader implementation based on the path.
    :param path: The path or URL to the catalog.
    :return: An instance of CatalogDataLoader.
    """
    # if path.startswith("http"):
        # return RemoteCatalogDataLoader(path)
    # else:
    return LocalCatalogDataLoader(path)