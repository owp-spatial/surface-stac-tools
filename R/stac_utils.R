library(rstac)
library(terra)
library(sf)
library(jsonlite)
library(lubridate)
library(uuid)
library(dplyr)

# extract tif files from vrt using gdalinfo
extract_tif_files_from_vrt <- function(vrt_path) {
  cmd <- paste("gdalinfo -mdd files", vrt_path)
  gdalinfo_output <- try(system(cmd, intern = TRUE))
  
  if(inherits(gdalinfo_output, "try-error")) {
    stop("failed to execute gdalinfo command. ensure gdal is installed and accessible.")
  }
  
  tif_files <- gdalinfo_output[grep(".tif", gdalinfo_output)]
  tif_files <- trimws(gsub(".*= ", "", tif_files))
  
  if(length(tif_files) == 0) {
    warning("no tif files found in the vrt.")
  }
  
  return(tif_files)
}

# create root catalog structure
create_root_catalog <- function(title = "DEM Data Catalog", 
                              description = "Catalog of Digital Elevation Model datasets") {
  list(
    stac_version = "1.0.0",
    id = "root",
    type = "Catalog",
    title = title,
    description = description,
    links = list()
  )
}

# create collection structure with enhanced metadata
create_collection <- function(rast, 
                            collection_id,
                            title, 
                            description, 
                            providers = NULL,
                            dataset_type = "dem",
                            additional_properties = list()) {
  
  if (is.null(providers)) {
    providers <- list(list(
      name = "Default Provider",
      roles = list("producer", "processor"),
      url = "https://example.com"
    ))
  }
  
  collection <- list(
    stac_version = "1.0.0",
    type = "Collection",
    id = collection_id,
    title = title,
    description = description,
    license = "proprietary",
    providers = providers,
    extent = list(
      spatial = list(
        bbox = list(as.vector(terra::ext(rast))),
        crs = crs(rast)
      ),
      temporal = list(
        interval = list(list(
          format(Sys.time(), "%Y-%m-%dT%H:%M:%SZ"),
          NULL
        ))
      )
    ),
    summaries = list(
      "dem:type" = list(dataset_type),
      "dem:resolution" = list(res(rast)[1])
    ),
    links = list()
  )
  
  collection <- modifyList(collection, additional_properties)
  return(collection)
}

# create stac item for a raster file (vrt or tif)
create_stac_item <- function(raster_file, 
                           collection_id, 
                           dataset_type = "dem",
                           is_vrt = FALSE,
                           additional_properties = list()) {
  
  rast_data <- terra::rast(raster_file)
  bbox <- as.numeric(as.vector(terra::ext(rast_data)))
  
  item_id <- if(is_vrt) {
    paste0(tools::file_path_sans_ext(basename(raster_file)), "-vrt")
  } else {
    UUIDgenerate()
  }
  
  file_type <- if(is_vrt) {
    "application/x-vrt"
  } else {
    "image/tiff; application=geotiff"
  }

  item <- list(
    stac_version = "1.0.0",
    type = "Feature",
    id = item_id,
    collection = collection_id,
    geometry = sf::st_as_text(
      sf::st_as_sfc(
        sf::st_bbox(
          c(xmin = bbox[1], ymin = bbox[3], 
            xmax = bbox[2], ymax = bbox[4]),
          crs = terra::crs(rast_data, proj = T)
        )
      )
    ),
    properties = list(
      datetime = format(file.info(raster_file)$mtime, "%Y-%m-%dT%H:%M:%SZ"),
      "dem:type" = dataset_type,
      "dem:resolution" = terra::res(rast_data)[1],
      created = format(Sys.time(), "%Y-%m-%dT%H:%M:%SZ"),
      updated = format(Sys.time(), "%Y-%m-%dT%H:%M:%SZ")
    ),
    bbox = bbox,
    assets = list(
      data = list(
        href = raster_file,
        type = file_type,
        roles = list("data"),
        "raster:bands" = list(
          list(
            nodata = NA_real_,
            spatial_resolution = terra::res(rast_data)[1],
            unit = "meter"
          )
        )
      )
    ),
    links = list()
  )
  
  if(is_vrt) {
    # add reference to source files if it's a vrt
    source_files <- extract_tif_files_from_vrt(raster_file)
    item$assets$sources <- list(
      href = source_files,
      type = "image/tiff; application=geotiff",
      roles = list("source-data")
    )
  }
  
  item$properties <- modifyList(item$properties, additional_properties)
  return(item)
}

