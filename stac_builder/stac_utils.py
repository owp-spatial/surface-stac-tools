import os
from abc import ABC, abstractmethod
import json
import urllib.request
from datetime import datetime, timezone
from dataclasses import dataclass
from typing import List, Optional, Dict, Any

import rasterio
import pystac
from pystac import MediaType
from pathlib import Path
import uuid

from shapely.geometry import Polygon, mapping
from tempfile import TemporaryDirectory
from stac_builder.constants import BASE_DIR, DEM_PATH, CATALOG_DIR, FILE_EXT_TO_MEDIA_TYPE

# class Metadata:
#     """
#     Class to hold metadata attributes in a flexible manner.
#     Attributes are stored as key-value pairs in a dictionary.
#     """

#     def __init__(self, **kwargs):
#         """
#         Initialize Metadata with dynamic attributes.
#         The kwargs allow passing arbitrary attributes.
#         """
#         self.metadata = kwargs

#     def get(self, key):
#         """
#         Get the value of a specific metadata attribute.
#         """
#         return self.metadata.get(key)

#     def set(self, key, value):
#         """
#         Set the value of a specific metadata attribute.
#         """
#         self.metadata[key] = value

#     def __repr__(self):
#         return f"Metadata({self.metadata})"

# # Abstract Base Class for Metadata Extractors
# class MetaDataExtractor(ABC):
#     """
#     Abstract base class for metadata extraction.
#     """

#     def __init__(self, file_path: str):
#         self.file_path = file_path

#     @abstractmethod
#     def extract_metadata(self):
#         """
#         Abstract method to extract metadata from the file.
#         """
#         pass

#     @classmethod
#     def get_media_type(cls, file_path: str) -> MediaType:
#         """
#         Infers the pystac.MediaType enum based on the file extension.

#         Args:
#             file_path (str): The path or name of the file.

#         Returns:
#             MediaType: The inferred MediaType enum value, or None if not matched.
#         """
#         # Get the file extension
#         _, ext = os.path.splitext(file_path)
#         ext = ext.lower()

#         # Return the corresponding MediaType enum or None if not found
#         return FILE_EXT_TO_MEDIA_TYPE.get(ext)


# # Concrete Class for TIF Files
# class TIFMetaData(MetaDataExtractor):
#     """
#     Metadata extraction for TIF files using rasterio.
#     """

#     def extract_metadata(self):
#         """
#         Extract metadata from a VRT file.
#         Returns: (bbox, mapping(footprint), vrt_files)
#         """

#         # Assuming you have a way to open and read VRT metadata, e.g., using rasterio
#         with rasterio.open(self.file_path) as src:
            
#             bbox = self.get_bbox(src)
#             footprint = self.get_footprint(src)
#             media_type = self.get_media_type(self.file_path)
#             # return bbox, footprint
#             # Return metadata in a flexible Metadata object
#             metadata = Metadata(bbox=bbox, geometry=footprint, media_type=media_type)
#             return metadata

#     def get_bbox(self, src):
#         bbox = [src.bounds.left, src.bounds.bottom, src.bounds.right, src.bounds.top]
#         return bbox 
        
#     def get_footprint(self, src):
#         """
#         Helper method to compute the footprint of the VRT file.
#         """
        
#         bounds = src.bounds
#         footprint = Polygon([
#             [bounds.left, bounds.bottom],
#             [bounds.left, bounds.top],
#             [bounds.right, bounds.top],
#             [bounds.right, bounds.bottom]
#         ])

#         return footprint

# # Concrete Class for VRT Files
# class VRTMetaData(MetaDataExtractor):
#     """
#     Metadata extraction for TIF files using rasterio.
#     """

#     def extract_metadata(self):
#         """
#         Extract metadata from a VRT file.
#         Returns: (bbox, mapping(footprint), vrt_files)
#         """

#         # Assuming you have a way to open and read VRT metadata, e.g., using rasterio
#         with rasterio.open(self.file_path) as src:
            
