import os

import pystac 
from pystac import Catalog, Collection, Extent, SpatialExtent, TemporalExtent

from stac_manager.catalog_extents import GenericExtent

# TODO: This needs to be looked at more, but i think this is the right direction 
class CollectionManager:

    def __init__(self, 
                 collection_id:str, 
                 title: str ,
                 description : str,
                 extent : Extent = None,
                 ):
        self.collection_id = collection_id if collection_id else "Default collection id"
        self.title = title if title else "Default collection title"
        self.description = description if description else "Default collection description"
        self.extent = extent if extent else GenericExtent().get_extent()
        self.collection = None
        self.create_collection()
    
    def create_collection(self) -> None:
        self.collection = pystac.Collection(
            id=self.collection_id,
            description=self.description,
            title=self.title,
            extent=self.extent
            )
        return
    
    def get_collection(self) -> pystac.Collection:
        return self.collection
    
    def get_item(self, id :str, recursive:bool = False) -> pystac.Item:
        return self.collection.get_item(id, recursive)

    def update_extent_from_items(self) -> None:
        self.collection.update_extent_from_items()
        return 
