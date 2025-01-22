import os
from dotenv import load_dotenv
from pathlib import Path

# Locate the .env file
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"

# Load environment variables from the .env file
load_dotenv(dotenv_path=ENV_PATH)

DEBUG = os.getenv("DEBUG") == "True"
BASE_DIR = os.getenv("BASE_DIR")
CATALOG_DIR = os.getenv("CATALOG_DIR")
ROOT_CATALOG_NAME = os.getenv("ROOT_CATALOG_NAME")

CATALOG_URI = os.path.join(BASE_DIR, CATALOG_DIR, ROOT_CATALOG_NAME)
# CATALOG_URI = f"{BASE_DIR}/{CATALOG_DIR}/{ROOT_CATALOG_NAME}"

# Name data for the root STAC catalog
ROOT_CATALOG_ID = "hydrofabric-surfaces"
ROOT_CATALOG_TITLE = "Hydrofabric Surfaces STAC Catalog"
ROOT_CATALOG_DESCRIPTION = "A STAC catalog containing diverse hydrologic surfaces"


# TODO: Remove these testing files from the settings
VRT_URI = os.getenv("VRT_URI")
TIF_URI = os.getenv("TIF_URI")
TIF_URI_1 = os.getenv("TIF_URI_1")
TIF_URI_2 = os.getenv("TIF_URI_2")