from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass

@dataclass(init=True)
class STACCollectionSource:
    """Class for defining a STAC Data source"""
    id : Union[str, int]
    title: str
    description : str

@dataclass(init=True)
class STACItemSource:
    """Class for defining a STAC Item's Data source"""
    collection_id : Union[str, int]
    id : Union[str, int]
    data_path : str
    properties : Dict[str, Union[str, int, float]]
