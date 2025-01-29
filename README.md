# **surface-stac**

# Installation:
```bash
pip install git+https://github.com/owp-spatial/surface-stac-tools.git
```

# Catalog Manager for initializing and managing a STAC catalog
This guide explains how to use the provided Python script for managing a STAC catalog, including setting up the initial catalog, adding collections, and adding items to collections.

## Prerequisites
- **Python Libraries**: Install required dependencies from `requirements.txt` file.
- **Configuration**: Ensure that the configuration file `config/settings.py` is correctly set up with the following variables:
  - `CATALOG_URI`: Path or URI where the catalog is stored (or will be created).
  - `ROOT_CATALOG_TITLE`: Title of the root catalog.
  - `ROOT_CATALOG_DESCRIPTION`: Description of the root catalog.

## Steps to Use the Script

### 1. Setup the Catalog

To initialize or load an existing catalog, the script uses the `CatalogManager` class. The catalog is set up with the following parameters:

- **Catalog Path**: The location of the catalog (specified in `settings.CATALOG_URI`).
- **Title**: The title of the catalog (specified in `settings.ROOT_CATALOG_TITLE`).
- **Description**: The description of the catalog (specified in `settings.ROOT_CATALOG_DESCRIPTION`).

Example initialization:
```python
catalog_manager = CatalogManager(
    catalog_path=settings.CATALOG_URI,
    id=settings.ROOT_CATALOG_ID,
    title=settings.ROOT_CATALOG_TITLE,
    description=settings.ROOT_CATALOG_DESCRIPTION
)

catalog_manager.describe()
```

### 2. Add a New Collection

A collection groups related items in the catalog. To add a new collection, use the `add_child_collection` method with the following parameters:
- **`collection_id`**: Unique identifier for the collection.
- **`title`**: A descriptive title for the collection.
- **`description`**: A description of the collection.

Example:
```python
catalog_manager.add_child_collection(
    collection_id="tif-1",
    title="TIF-1 Collection Title",
    description="TIF-1 Collection Description"
)
```

### 3. Add a New Item to a Collection

Items represent individual resources (e.g., images, datasets) within a collection. Use the `add_item_to_collection` method to add an item, providing:
- **`collection_id`**: ID of the target collection.
- **`data_path`**: Path or URI of the data file to be added.
- **`properties`**: Dictionary of additional properties for the item.

Example:
```python
catalog_manager.add_item_to_collection(
    collection_id="tif-1",
    data_path="s3://bucket/tif-1.tif",
    properties={"priority": 2}
)
```

### 4. Save the Catalog
After making changes to the catalog (e.g., adding collections or items), save it using the `save_catalog` method. This ensures all changes are persisted.

Example:
```python
catalog_manager.save_catalog(catalog_type=pystac.CatalogType.SELF_CONTAINED)
```

### Script Workflow
1. **Load or Create Catalog:** The script initializes the catalog manager and sets the catalog title and description.
2. **Add Collections:** Multiple collections can be added to the catalog using the provided IDs, titles, and descriptions.
3. **Add Items:** Items are added to the respective collections with associated properties.
4. **Save Catalog:** The catalog is saved in a self-contained format for portability.