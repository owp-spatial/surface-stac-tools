from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Dict, List, Optional, Union
import pystac
from pystac import Catalog, Collection, Item, Asset, MediaType, Extent, SpatialExtent, TemporalExtent

def get_current_temporal_interval() -> list[datetime, datetime]:
    """
    Update the temporal interval with a new datetime value.
    Ensures datetime is timezone-aware.
    """
    datetime_value = datetime.now(timezone.utc)

    # Make datetime timezone-aware if it isn't already
    if datetime_value.tzinfo is None:
        datetime_value = datetime_value.replace(tzinfo=timezone.utc)
        
    temporal_interval = None

    if temporal_interval is None:
        temporal_interval = [datetime_value, datetime_value]
    else:
        temporal_interval = [
            min(temporal_interval[0], datetime_value),
            max(temporal_interval[1], datetime_value)
        ]
    return temporal_interval

class GenericExtent:

    def __init__(self, bbox = None, temporal_interval = None):
        self.bbox = bbox
        self.temporal_interval = temporal_interval
    
    # def get_current_temporal_interval(self) -> list[datetime, datetime]:
    #     """
    #     Update the temporal interval with a new datetime value.
    #     Ensures datetime is timezone-aware.
    #     """
    #     datetime_value = datetime.now(timezone.utc)
    #     # Make datetime timezone-aware if it isn't already
    #     if datetime_value.tzinfo is None:
    #         datetime_value = datetime_value.replace(tzinfo=timezone.utc)
    #     if self.temporal_interval is None:
    #         self.temporal_interval = [datetime_value, datetime_value]
    #     # else:
    #         # self.temporal_interval = [
    #             # min(self.temporal_interval[0], datetime_value),
    #             # max(self.temporal_interval[1], datetime_value)
    #         # ]
    #     return self.temporal_interval

    def get_extent(self) -> Extent:
        """
        Build a PySTAC Extent object.
        
        If bbox is None, uses global extent [-180, -90, 180, 90].
        If temporal_interval is None, uses [current_time, current_time].
        
        Returns:
            pystac.Extent object containing spatial and temporal extent information
        """

        # Default to global extent if no bbox is available
        if self.bbox is None:
            self.bbox = [-180.0, -90.0, 180.0, 90.0]
        
        # Default to current time for both start and end if no temporal interval
        if self.temporal_interval is None:
            current_time = datetime.now(timezone.utc)
            self.temporal_interval = [current_time, current_time]
            
        # Create and return a proper PySTAC Extent object
        return Extent(
            spatial=SpatialExtent(
                bboxes=[self.bbox]
            ),
            temporal=TemporalExtent(
                intervals=[[
                    self.temporal_interval[0],  
                    self.temporal_interval[1]
                ]]
            )
        )

# import os

# from stac_builder.stac_metadata import MetaDataExtractorFactory
# import os
# from abc import ABC, abstractmethod
# import json
# import urllib.request
# from datetime import datetime, timezone
# from dataclasses import dataclass
# from typing import List, Optional, Dict, Any

# import rasterio
# import pystac
# from pystac import MediaType
# from pathlib import Path
# import uuid

# from shapely.geometry import Polygon, mapping
# from stac_builder.constants import BASE_DIR, DEM_PATH, CATALOG_DIR, FILE_EXT_TO_MEDIA_TYPE

# class ExtentBuilder:
#     """
#     Helper class to build STAC extent dictionaries from geospatial files.
#     """
#     def __init__(self):
#         self.bbox = None
#         self.temporal_interval = None
        
#     def update_bbox(self, new_bbox: List[float]) -> None:
#         """
#         Update the current bbox with a new bbox, expanding if necessary.
#         """
#         if self.bbox is None:
#             self.bbox = new_bbox
#         else:
#             self.bbox = [
#                 min(self.bbox[0], new_bbox[0]),  # min x
#                 min(self.bbox[1], new_bbox[1]),  # min y
#                 max(self.bbox[2], new_bbox[2]),  # max x
#                 max(self.bbox[3], new_bbox[3])   # max y
#             ]
    
#     def update_temporal_interval(self, datetime_value: datetime) -> None:
#         """
#         Update the temporal interval with a new datetime value.
#         Ensures datetime is timezone-aware.
#         """
#         # Make datetime timezone-aware if it isn't already
#         if datetime_value.tzinfo is None:
#             datetime_value = datetime_value.replace(tzinfo=timezone.utc)
            
