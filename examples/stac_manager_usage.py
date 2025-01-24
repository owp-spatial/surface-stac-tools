import os
from stac_manager.stac_manager import STACManager

import config.settings as settings

# Initialize the STACManager
manager = STACManager()

# --------------------------------------------------------------------------------------
# ----- Input variables -----
# --------------------------------------------------------------------------------------
COLLECTION_ID_1 = "tif-1"
COLLECTION_ID_2 = "tif-2"
COLLECTION_ID_3 = "vrt-1"

settings.CATALOG_URI
settings.ROOT_CATALOG_ID
settings.ROOT_CATALOG_TITLE
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------

catalog1 = manager.get_catalog(catalog_path = settings.CATALOG_URI,
                                              catalog_id=settings.ROOT_CATALOG_ID)
catalog1.describe()
# catalog1.catalog_path
# catalog1.save_catalog()
manager.describe_catalog(catalog1.id)

manager.add_collection_to_catalog(catalog_id=catalog1.id,
                                  collection_id=COLLECTION_ID_1,
                                  title=f"{COLLECTION_ID_1}-title",
                                  description=f"{COLLECTION_ID_1}-desc"
                                  )

# Add TIF 1 item to collection 1
manager.add_item_to_collection_in_catalog(
    catalog_id=catalog1.id,
    collection_id=COLLECTION_ID_1,
    data_path=settings.TIF_URI_1,
    properties={"priority": 2}
)

manager.describe_catalog(catalog1.id)

manager.save_all_catalogs()
settings.CATALOG_URI
catalog2 = manager.get_catalog(catalog_path = '/Volumes/T7SSD/hydrofabric-stac2/catalog.json',
                                                catalog_id='catalog2-id')
catalog2.describe()

manager.add_collection_to_catalog(catalog_id=catalog2.id,
                                    collection_id=COLLECTION_ID_2,
                                    title=f"{COLLECTION_ID_2}-title",
                                    description=f"{COLLECTION_ID_2}-desc"
                                    )

# Add TIF 2 item to collection 2
manager.add_item_to_collection_in_catalog(
    catalog_id=catalog2.id,
    collection_id=COLLECTION_ID_2,
    data_path=settings.TIF_URI_2,
    properties={"priority": 1}
)

manager.describe_catalog(catalog2.id)

manager.save_all_catalogs()
manager.describe_catalog(catalog1.id)
manager.remove_catalog(catalog_id=catalog1.id)

# # add a new collection 1
catalog_manager.add_child_collection(collection_id=COLLECTION_ID_1, 
                                     title=f"{COLLECTION_ID_1}-title", 
                                     description=f"{COLLECTION_ID_1}-desc"
                                     )

catalog_manager.describe() 

# Add TIF 1 item to collection 1
catalog_manager.add_item_to_collection(
    collection_id=COLLECTION_ID_1,
    data_path=settings.TIF_URI_1,
    properties={"priority": 2}
)



print(f"Catalog created/retrieved with custom ID: {catalog1.id}")

# Case 2: Retrieve the same catalog using the custom catalog_id
retrieved_catalog1 = manager.get_or_create_catalog(catalog_id=custom_catalog_id)
print(f"Catalog retrieved with custom ID: {retrieved_catalog1.id}")
print(f"Are catalog1 and retrieved_catalog1 the same? {catalog1 is retrieved_catalog1}")

# Case 3: Create a catalog without specifying a catalog_id
# This will auto-generate a catalog ID using the default ID and counter
catalog2 = manager.get_or_create_catalog()
print(f"Catalog created/retrieved with auto-generated ID: {catalog2.id}")

# Case 4: Retrieve the same catalog using the auto-generated ID
auto_generated_id = catalog2.id
retrieved_catalog2 = manager.get_or_create_catalog(catalog_id=auto_generated_id)
print(f"Catalog retrieved with auto-generated ID: {retrieved_catalog2.id}")
print(f"Are catalog2 and retrieved_catalog2 the same? {catalog2 is retrieved_catalog2}")

# Case 5: Create another catalog without specifying a catalog_id
# The ID should increment automatically
catalog3 = manager.get_or_create_catalog()
print(f"Catalog created/retrieved with next auto-generated ID: {catalog3.id}")