import os
from pathlib import Path
import uuid
from abc import ABC, abstractmethod
import json
import urllib.request
from datetime import datetime, timezone
from dataclasses import dataclass
from typing import List, Optional, Dict, Any, Tuple, Union
from enum import Enum
import warnings 


from shapely.geometry import Polygon, mapping
import rasterio
from rasterio.crs import CRS
from rasterio.transform import from_bounds
import rasterio
import xarray as xr 
import numpy as np
import rio_stac

import pystac
from pystac import MediaType

from stac_manager.constants import FILE_EXT_TO_MEDIA_TYPE

class Metadata:
    """
    Class to hold metadata attributes in a flexible manner.
    Attributes are stored as key-value pairs in a dictionary.
    """

    def __init__(self, **kwargs):
        """
        Initialize Metadata with dynamic attributes.
        The kwargs allow passing arbitrary attributes.
        """
        self.metadata = kwargs

    def get(self, key, default = None) -> Any:
        """
        Get the value of a specific metadata attribute.
        """
        return self.metadata.get(key, default)

    def set(self, key, value) -> None:
        """
        Set the value of a specific metadata attribute.
        """
        self.metadata[key] = value

    def __repr__(self):
        return f"Metadata({self.metadata})"

# Abstract Base Class for Metadata Extractors
class MetaDataExtractor(ABC):
    """
    Abstract base class for metadata extraction.
    """

    def __init__(self, file_path: str):
        self.file_path = file_path

    @abstractmethod
    def extract_metadata(self):
        """
        Abstract method to extract metadata from the file.
        """
        pass

    @classmethod
    def get_media_type(cls, file_path: str) -> MediaType:
        """
        Infers the pystac.MediaType enum based on the file extension.

        Args:
            file_path (str): The path or name of the file.

        Returns:
            MediaType: The inferred MediaType enum value, or None if not matched.
        """
        # Get the file extension
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()

        # Return the corresponding MediaType enum or None if not found
        return FILE_EXT_TO_MEDIA_TYPE.get(ext)
    
    @classmethod
    def get_proj_ext_properties(self, src) -> dict:
        """Update the properties dictionary with the metadata from the dataset."""
        try:
            proj_ext_props = {
                f"proj:{name}": value
                for name, value in rio_stac.stac.get_projection_info(src).items()
                }
            return proj_ext_props
        except:
            return {}

        # return {
        #             f"proj:{name}": value
        #             for name, value in rio_stac.stac.get_projection_info(src).items()
        #             }

    @classmethod
    def get_proj_ext_path(self) -> str:
        """Return the path to the projection extension schema."""
        return f"https://stac-extensions.github.io/projection/{rio_stac.stac.PROJECTION_EXT_VERSION}/schema.json"

# Concrete Class for TIF Files
class TIFMetaData(MetaDataExtractor):
    """
    Metadata extraction for TIF files using rasterio.
    """

    def extract_metadata(self):
        """
        Extract metadata from a VRT file.
        Returns: (bbox, mapping(footprint), vrt_files)
        """
        properties = {} 
        stac_extensions = []

        # Assuming you have a way to open and read VRT metadata, e.g., using rasterio
        with rasterio.open(self.file_path) as src:
            
            bbox = self.get_bbox(src)
            footprint = self.get_footprint(src)
            media_type = self.get_media_type(self.file_path)

            # Add projection extension properties            
            proj_ext_props = self.get_proj_ext_properties(src)
            properties.update(proj_ext_props)

            # add the projection extension schema path
            stac_extensions.append(self.get_proj_ext_path())

            # return bbox, footprint
            # Return metadata in a flexible Metadata object
            metadata = Metadata(bbox=bbox, 
                                geometry=footprint, 
                                media_type=media_type, 
                                properties=properties, 
                                stac_extensions=stac_extensions
                                )
            return metadata

    def get_bbox(self, src : rasterio.DatasetReader) -> List[float]:
        bbox = [src.bounds.left, src.bounds.bottom, src.bounds.right, src.bounds.top]
        return bbox 
        
    def get_footprint(self, src : rasterio.DatasetReader) -> Dict[str, Any]:
        """
        Helper method to compute the footprint of the VRT file.
        """
        
        bounds = src.bounds
        footprint = Polygon([
            [bounds.left, bounds.bottom],
            [bounds.left, bounds.top],
            [bounds.right, bounds.top],
            [bounds.right, bounds.bottom]
        ])

        return mapping(footprint)

