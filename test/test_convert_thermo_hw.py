"""Test the convert_thermo_hw module."""
import os
import pkg_resources

import nbformat
from thermohw.convert_thermo_hw import pdf_exp, nb_exp


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


def test_tags() -> None:
    """Test tag support."""
    filename = os.path.join("test-cell-tags.ipynb")
    filename = pkg_resources.resource_filename(__name__, filename)
    res = {"remove_solution": True, "legacy": False}
    problem_nb = nbformat.read(filename, as_version=4)
    if "celltoolbar" in problem_nb.metadata:
        del problem_nb.metadata["celltoolbar"]
    solution_nb, _ = nb_exp.from_notebook_node(problem_nb, res)
    assert len(solution_nb) > 0