#             bbox = self.get_bbox(src)
#             footprint = self.get_footprint(src)
#             vrt_files = self.get_vrt_files(src)
#             media_type = self.get_media_type(self.file_path)
#             # return bbox, footprint, vrt_files
#             # Return metadata in a flexible Metadata object
#             metadata = Metadata(bbox=bbox, geometry=footprint, vrt_files=vrt_files, media_type=media_type)
#             return metadata

#     def get_bbox(self, src):
#         bbox = [src.bounds.left, src.bounds.bottom, src.bounds.right, src.bounds.top]
#         return bbox 
        
#     def get_footprint(self, src):
#         """
#         Helper method to compute the footprint of the VRT file.
#         """
        
#         bounds = src.bounds
#         footprint = Polygon([
#             [bounds.left, bounds.bottom],
#             [bounds.left, bounds.top],
#             [bounds.right, bounds.top],
#             [bounds.right, bounds.bottom]
#         ])

#         return footprint

#     def get_vrt_files(self, src):
#         """
#         Assuming we extract a list of VRT files involved.
#         This would be a method to return the VRT-specific files.
#         """
#         return {"files": src.files}
 
# # Factory Class to Instantiate Correct Metadata Extractor
# class MetaDataExtractorFactory:
#     """
#     Factory class to create an appropriate metadata extractor based on file type.
#     """

#     @staticmethod
#     def get_metadata_extractor(file_path: str) -> MetaDataExtractor:
#         """
#         Factory method to create the appropriate metadata extractor based on file type.
#         """
#         file_extension = os.path.splitext(file_path)[-1].lower()

#         if file_extension == ".tif":
#             return TIFMetaData(file_path)
#         elif file_extension == ".vrt":
#             return VRTMetaData(file_path)
#         else:
#             raise ValueError(f"Unsupported file type: {file_extension}")

# TODO:
# this still needs to be testedo out to make sure it works as intended and
#  that it is the correct way to do
def get_media_type(file_path: str) -> MediaType:
    """
    Infers the pystac.MediaType enum based on the file extension.

    Args:
        file_path (str): The path or name of the file.

    Returns:
        MediaType: The inferred MediaType enum value, or None if not matched.
    """
    # get file extension 
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()

    # Return the corresponding MediaType enum or None if not found
    return FILE_EXT_TO_MEDIA_TYPE.get(ext)

def get_bbox_and_footprint(raster):
    with rasterio.open(raster) as r:
        bounds = r.bounds
        bbox = [bounds.left, bounds.bottom, bounds.right, bounds.top]
        footprint = Polygon([
            [bounds.left, bounds.bottom],
            [bounds.left, bounds.top],
            [bounds.right, bounds.top],
            [bounds.right, bounds.bottom]
        ])
        
        return (bbox, mapping(footprint))

def get_vrt_metadata(raster):
    with rasterio.open(raster) as r:
        bounds = r.bounds
        bbox = [bounds.left, bounds.bottom, bounds.right, bounds.top]
        footprint = Polygon([
            [bounds.left, bounds.bottom],
            [bounds.left, bounds.top],
            [bounds.right, bounds.top],
            [bounds.right, bounds.bottom]
        ])
        vrt_files = r.files
        
        return (bbox, mapping(footprint), vrt_files)

@dataclass
class DatasetInfo:
    """dataclass to store dataset information and metadata"""
    path: str
    provider_name: str
    provider_url: Optional[str] = None
    provider_roles: List[str] = None
    collection_id: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    dataset_type: str = "dem"
    use_vrt_as_item: bool = True

    def __post_init__(self):
        """automatically generate missing fields after initialization"""
        if self.provider_roles is None:
            self.provider_roles = ["producer", "processor"]
            
        if self.collection_id is None:
            base_name = Path(self.path).stem
            self.collection_id = f"{self.provider_name.lower()}-{self.dataset_type}-{base_name}"
            
        if self.title is None:
            self.title = f"{self.provider_name} {self.dataset_type.upper()} dataset"
            
        if self.description is None:
            self.description = f"Dataset provided by {self.provider_name}"
            
        self.is_vrt = Path(self.path).suffix.lower() == ".vrt"

