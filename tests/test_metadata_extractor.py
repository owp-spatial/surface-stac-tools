import pytest
import tempfile
import os
import rasterio
import numpy as np
from stac_manager.stac_metadata import (
    MetaDataExtractorFactory, 
    TIFMetaData, 
    VRTMetaData, 
    NetCDFMetaData,
    Metadata
)

# ---------------------------------------------------------------------------------
# ---- Test Basic TIFs / VRTs -----
# ---------------------------------------------------------------------------------

class TestMetaDataExtractor:
    @pytest.fixture
    def create_test_tif(self):
        """Create a temporary GeoTIFF for testing"""
        with tempfile.NamedTemporaryFile(suffix='.tif', delete=False) as tmp:
            # Create a test raster
            with rasterio.open(
                tmp.name, 'w', 
                driver='GTiff', 
                height=10, width=10, 
                count=1, 
                dtype=np.uint8, 
                crs='+proj=latlong', 
                transform=rasterio.transform.from_bounds(-180, -90, 180, 90, 10, 10)
            ) as dst:
                # non random data
                dst.write(np.ones((1, 10, 10), dtype=np.uint8) * 255)
                # dst.write(np.random.randint(0, 255, (1, 10, 10), dtype=np.uint8))
            yield tmp.name

    @pytest.fixture
    def create_test_vrt(self, create_test_tif):
        """Create a VRT file referencing a test TIF"""
        with tempfile.NamedTemporaryFile(suffix='.vrt', delete=False) as tmp:
            # Create a VRT that references the test TIF
            vrt_content = f'''<VRTDataset rasterXSize="10" rasterYSize="10">
                <VRTRasterBand dataType="Byte" band="1">
                    <SimpleSource>
                        <SourceFilename relativeToVRT="0">{create_test_tif}</SourceFilename>
                        <SourceBand>1</SourceBand>
                    </SimpleSource>
                </VRTRasterBand>
            </VRTDataset>'''
            tmp.write(vrt_content.encode())
            tmp.flush()
            yield tmp.name

    def test_metadata_extractor_factory(self, create_test_tif, create_test_vrt):
        """Test MetaDataExtractorFactory returns correct extractor"""
        tif_extractor = MetaDataExtractorFactory.get_metadata_extractor(create_test_tif)
        vrt_extractor = MetaDataExtractorFactory.get_metadata_extractor(create_test_vrt)

        assert isinstance(tif_extractor, TIFMetaData)
        assert isinstance(vrt_extractor, VRTMetaData)

    def test_tif_metadata_extraction(self, create_test_tif):
        """Test metadata extraction for TIF files"""
        extractor = TIFMetaData(create_test_tif)
        metadata = extractor.extract_metadata()

        assert isinstance(metadata, Metadata)
        assert 'bbox' in metadata.metadata
        assert 'geometry' in metadata.metadata
        assert 'proj:' in str(metadata.metadata)

    def test_vrt_metadata_extraction(self, create_test_vrt):
        """Test metadata extraction for VRT files"""
        extractor = VRTMetaData(create_test_vrt)
        metadata = extractor.extract_metadata()

        assert isinstance(metadata, Metadata)
        assert 'bbox' in metadata.metadata
        assert 'geometry' in metadata.metadata
        assert 'vrt_files' in metadata.metadata
        assert isinstance(metadata.get('vrt_files'), list)

# ---------------------------------------------------------------------------------
# ---- Test Complex TIFs / VRTs -----
# ---------------------------------------------------------------------------------

# class TestComplexMetadataExtractor:
#     @pytest.fixture
#     def create_multiband_tif(self):
#         """Create a multiband GeoTIFF for testing"""
#         with tempfile.NamedTemporaryFile(suffix='.tif', delete=False) as tmp:
#             # Create a multiband raster
#             with rasterio.open(
#                 tmp.name, 'w', 
#                 driver='GTiff', 
#                 height=20, width=20, 
#                 count=3,  # 3 bands 
#                 dtype=np.uint16, 
#                 crs='+proj=utm +zone=33 +datum=WGS84', 
#                 transform=rasterio.transform.from_bounds(0, 0, 1000, 1000, 20, 20)
#             ) as dst:
#                 # Write i value data for 3 bands
#                 for i in range(3):
#                     dst.write(np.ones((1, 20, 20), dtype=np.uint16) * i, i+1)
#             yield tmp.name

#     @pytest.fixture
#     def create_complex_vrt(self, create_multiband_tif):
#         """Create a complex VRT referencing multiple files"""
#         with tempfile.NamedTemporaryFile(suffix='.vrt', delete=False) as tmp:
#             # Create a VRT with multiple source references
#             vrt_content = f'''<VRTDataset rasterXSize="20" rasterYSize="20">
#                 <VRTRasterBand dataType="UInt16" band="1">
#                     <SimpleSource>
#                         <SourceFilename relativeToVRT="0">{create_multiband_tif}</SourceFilename>
#                         <SourceBand>1</SourceBand>
#                     </SimpleSource>
#                 </VRTRasterBand>
#                 <VRTRasterBand dataType="UInt16" band="2">
#                     <SimpleSource>
#                         <SourceFilename relativeToVRT="0">{create_multiband_tif}</SourceFilename>
#                         <SourceBand>2</SourceBand>
#                     </SimpleSource>
#                 </VRTRasterBand>
#             </VRTDataset>'''
#             tmp.write(vrt_content.encode())
#             tmp.flush()
#             yield tmp.name

