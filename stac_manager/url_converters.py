# item_manager.py
from typing import Dict, Any, Optional, List
from urllib.parse import urlparse, urlunparse

# TODO: this class is specifically designed to work on 'ngdc' URLs and convert them from using "filesServer" or "ncml" formatted URLs into URLs that use
# TODO: the dodsC protocol in the URL to allow for remote file access and meta data extraction
class NGDCNetCDFUrlConverter:

    def __init__(self, url:str):
        self._url = url
        self._clean_url = None
        self.init_clean_url()

    def _is_nc_url(self):
        return ".nc" in self._url
    
    def _is_ngdc_url(self):
        return "www.ngdc" in urlparse(self._url).netloc

    def _is_thredds_url(self):
        return "thredds" in self._url.lower()
    
    def _is_eligible(self):
        return self._is_nc_url() and self._is_ngdc_url() and self._is_thredds_url()

    def init_clean_url(self) -> None:
        if self._is_nc_url() and self._is_ngdc_url() and self._is_thredds_url():
            self._clean_nc_url()
            self._convert_to_dods_url()
        return 

    def get_url(self):
        return self._url

    def get_clean_url(self):
        return self._clean_url if self._clean_url else self._url

    def _clean_nc_url(self) -> None:
        """Removes query parameters from a NetCDF URL, preserving the base .nc file path."""
        parsed_url = urlparse(self._url)
        
        # Reconstruct the URL without query parameters
        self._clean_url = urlunparse((parsed_url.scheme, parsed_url.netloc, parsed_url.path, '', '', ''))

        return 

    def _convert_to_dods_url(self) -> None:
        """
        Convert a THREDDS file URL to its OpenDAP-compatible /dodsC/ URL if possible.
        Returns:
            None
        """

        # Convert fileServer or ncml URL to dodsC
        if "/fileServer/" in self._clean_url:
            self._clean_url = self._clean_url.replace("/fileServer/", "/dodsC/")
        elif "/ncml/" in self._clean_url:
            self._clean_url = self._clean_url.replace("/ncml/", "/dodsC/")
        else:
            self._clean_url = self._clean_url  # assume it's already an OpenDAP-compatible URL

        return 