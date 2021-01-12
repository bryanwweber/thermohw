"""Preprocessors for homework assignments.

This module contains the preprocessors that are used to convert
Notebooks into homework assignments.

Classes
-------
HomeworkPreprocessor:
    Preprocess a homework problem for notes and other things that don't
    belong in an assignment.

SolnRemoverPreprocessor:
    Preprocess the Notebook to remove the solution section and replace
    it with headings for solution parts.

"""

# Standard Library
from typing import TYPE_CHECKING, Tuple, List, Dict
import warnings

# Third-Party
from nbconvert.preprocessors import Preprocessor
from nbformat.v4 import new_code_cell, new_markdown_cell

if TYPE_CHECKING:
    from nbformat import NotebookNode  # noqa: F401 # typing only


by_hand_source = (
    "**Attach an image of your solution for this problem in this cell. "
    "Attach multiple images, one in each cell, if necessary. Please make "
    "sure the text is clear and legible.**"
)
by_hand_cell = new_markdown_cell(source=by_hand_source)

md_expl_source = (
    "**Write your engineering model, equations, and/or explanation of your process "
    "here.**"
)
md_expl_cell = new_markdown_cell(source=md_expl_source)

code_ans_source = (
    "# Write your code here to solve the problem\n"
    "# Make sure to write your final answer in the cell below."
)
code_ans_cell = new_code_cell(source=code_ans_source)

md_ans_source = """\
<div class="alert alert-success">

**Answer:**

</div>
"""
md_ans_cell = new_markdown_cell(source=md_ans_source)
md_ans_cell.metadata.deletable = False

sketch_source = "**Attach an image of your sketch for this problem in this cell.**"
sketch_cell = new_markdown_cell(source=sketch_source)


class RawRemover(Preprocessor):  # type: ignore
    """Remove any raw cells from the Notebook."""

    def preprocess(
        self, nb: "NotebookNode", resources: Dict[str, Dict[str, bool]]
    ) -> Tuple["NotebookNode", Dict[str, Dict[str, bool]]]:
        """Remove any raw cells from the Notebook.

        By default, exclude raw cells from the output. Change this by including
        global_content_filter->include_raw = True in the resources dictionary.
        This preprocessor is necessary because the NotebookExporter doesn't
        include the exclude_raw config."""
        if not resources.get("global_content_filter", {}).get("include_raw", False):
            keep_cells = []
            for cell in nb.cells:
                if cell.cell_type != "raw":
                    keep_cells.append(cell)

            nb.cells = keep_cells

        return nb, resources


class SolutionRemover(Preprocessor):  # type: ignore
    """Preprocess a homework problem to remove the solution.

    This preprocessor produces output suitable for distribution to students as
    an assignment by removing the solution from the Notebook.

    The solution cells are found by tags attached to the cells. A cell tagged
    ``solution`` will start the Solution section. Following that, any cell
    tagged ``part`` will insert a solution prompt into the assignment. If the
    additional tag ``sketch`` is added, then a prompt for a sketch is inserted
    instead. Prior to the start of the Solution, all cells are kept.

    To enable the legacy processing behavior, described below, the
    resources->legacy key must be set to True. If no legacy key is present in
    resources, the default is assumed to be True for now. This will change in
    the future.

    The preprocessor looks for a cell with the header '## solution'
    (case-insensitive) in it, which delimits the beginning of the solution
    section. Then, for every cell after that, it checks for a level 3 header,
    which delimits the start of a section of the solution. All cells between the
    level 3 headers are replaced with cells that ask the students to write their
    code and explanation.

    The processing is only done if the resources->remove_solution key is True.
    """

    def preprocess(
        self, nb: "NotebookNode", resources: Dict[str, bool]
    ) -> Tuple["NotebookNode", Dict[str, bool]]:
        """Preprocess the entire notebook."""
        if "remove_solution" not in resources:
            raise KeyError("The resources dictionary must have a remove_solution key.")
        if not resources["remove_solution"]:
            return nb, resources

        if resources.get("legacy", True):
            warnings.warn(
                "The legacy behavior for finding solution cells will be removed in "
                "the future.",
                FutureWarning,
            )
            return self.legacy_parser(nb, resources)

        keep_cells: List["NotebookNode"] = []
        solution_started = False
        for cell in nb.cells:
            if "tags" in cell.metadata:
                tags = cell.metadata["tags"][:]
                del cell.metadata["tags"]
            else:
                tags = []
            if "solution" in tags:
                solution_started = True
                keep_cells.append(cell)
            elif "part" in tags:
                keep_cells.append(cell)
                if "sketch" in tags:
                    keep_cells.append(sketch_cell)
                elif resources["by_hand"]:
                    keep_cells.append(by_hand_cell)
                else:
                    keep_cells.append(md_expl_cell)
                    keep_cells.append(code_ans_cell)
                    keep_cells.append(md_ans_cell)
            else:
                if tags:
                    warnings.warn(f"Unknown tag value: {tags}", UserWarning)
                if not solution_started:
                    keep_cells.append(cell)

        nb.cells = keep_cells
        return nb, resources

    def legacy_parser(
        self, nb: "NotebookNode", resources: Dict[str, bool]
    ) -> Tuple["NotebookNode", Dict[str, bool]]:
        keep_cells_idx: List[int] = []
        for index, cell in enumerate(nb.cells):
            if "## solution" in cell.source.lower():
                keep_cells_idx.append(index)
            # The space at the end of the test string here is important
            elif len(keep_cells_idx) > 0 and cell.source.startswith("### "):
                keep_cells_idx.append(index)

        if len(keep_cells_idx) == 0:
            raise ValueError(
                "The Notebook must have a cell with the text '## solution' "
                "(case insensitive) in it."
            )

        keep_cells = nb.cells[: keep_cells_idx[0] + 1]
        if len(keep_cells_idx) == 1:
            if resources["by_hand"]:
                keep_cells.append(by_hand_cell)
            else:
                if "sketch" in nb.cells[keep_cells_idx[0]].source.lower():
                    keep_cells.append(sketch_cell)
                else:
                    keep_cells.append(md_expl_cell)
                    keep_cells.append(code_ans_cell)
                    keep_cells.append(md_ans_cell)
        else:
            for i in keep_cells_idx[1:]:
                keep_cells.append(nb.cells[i])
                if resources["by_hand"]:
                    keep_cells.append(by_hand_cell)
                else:
                    if "sketch" in nb.cells[i].source.lower():
                        keep_cells.append(sketch_cell)
                    else:
                        keep_cells.append(md_expl_cell)
                        keep_cells.append(code_ans_cell)
                        keep_cells.append(md_ans_cell)

        nb.cells = keep_cells
        return nb, resources
