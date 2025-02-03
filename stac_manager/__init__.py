# __init__.py
version = "0.0.2"

from .catalog_manager import CatalogManager
from .stac_manager import STACManager

__all__ = [
    'CatalogManager', 
    'STACManager'
    ]
