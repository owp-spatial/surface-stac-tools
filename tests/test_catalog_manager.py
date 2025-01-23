import os
import pytest
import tempfile
import pystac
import rasterio
import numpy as np
from pathlib import Path

from stac_manager.catalog_manager import CatalogManager
from stac_manager.stac_metadata import MetaDataExtractorFactory
from stac_manager.constants import DEFAULT_ROOT_CATALOG_ID, DEFAULT_ROOT_CATALOG_TITLE, DEFAULT_ROOT_CATALOG_DESC

class TestCatalogManager:
    @pytest.fixture
    def temp_catalog_path(self):
        """Create a temporary directory for catalog testing"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def catalog_manager(self, temp_catalog_path):
        """Create a CatalogManager instance for testing"""
        return CatalogManager(catalog_path=temp_catalog_path)
    
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

    def test_catalog_initialization(self, catalog_manager):
        """Test catalog is created with default values when no metadata is provided"""
        assert catalog_manager.get_catalog() is not None
        assert catalog_manager.get_catalog().id == DEFAULT_ROOT_CATALOG_ID 
        assert catalog_manager.get_catalog().description == DEFAULT_ROOT_CATALOG_DESC

    def test_set_catalog_id(self, catalog_manager):
        """Test setting the catalog ID"""
        catalog_manager.set_catalog_id('test-catalog')
        catalog = catalog_manager.get_catalog()
        assert catalog.id == 'test-catalog'
    
    def test_set_catalog_title(self, catalog_manager):
        """Test setting the catalog title"""
        catalog_manager.set_catalog_title('Test Catalog')
        catalog = catalog_manager.get_catalog()
        assert catalog.title == 'Test Catalog'
    
    def test_set_catalog_description(self, catalog_manager):
        """Test setting the catalog description"""
        catalog_manager.set_catalog_description('A catalog for testing')
        catalog = catalog_manager.get_catalog()
        assert catalog.description == 'A catalog for testing'

    def test_add_collection(self, catalog_manager):
        """Test adding a collection to the catalog"""
        catalog_manager.add_child_collection(
            collection_id='test-collection', 
            title='Test Collection', 
            description='A collection for testing'
        )

        collections = list(catalog_manager.get_children())
        assert len(collections) == 1
        assert collections[0].id == 'test-collection'
        assert collections[0].title == 'Test Collection'

    def test_remove_collection(self, catalog_manager):
        """Test removing a collection from the catalog"""
        catalog_manager.add_child_collection(
            collection_id='test-collection', 
            title='Test Collection', 
            description='A collection for testing'
        )

        catalog_manager.remove_collection('test-collection')
        collections = list(catalog_manager.get_children())
        print(f"collections: {collections}")
        assert len(collections) == 0

    def test_add_item_to_collection(self, catalog_manager, create_test_tif):
        """Test adding an item to a collection"""

        # Add a collection first
        catalog_manager.add_child_collection(
            collection_id='test-collection', 
            title='Test Collection', 
            description='A collection for testing'
        )

        # Add item to collection
        catalog_manager.add_item_to_collection(
            collection_id='test-collection', 
            # data_path=test_tif
            data_path=create_test_tif
        )

        # Verify item was added
        collection = catalog_manager.get_collection_by_id('test-collection')
        items = list(collection.get_items())
        assert len(items) == 1
        assert items[0].id == Path(create_test_tif).stem

    def test_update_item_properties(self, catalog_manager, create_test_tif):
        """Test updating item properties"""

        # Add a collection and item
        catalog_manager.add_child_collection(
            collection_id='test-collection', 
            title='Test Collection', 
            description='A collection for testing'
        )
        catalog_manager.add_item_to_collection(
            collection_id='test-collection', 
            data_path=create_test_tif
        )

        # Update item properties
        catalog_manager.update_item_properties(
            collection_id='test-collection', 
            item_id=Path(create_test_tif).stem,
            properties={'custom_property': 'test_value'}
        )

        # Verify properties were updated
        item = catalog_manager.get_item_by_id('test-collection', Path(create_test_tif).stem)
        assert item.properties.get('custom_property') == 'test_value'