# process items for a collection
process_collection_items <- function(raster_files, 
                                   collection, 
                                   dataset_type, 
                                   is_vrt = FALSE,
                                   additional_properties = list()) {
  
  items <- list()
  for(raster_file in raster_files) {
    print(raster_file)
    item <- create_stac_item(
      raster_file = raster_file,
      collection_id = collection$id,
      dataset_type = dataset_type,
      is_vrt = is_vrt,
      additional_properties = additional_properties
    )
    
    # add item to collection links
    collection$links <- append(collection$links, list(list(
      rel = "item",
      href = paste0(item$id, ".json"),
      type = "application/json",
      title = basename(raster_file)
    )))
    
    items[[item$id]] <- item
  }
  return(list(collection = collection, items = items))
}

# prepare dataset for caßtalog
prepare_dataset_for_catalog <- function(vrt_path, 
                                      collection_id, 
                                      title, 
                                      description,
                                      dataset_type = "dem",
                                      providers = NULL,
                                      use_vrt_as_item = FALSE,
                                      additional_properties = list()) {
  
  # read vrt dataset
  vrt <- terra::rast(vrt_path)
  
  # create collection
  collection <- create_collection(
    rast = vrt,
    collection_id = collection_id,
    title = title,
    description = description,
    providers = providers,
    dataset_type = dataset_type,
    additional_properties = additional_properties
  )
  
  # process items based on strategy
  if(use_vrt_as_item) {
    # use vrt file as single item
    result <- process_collection_items(
      raster_files = vrt_path,
      collection = collection,
      dataset_type = dataset_type,
      is_vrt = TRUE,
      additional_properties = additional_properties
    )
  } else {
    # use individual tif files as items
    tif_files <- extract_tif_files_from_vrt(vrt_path)
    result <- process_collection_items(
      raster_files = tif_files,
      collection = collection,
      dataset_type = dataset_type,
      is_vrt = FALSE,
      additional_properties = additional_properties
    )
  }
  
  return(result)
}

# save JSON file
save_json <- function(data, filepath) {
  write(toJSON(data, auto_unbox = TRUE, pretty = TRUE), filepath)
  return(filepath)
}

# save catalog files
save_catalog_files <- function(catalog_dir, catalog, collection, items) {
  # create directory if it doesn't exist
  dir.create(catalog_dir, recursive = TRUE, showWarnings = FALSE)
  
  # save catalog
  save_json(catalog, file.path(catalog_dir, "catalog.json"))

  # save collection
  save_json(collection, file.path(catalog_dir, paste0(collection$id, "-collection.json")))

  # save items
  for(item_id in names(items)) {
    save_json(items[[item_id]], file.path(catalog_dir, paste0(item_id, ".json")))
  }
}

# main function to create stac catalog
create_stac_catalog_from_vrt <- function(vrt_path, 
                                       catalog_dir, 
                                       collection_id = "dem-conus",
                                       title = "CONUS Digital Elevation Model",
                                       description = "Digital Elevation Model dataset for CONUS",
                                       dataset_type = "dem",
                                       providers = NULL,
                                       use_vrt_as_item = FALSE,
                                       additional_properties = list()) {
  
  # prepare catalog data
  catalog <- create_root_catalog()
  
  # prepare dataset
  result <- prepare_dataset_for_catalog(
    vrt_path = vrt_path,
    collection_id = collection_id,
    title = title,
    description = description,
    dataset_type = dataset_type,
    providers = providers,
    use_vrt_as_item = use_vrt_as_item,
    additional_properties = additional_propertießs
  )
  
  # update catalog links
  catalog$links <- append(catalog$links, list(list(
    rel = "child",
    href = paste0(collection_id, "-collection.json"),
    type = "application/json",
    title = title
  )))
  
  # save all files
  save_catalog_files(catalog_dir, catalog, result$collection, result$items)
  
  return(catalog_dir)
}

