"""Test the convert_thermo_hw module."""
import os
import pkg_resources

from ..convert_thermo_hw import pdf_exp


def test_convert_pathological_image_name() -> None:
    """Test that converting a notebook with a pathological image name works."""
    filename = os.path.join("test-pathological-image-name.ipynb")
    filename = pkg_resources.resource_filename(__name__, filename)
    res = {
        "unique_key": "test-pathological-image-name",
        "by_hand": False,
        "remove_solution": False,
    }
    solution_pdf, _ = pdf_exp.from_filename(filename, res)
    assert len(solution_pdf) > 0