def init_root_catalog(
    catalog_dir: str,
    title: str = "Geospatial Data Catalog",
    description: str = "Comprehensive catalog of geospatial datasets"
) -> pystac.Catalog:
    """create and initialize a root stac catalog"""
    
    # create directory if it doesn't exist
    os.makedirs(catalog_dir, exist_ok=True)
    
    # create catalog
    catalog = pystac.Catalog(
        id="root",
        description=description,
        title=title
    )
    
    # save catalog
    catalog.normalize_hrefs(catalog_dir)
    catalog.save(catalog_type=pystac.CatalogType.SELF_CONTAINED)
    
    return catalog

def get_raster_metadata(raster_path: str) -> Dict[str, Any]:
    """extract metadata from a raster file"""
    with rasterio.open(raster_path) as src:
        bounds = src.bounds
        bbox = [bounds.left, bounds.bottom, bounds.right, bounds.top]
        
        metadata = {
            "bbox": bbox,
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [bounds.left, bounds.bottom],
                    [bounds.left, bounds.top],
                    [bounds.right, bounds.top],
                    [bounds.right, bounds.bottom],
                    [bounds.left, bounds.bottom]
                ]]
            },
            "resolution": src.res[0],
            "crs": src.crs.to_string(),
            "transform": list(src.transform),
            "shape": src.shape
        }
    
    return metadata

def extract_vrt_sources(vrt_path: str) -> List[str]:
    """extract source files from a vrt"""
    with rasterio.open(vrt_path) as src:
        if isinstance(src, vrt.WarpedVRT):
            # for warped vrts, get the source dataset
            sources = [src.src_dataset.name]
        else:
            # for regular vrts, get all source paths
            sources = [src_path for src_path in src.files if src_path != vrt_path]
    
    return sources

def create_raster_item(
    dataset_info: DatasetInfo,
    raster_path: str,
    collection: pystac.Collection
) -> pystac.Item:
    """create a stac item from a raster file"""
    
    # get raster metadata
    metadata = get_raster_metadata(raster_path)
    
    # create unique id for the item
    item_id = str(uuid.uuid4()) if not dataset_info.is_vrt else f"{Path(raster_path).stem}-vrt"
    
    # create the item
    item = pystac.Item(
        id=item_id,
        geometry=metadata["geometry"],
        bbox=metadata["bbox"],
        datetime=datetime.utcnow(),
        properties={
            f"{dataset_info.dataset_type}:type": dataset_info.dataset_type,
            f"{dataset_info.dataset_type}:resolution": metadata["resolution"],
            "created": datetime.utcnow().isoformat() + "Z",
            "updated": datetime.utcnow().isoformat() + "Z"
        }
    )
    
    # add the main raster asset
    item.add_asset(
        key="data",
        asset=pystac.Asset(
            href=os.path.abspath(raster_path),
            media_type="application/x-vrt" if dataset_info.is_vrt else "image/tiff; application=geotiff",
            roles=["data"],
            extra_fields={
                "raster:bands": [{
                    "nodata": None,
                    "spatial_resolution": metadata["resolution"],
                    "unit": "meter"
                }]
            }
        )
    )
    
    # if it's a vrt, add source files as additional assets
    if dataset_info.is_vrt:
        source_files = extract_vrt_sources(raster_path)
        item.add_asset(
            key="sources",
            asset=pystac.Asset(
                href=source_files,
                media_type="image/tiff; application=geotiff",
                roles=["source-data"]
            )
        )
    
    return item

