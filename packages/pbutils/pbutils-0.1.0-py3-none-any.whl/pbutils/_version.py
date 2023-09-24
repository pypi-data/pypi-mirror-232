from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("pbutils")
except PackageNotFoundError:
    __version__ = "0.dev0"
