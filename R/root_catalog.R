library(rstac)
library(terra)
library(sf)
library(jsonlite)
library(lubridate)
library(uuid)
library(dplyr)

source("R/base_vars.R")
source("R/stac_utils.R")

# example usage

# initialize root catalog
catalog_path <- init_root_catalog(
catalog_dir = CATALOG_DIR,
title = "Multi-Source Geospatial Data Catalog",
description = "Comprehensive catalog of DEM and other geospatial datasets from various providers"
)

# define multiple datasets
datasets <- list(
# usgs 3dep dem
DatasetInfo(
    path = DEM_PATH,
    provider_name = "USGS",
    provider_url = "https://www.usgs.gov",
    collection_id = "usgs-3dep-dem",
    title = "USGS 3DEP Digital Elevation Model",
    description = "3DEP 1-meter Digital Elevation Model",
    dataset_type = "dem",
    use_vrt_as_item = TRUE
)

# # noaa dem
# DatasetInfo(
#   path = file.path(BASE_DIR, "noaa/dem/coastal_dem.vrt"),
#   provider_name = "NOAA",
#   provider_url = "https://www.noaa.gov",
#   collection_id = "noaa-coastal-dem",
#   title = "NOAA Coastal DEM",
#   description = "High-resolution coastal elevation data",
#   dataset_type = "dem"
# ),

# # example landcover dataset
# DatasetInfo(
#   path = file.path(BASE_DIR, "nlcd/nlcd_2019.tif"),
#   provider_name = "MRLC",
#   provider_url = "https://www.mrlc.gov",
#   collection_id = "nlcd-2019",
#   title = "National Land Cover Database 2019",
#   description = "NLCD 2019 land cover classification",
#   dataset_type = "landcover",
#   use_vrt_as_item = FALSE
# )
)

# add all datasets to catalog
add_datasets_to_catalog(catalog_path, datasets)
