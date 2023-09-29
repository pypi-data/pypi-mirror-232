import inspect
import os

__author__ = "Jayaram Kancherla"
__copyright__ = "jkanche"
__license__ = "MIT"


def get_schema_directory() -> str:
    """Get the path to the directory containing artifactdb schemas.

    Returns:
        str: Path to a directory.
    """
    dirname = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    return os.path.join(dirname, "schemas")