#     def test_multiband_tif_metadata(self, create_multiband_tif):
#         """Test metadata extraction for multiband TIF"""
#         extractor = TIFMetaData(create_multiband_tif)
#         metadata = extractor.extract_metadata()

#         assert isinstance(metadata, Metadata)
#         assert metadata.get('raster:bands') == 3
#         assert metadata.get('proj:epsg') == 32633  # UTM Zone 33N
#         assert 'bbox' in metadata.metadata
#         assert 'geometry' in metadata.metadata

#     def test_complex_vrt_metadata(self, create_complex_vrt):
#         """Test metadata extraction for complex VRT with multiple sources"""
#         extractor = VRTMetaData(create_complex_vrt)
#         metadata = extractor.extract_metadata()

#         assert isinstance(metadata, Metadata)
#         assert metadata.get('raster:bands') == 2
#         assert 'vrt_files' in metadata.metadata
#         assert len(metadata.get('vrt_files')) > 0

#     def test_unsupported_file_type(self):
#         """Test handling of unsupported file types"""
#         with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as tmp:
#             tmp.write(b'This is a test text file')
#             tmp.flush()

#         with pytest.raises(ValueError, match="Unsupported file type"):
#             MetaDataExtractorFactory.get_metadata_extractor(tmp.name)

#     def test_metadata_factory_registration(self):
#         """Test ability to register custom metadata extractors"""
#         class CustomMetaData:
#             def __init__(self, file_path):
#                 self.file_path = file_path
            
#             def extract_metadata(self):
#                 return Metadata({'custom': 'metadata'})

#         # Register custom extractor for a new file type
#         MetaDataExtractorFactory.register_extractor('.custom', CustomMetaData)

#         # Create a mock custom file
#         with tempfile.NamedTemporaryFile(suffix='.custom', delete=False) as tmp:
#             tmp.write(b'Custom file content')
#             tmp.flush()

#         # Test custom extractor retrieval and metadata extraction
#         extractor = MetaDataExtractorFactory.get_metadata_extractor(tmp.name)
#         assert isinstance(extractor, CustomMetaData)
        
#         metadata = extractor.extract_metadata()
#         assert metadata.get('custom') == 'metadata'

#     def test_corrupted_file_handling(self):
#         """Test handling of corrupted or invalid geospatial files"""
#         with tempfile.NamedTemporaryFile(suffix='.tif', delete=False) as tmp:
#             # Write intentionally corrupted file content
#             tmp.write(b'Corrupted TIF file')
#             tmp.flush()

#         with pytest.raises((ValueError, rasterio.RasterioError)):
#             MetaDataExtractorFactory.get_metadata_extractor(tmp.name)

# ---------------------------------------------------------------------------------
# ---- Test NetCDFMetaData -----
# ---------------------------------------------------------------------------------

        
# NC_URL = "http://thredds.northwestknowledge.net:8080/thredds/dodsC/NWCSC_INTEGRATED_SCENARIOS_ALL_CLIMATE/bcsd-nmme/dailyForecasts/bcsd_nmme_metdata_NCAR_forecast_was_daily.nc"
# # # NC_URL = "https://www.ngdc.noaa.gov/thredds/fileServer/crm/cudem/crm_vol9_2023.nc"
# # # NC_URL = "https://www.ngdc.noaa.gov/thredds/ncml/regional/crescent_city_13_navd88_2010.nc?catalog=https%3A%2F%2Fwww.ngdc.noaa.gov%2Fthredds%2Fcatalog%2Fregional%2Fcatalog.html&dataset=regionalDatasetScan%2Fcrescent_city_13_navd88_2010.nc"
# # # Open the NetCDF file remotely
# ds = xr.open_dataset(NC_URL)
# for key,val in ds.attrs.items():
#     print(f"{key}\n > '{val}'")
#     print()

# metadata = NetCDFMetaData(NC_URL)
# metadata.extract_metadata()

# with xr.open_dataset(NC_URL) as src:
#     print(src['lat'])

# # TODO: use this to make a test data set for testing NetCDFMetaData class
# time = np.arange(0, 10)  # 10 time steps
# lat = np.linspace(-90, 90, 5)  # 5 latitude points
# lon = np.linspace(-180, 180, 5)  # 5 longitude points
# data = np.random.random((len(time), len(lat), len(lon)))  # Random data for the variable
# ds = xr.Dataset(
#     {
#         "temperature": (["time", "lat", "lon"], data)  # Create a variable 'temperature'
#     },
#     coords={
#         "time": time,
#         "lat": lat,
#         "lon": lon
#     }
# )
# output_path = "path/to/local/netcdf.nc"
# ds.to_netcdf(output_path)
