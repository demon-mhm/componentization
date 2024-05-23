from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("ns.tdata")
except PackageNotFoundError:
    # package is not installed
    pass
