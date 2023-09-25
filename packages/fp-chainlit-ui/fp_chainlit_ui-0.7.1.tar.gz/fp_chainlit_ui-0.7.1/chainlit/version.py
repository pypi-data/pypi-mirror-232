from importlib import metadata

try:
    __version__ = "0.7.1"
except metadata.PackageNotFoundError:
    # Case where package metadata is not available.
    __version__ = "0.7.1"