def create_collection_for_raster_dataset(dataset_info: DatasetInfo) -> pystac.Collection:
    """create a stac collection for a dataset"""
    
    # get temporal and spatial extent from the data
    metadata = get_raster_metadata(dataset_info.path)
    
    # create provider
    provider = pystac.Provider(
        name=dataset_info.provider_name,
        roles=dataset_info.provider_roles,
        url=dataset_info.provider_url
    )
    
    # create spatial and temporal extent
    extent = pystac.Extent(
        spatial=pystac.SpatialExtent([metadata["bbox"]]),
        temporal=pystac.TemporalExtent([[datetime.utcnow(), None]])
    )
    
    # create collection
    collection = pystac.Collection(
        id=dataset_info.collection_id,
        description=dataset_info.description,
        extent=extent,
        title=dataset_info.title,
        providers=[provider],
        extra_fields={
            f"{dataset_info.dataset_type}:type": dataset_info.dataset_type,
            f"{dataset_info.dataset_type}:resolution": metadata["resolution"]
        }
    )
    
    return collection

def add_dataset_to_catalog(
    catalog: pystac.Catalog,
    dataset_info: DatasetInfo
) -> pystac.Catalog:
    """add a dataset to the catalog as a collection with items"""
    
    # create collection for the dataset
    collection = create_collection_for_raster_dataset(dataset_info)
    catalog.add_child(collection)
    
    if dataset_info.use_vrt_as_item and dataset_info.is_vrt:
        # add vrt as a single item
        item = create_raster_item(dataset_info, dataset_info.path, collection)
        collection.add_item(item)
    else:
        # add individual files as items
        source_files = extract_vrt_sources(dataset_info.path) if dataset_info.is_vrt else [dataset_info.path]
        for file_path in source_files:
            item = create_raster_item(dataset_info, file_path, collection)
            collection.add_item(item)
    
    return catalog

def add_datasets_to_catalog(
    catalog: pystac.Catalog,
    dataset_info_list: List[DatasetInfo]
) -> pystac.Catalog:
    """add multiple datasets to the catalog"""
    for dataset_info in dataset_info_list:
        catalog = add_dataset_to_catalog(catalog, dataset_info)
    return catalog

# # example usage
# def main():
#     # define base directories
#     base_dir = "/Volumes/T7SSD/"
#     catalog_dir = os.path.join(base_dir, "geospatial-stac")
    
#     # initialize root catalog
#     catalog = init_root_catalog(
#         catalog_dir=catalog_dir,
#         title="Multi-Source Geospatial Data Catalog",
#         description="Comprehensive catalog of DEM and other geospatial datasets from various providers"
#     )
    
#     # define datasets
#     datasets = [
#         # usgs 3dep dem
#         DatasetInfo(
#             path=DEM_PATH,
#             provider_name="USGS",
#             provider_url="https://www.usgs.gov",
#             collection_id="usgs-3dep-dem",
#             title="USGS 3DEP Digital Elevation Model",
#             description="3DEP 1-meter Digital Elevation Model",
#             dataset_type="dem",
#             use_vrt_as_item=True
#         ),
        
#         # # noaa dem
#         # DatasetInfo(
#         #     path=os.path.join(BASE_DIR, "noaa/dem/coastal_dem.vrt"),
#         #     provider_name="NOAA",
#         #     provider_url="https://www.noaa.gov",
#         #     collection_id="noaa-coastal-dem",
#         #     title="NOAA Coastal DEM",
#         #     description="High-resolution coastal elevation data",
#         #     dataset_type="dem"
#         # ),
        
#         # # example landcover dataset
#         # DatasetInfo(
#         #     path=os.path.join(BASE_DIR, "nlcd/nlcd_2019.tif"),
#         #     provider_name="MRLC",
#         #     provider_url="https://www.mrlc.gov",
#         #     collection_id="nlcd-2019",
#         #     title="National Land Cover Database 2019",
#         #     description="NLCD 2019 land cover classification",
#         #     dataset_type="landcover",
#         #     use_vrt_as_item=False
#         # )
#     ]
    
#     # add all datasets to catalog
#     catalog = add_datasets_to_catalog(catalog, datasets)
    
#     # save the catalog
#     catalog.save(catalog_type=pystac.CatalogType.SELF_CONTAINED)

# if __name__ == "__main__":
#     main()