#         if self.temporal_interval is None:
#             self.temporal_interval = [datetime_value, datetime_value]
#         else:
#             self.temporal_interval = [
#                 min(self.temporal_interval[0], datetime_value),
#                 max(self.temporal_interval[1], datetime_value)
#             ]

#     @classmethod
#     def from_files(cls, file_paths: List[str]) -> Dict:
#         """
#         Create an extent dictionary from a list of files.
        
#         Args:
#             file_paths: List of paths to geospatial files
            
#         Returns:
#             Dict containing STAC-compliant extent information
#         """
#         builder = cls()
        
#         for file_path in file_paths:
#             extractor = MetaDataExtractorFactory.get_metadata_extractor(file_path)
#             metadata = extractor.extract_metadata()
            
#             # Update spatial extent
#             if metadata.get('bbox'):
#                 builder.update_bbox(metadata.get('bbox'))
            
#             # Update temporal extent if available
#             # Note: You might want to extract this from file metadata
#             # For now, using current time as an example
#             builder.update_temporal_interval(datetime.utcnow())
        
#         return builder.build()

#     @classmethod
#     def from_file(cls, file_path: str) -> Dict:
#         """
#         Create an extent dictionary from a file path.
        
#         Args:
#             file_path: str path to geospatial files
            
#         Returns:
#             Dict containing STAC-compliant extent information
#         """
#         builder = cls()
        
#         extractor = MetaDataExtractorFactory.get_metadata_extractor(file_path)
#         metadata = extractor.extract_metadata()
        
#         # Update spatial extent
#         if metadata.get('bbox'):
#             builder.update_bbox(metadata.get('bbox'))
        
#         # Update temporal extent if available
#         # Note: You might want to extract this from file metadata
#         # For now, using current time as an example
#         builder.update_temporal_interval(datetime.utcnow())
        
#         return builder.build()

#     @classmethod
#     def from_vrt(cls, vrt_path: str) -> Dict:
#         """
#         Create an extent dictionary from a VRT file and its sources.
        
#         Args:
#             vrt_path: Path to VRT file
            
#         Returns:
#             Dict containing STAC-compliant extent information
#         """
#         builder = cls()
        
#         # First process the VRT file itself
#         extractor = MetaDataExtractorFactory.get_metadata_extractor(vrt_path)
#         metadata = extractor.extract_metadata()
        
#         if metadata.get('bbox'):
#             builder.update_bbox(metadata.get('bbox'))
        
#         # Process all files referenced in the VRT
#         # print(f"metadata: {metadata}")

#         # vrt_files = metadata.get('vrt_files', {})
#         vrt_files = metadata.get('vrt_files', {}).get("files", [])
#         for file_path in vrt_files:
#             if os.path.exists(file_path):
#                 file_extractor = MetaDataExtractorFactory.get_metadata_extractor(file_path)
#                 file_metadata = file_extractor.extract_metadata()
                
#                 if file_metadata.get('bbox'):
#                     builder.update_bbox(file_metadata.get('bbox'))
                
#                 # Update temporal extent if available
#                 builder.update_temporal_interval(datetime.utcnow())
        
#         return builder.build()

#     def build(self) -> Extent:
#         """
#         Build a PySTAC Extent object.
        
#         If bbox is None, uses global extent [-180, -90, 180, 90].
#         If temporal_interval is None, uses [current_time, current_time].
        
#         Returns:
#             pystac.Extent object containing spatial and temporal extent information
#         """
#         # Default to global extent if no bbox is available
#         if self.bbox is None:
#             self.bbox = [-180.0, -90.0, 180.0, 90.0]
        
#         # Default to current time for both start and end if no temporal interval
#         if self.temporal_interval is None:
#             current_time = datetime.now(timezone.utc)
#             self.temporal_interval = [current_time, current_time]
            
#         # Create and return a proper PySTAC Extent object
#         return Extent(
#             spatial=SpatialExtent(
#                 bboxes=[self.bbox]
#             ),
#             temporal=TemporalExtent(
#                 intervals=[[
#                     self.temporal_interval[0],  # Pass datetime objects directly
#                     self.temporal_interval[1]   # Pass datetime objects directly
#                 ]]
#             )
#         )