# define dataset info class for consistent data handling
DatasetInfo <- function(path, 
                       provider_name, 
                       provider_url = NULL,
                       provider_roles = c("producer", "processor"),
                       collection_id = NULL,
                       title = NULL,
                       description = NULL,
                       dataset_type = "dem",
                       use_vrt_as_item = TRUE) {
  
  # automatically generate collection id if not provided
  if(is.null(collection_id)) {
    collection_id <- paste0(
      tolower(provider_name), "-",
      dataset_type, "-",
      tools::file_path_sans_ext(basename(path))
    )
  }
  
  # automatically generate title if not provided
  if(is.null(title)) {
    title <- paste(provider_name, dataset_type, "dataset")
  }
  
  # automatically generate description if not provided
  if(is.null(description)) {
    description <- paste("Dataset provided by", provider_name)
  }
  
  structure(list(
    path = path,
    provider = list(
      name = provider_name,
      url = provider_url,
      roles = provider_roles
    ),
    collection_id = collection_id,
    title = title,
    description = description,
    dataset_type = dataset_type,
    use_vrt_as_item = use_vrt_as_item,
    is_vrt = tolower(tools::file_ext(path)) == "vrt"
  ), class = "DatasetInfo")
}

# initialize root catalog
init_root_catalog <- function(catalog_dir, 
                                  title = "Geospatial Data Catalog",
                                  description = "Comprehensive catalog of geospatial datasets") {
  
  # create directory if it doesn't exist
  dir.create(catalog_dir, recursive = TRUE, showWarnings = FALSE)
  
  # create catalog structure
  catalog <- list(
    stac_version = "1.0.0",
    id = "root",
    type = "Catalog",
    title = title,
    description = description,
    links = list()
  )
  
  # save catalog
  catalog_path <- file.path(catalog_dir, "catalog.json")
  write(toJSON(catalog, auto_unbox = TRUE, pretty = TRUE), catalog_path)
  
  return(catalog_path)
}

# load existing catalog
load_catalog <- function(catalog_path) {
  if (!file.exists(catalog_path)) {
    stop("catalog file does not exist at: ", catalog_path)
  }
  return(fromJSON(catalog_path))
}

# function to add a dataset to an existing catalog
add_dataset_to_catalog <- function(catalog_path, dataset_info) {
  # validate input
  if (!inherits(dataset_info, "DatasetInfo")) {
    stop("dataset_info must be created using DatasetInfo()")
  }
  
  # load existing catalog
  catalog <- load_catalog(catalog_path)
  catalog_dir <- dirname(catalog_path)
  
  # prepare dataset
  result <- prepare_dataset_for_catalog(
    vrt_path = dataset_info$path,
    collection_id = dataset_info$collection_id,
    title = dataset_info$title,
    description = dataset_info$description,
    dataset_type = dataset_info$dataset_type,
    providers = list(dataset_info$provider),
    use_vrt_as_item = dataset_info$use_vrt_as_item
  )
  
  # update catalog links
  collection_filename <- paste0(dataset_info$collection_id, "-collection.json")
  catalog$links <- append(catalog$links, list(list(
    rel = "child",
    href = collection_filename,
    type = "application/json",
    title = dataset_info$title
  )))
  
  # save updated files
  save_catalog_files(catalog_dir, catalog, result$collection, result$items)
  
  return(catalog_path)
}

# add multiple datasets to catalog
add_datasets_to_catalog <- function(catalog_path, dataset_info_list) {
  for (dataset_info in dataset_info_list) {
    catalog_path <- add_dataset_to_catalog(catalog_path, dataset_info)
  }
  return(catalog_path)
}
