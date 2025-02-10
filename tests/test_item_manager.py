import pytest
import tempfile
import os
from stac_manager.item_manager import ItemFactoryManager, RasterItemFactory, VRTItemFactory, NetCDFItemFactory
from stac_manager.stac_metadata import MetaDataExtractorFactory

class TestItemFactoryManager:
    @pytest.fixture
    def item_factory_manager(self):
        """Create an ItemFactoryManager instance for testing"""
        return ItemFactoryManager(MetaDataExtractorFactory())

    def test_get_supported_types(self, item_factory_manager):
        """Test getting supported data types"""
        supported_types = item_factory_manager.get_supported_types()
        assert set(supported_types) == {'tif', 'tiff', 'vrt', 'nc'}

    def test_get_raster_item_factory(self, item_factory_manager):
        """Test getting a RasterItemFactory for TIF files"""
        factory = item_factory_manager.get_item_factory('tif')
        assert isinstance(factory, RasterItemFactory)

    def test_get_vrt_item_factory(self, item_factory_manager):
        """Test getting a VRTItemFactory for VRT files"""
        factory = item_factory_manager.get_item_factory('vrt')
        assert isinstance(factory, VRTItemFactory)

    def test_get_netcdf_item_factory(self, item_factory_manager):
        """Test getting a NetCDFItemFactory for NetCDF files"""
        factory = item_factory_manager.get_item_factory('nc')
        assert isinstance(factory, NetCDFItemFactory)

    def test_unsupported_type_raises_error(self, item_factory_manager):
        """Test that an unsupported file type raises a ValueError"""
        with pytest.raises(ValueError, match="Unsupported data type"):
            item_factory_manager.get_item_factory('unsupported')

    def test_register_new_factory(self, item_factory_manager):
        """Test registering a new item factory type"""
        class CustomItemFactory:
            def __init__(self, metadata_extractor_factory):
                pass

        item_factory_manager.register_factory('custom', CustomItemFactory)
        factory = item_factory_manager.get_item_factory('custom')
        assert isinstance(factory, CustomItemFactory)