# Concrete Class for VRT Files
class VRTMetaData(MetaDataExtractor):
    """
    Metadata extraction for TIF files using rasterio.
    """

    def extract_metadata(self):
        """
        Extract metadata from a VRT file.
        Returns: (bbox, mapping(footprint), vrt_files)
        """
        properties = {} 
        stac_extensions = []

        # Assuming you have a way to open and read VRT metadata, e.g., using rasterio
        with rasterio.open(self.file_path) as src:
            
            bbox = self.get_bbox(src)
            footprint = self.get_footprint(src)
            vrt_files = self.get_vrt_files(src)
            media_type = self.get_media_type(self.file_path)

            # Add projection extension properties
            proj_ext_props = self.get_proj_ext_properties(src)
            properties.update(proj_ext_props)

            # add the projection extension schema path
            stac_extensions.append(self.get_proj_ext_path())
            
            # return bbox, footprint, vrt_files
            # Return metadata in a flexible Metadata object
            metadata = Metadata(bbox=bbox, 
                                geometry=footprint, 
                                vrt_files=vrt_files, 
                                media_type=media_type, 
                                properties=properties, 
                                stac_extensions=stac_extensions)
            return metadata

    def get_bbox(self, src : rasterio.DatasetReader) -> List[float]:
        bbox = [src.bounds.left, src.bounds.bottom, src.bounds.right, src.bounds.top]
        return bbox 
        
    def get_footprint(self, src : rasterio.DatasetReader) -> Dict[str, Any]:
        """
        Helper method to compute the footprint of the VRT file.
        """
        
        bounds = src.bounds
        footprint = Polygon([
            [bounds.left, bounds.bottom],
            [bounds.left, bounds.top],
            [bounds.right, bounds.top],
            [bounds.right, bounds.bottom]
        ])

        return mapping(footprint)

    def get_vrt_files(self, src) -> list[str]:
        """
        Assuming we extract a list of VRT files involved.
        This would be a method to return the VRT-specific files.
        """
        return src.files if src.files else []

# Concrete Class for NetCDF Files
class NetCDFMetaData(MetaDataExtractor):
    """
    Metadata extraction for TIF files using rasterio.
    """

    def extract_metadata(self):
        """
        Extract metadata from a VRT file.
        Returns: (bbox, mapping(footprint), vrt_files)
        """
        properties = {} 
        stac_extensions = []

        # Open the NetCDF file remotely
        with xr.open_dataset(self.file_path) as src:
            
            bbox = self.get_bbox(src)
            footprint = self.get_footprint(bbox)
            media_type = self.get_media_type(self.file_path)

            # Add NetCDF specific attributes
            netcdf_attrs = self.get_netcdf_attrs(src)
            properties.update(netcdf_attrs)

            # Add projection extension properties            
            proj_ext_props = self.get_proj_ext_properties(src)
            properties.update(proj_ext_props)

            # add the projection extension schema path
            stac_extensions.append(self.get_proj_ext_path())

            # return bbox, footprint
            # Return metadata in a flexible Metadata object
            metadata = Metadata(bbox=bbox, 
                                geometry=footprint, 
                                media_type=media_type, 
                                properties=properties, 
                                stac_extensions=stac_extensions
                                )
            return metadata

    def get_bbox(self, src: xr.Dataset) -> List[float]:
            """
            Attempt to retrieve latitude and longitude variables from a NetCDF file 
            by trying several common variable names.
            """
            lat_names = ["lat", "latitude", "Latitude", "LAT", "y", "Y"]
            lon_names = ["lon", "longitude", "Longitude", "LON", "x", "X"]

            lat_var, lon_var = None, None

            # Find the first existing latitude variable
            for name in lat_names:
                if name in src.variables:
                    lat_var = name
                    break

            # Find the first existing longitude variable
            for name in lon_names:
                if name in src.variables:
                    lon_var = name
                    break

            if lat_var is None or lon_var is None:
                raise ValueError("Could not find latitude and/or longitude variables in the NetCDF file.")

            ymin, ymax = src[lat_var].min().values, src[lat_var].max().values
            xmin, xmax = src[lon_var].min().values, src[lon_var].max().values

            return [xmin, ymin, xmax, ymax]
            # return [float(xmin), float(ymin), float(xmax), float(ymax)]

    # def get_bbox(self, src: xr.Dataset) -> List[float]:

    #     # TODO: This needs to be improved to handle non lat/lon named dimensions/coordinates 
    #     # TODO: This will break on NetCDFs with different dimension names...
    #     # assumes that lat and lon are dimension names in the NetCDF file
    #     ymin, ymax = src['lat'].min().values, src['lat'].max().values
    #     xmin, xmax = src['lon'].min().values, src['lon'].max().values

    #     # TODO: confirm this is the correct order
    #     bbox = [float(xmin), float(ymin), float(xmax), float(ymax)]

    #     return bbox

    def get_footprint(self, bbox: list[float]) -> Dict[str, Any]:
        """
        Helper method to compute the footprint of the VRT file.
        """
        
        left, bottom, right, top = bbox
        
        footprint = Polygon([
            [left, bottom],
            [left, top],
            [right, top],
            [right, bottom]
        ])

        return mapping(footprint)

    def get_netcdf_attrs(self, src : xr.Dataset) -> dict:
        try:
            attrs = src.attrs
            return attrs
        except:
            return {}

# Factory class for metadata extractors
class MetaDataExtractorFactory:
    """
    Factory to create appropriate metadata extractors based on file type.
    """
    # Add a mapping to associate file extensions with metadata extractors
    _extractor_mapping = {
        ".tif": TIFMetaData,
        ".tiff" : TIFMetaData,
        ".vrt": VRTMetaData,
        ".nc" : NetCDFMetaData
    }

    @staticmethod
    def get_metadata_extractor(file_path: str) -> MetaDataExtractor:
        file_extension = os.path.splitext(file_path)[-1].lower()
        extractor_class = MetaDataExtractorFactory._extractor_mapping.get(file_extension)

        if not extractor_class:
            raise ValueError(f"Unsupported file type: {file_extension}")
        return extractor_class(file_path)
