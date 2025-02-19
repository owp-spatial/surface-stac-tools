from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Dict, List, Optional, Union
import pystac
from pystac import Catalog, Collection, Item, Asset, MediaType, Extent, SpatialExtent, TemporalExtent

class GenericExtent:

    def __init__(self, bbox = None, temporal_interval = None):
        self.bbox = bbox
        self.temporal_interval = temporal_interval
    
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
