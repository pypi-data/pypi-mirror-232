import os

import dolomite_schemas
from dolomite_schemas import get_schema_directory

__author__ = "Jayaram Kancherla"
__copyright__ = "jkanche"
__license__ = "MIT"


def test_includes():
    out = get_schema_directory()
    assert isinstance(out, str)
    assert os.path.isdir(os.path.join(out, "array"))
    assert os.path.isdir(os.path.join(out, "vcf_file"))
    assert os.path.isdir(os.path.join(out, "single_cell_experiment"))

    # The recommended way works as well.
    assert out == os.path.join(os.path.dirname(dolomite_schemas.__file__), "schemas")
