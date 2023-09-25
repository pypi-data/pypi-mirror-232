import importlib.metadata

__version__ = importlib.metadata.version("pytest-maxcov")

pytest_plugins = ["pytest_maxcov.plugin"]
