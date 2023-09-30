from __future__ import annotations

import pkgutil
import sys

sys.path.append(".")

from . import domain, exc, ext, std
from .exc import CustomException


# pkg_import_map: dict = {"loguru": "red_utils.utils.loguru_utils"}

# def pkgutil_loader(package_import_map: dict = {}) -> None:
#     """For dependencies with requirements, ensure library is only imported
#     if namespace package is installed.

#     Example:

#         red_utils.utils.sqlalchemy_utils will only be imported if sqlalchemy is installed.

#     """
#     if not package_import_map:
#         return ValueError("Package import mapping is empty, no additional utils will be imported.")

#     if not isinstance(package_import_map, dict):
#         return TypeError(f"Invalid type for package_import_map: ({type(package_import_map)}). Must be a dict. No additional utils will be imported.")

#     for k, v in package_import_map.items():
#         if not isinstance(k, str) or not isinstance(v, str):
#             return TypeError(f"""
#                              Invalid key/value pair in package_import_map, keys and values must both be of type str.
#                                 Key [{k}]:({type(k)})
#                                 Value [{v}]:({type(v)}))
#                                 """
#                              )

#         if pkgutil.find_loader(k):
#             pkgutil.get_importer(v)

# pkgutil_loader(package_import_map=pkg_import_map)
