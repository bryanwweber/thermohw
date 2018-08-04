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
import copy

# Third-Party
from nbconvert.preprocessors import Preprocessor  # type: ignore


class HomeworkPreprocessor(Preprocessor):
    """Preprocess a homework problem to turn it into an assignment.

    This preprocessor produces output suitable for distribution to
    students as an assignment. It has three main tasks:

    1. Remove any raw cells from the output entirely
    2. If images are displayed by the ``Image`` display class, remove
       that line and replace it with a note that the cell should be
       deleted before being saved to PDF. This is to avoid issues with
       images in the nbconvert conversion process.
    3. Remove any lines from the second cell of the Notebook that are
       for the instructor use. Lines that are retained are any
       ``from ... import ...`` lines and any lines with ``matplotlib``
       import related bits.
    """

    def preprocess(self, nb, resources):
        """Preprocess the entire notebook."""
        keep_cells = []
        for cell in nb.cells:
            if cell.cell_type != 'raw':
                keep_cells.append(cell)

        nb.cells = keep_cells
        for index, cell in enumerate(nb.cells):
            nb.cells[index], resources = self.preprocess_cell(cell, resources, index)
        return nb, resources

    def preprocess_cell(self, cell, resources, index):
        """Preprocess each cell of the notebook."""
        if cell.cell_type != 'code':
            return cell, resources

        if 'Image' in cell.source:
            source = """# Delete this cell before exporting to PDF"""
            cell.source = source
            cell.execution_count = None
            return cell, resources

        if index == 1:
            final_source = []
            for l in cell.source.split('\n'):
                if '%matplotlib inline' in l or 'import matplotlib' in l:
                    final_source.append(l)
                elif 'from' not in l:
                    continue
                else:
                    final_source.append(l)

            cell.source = '\n'.join(final_source)
            cell.execution_count = None
            return cell, resources

        return cell, resources


class SolnRemoverPreprocessor(Preprocessor):
    """Preprocess a homework problem to remove the solution.

    This preprocessor produces output suitable for distribution to
    students as an assignment. It has one task: remove the solution
    from the Notebook. The preprocessor looks for a cell with the word
    'solution' in it, which delimits the beginning of the solution
    section. Then, for every cell after that, it checks for a level 3
    header, which delimits the start of a section of the solution, for
    multi-part problems. All cells between the level 3 headers are
    replaced with a single code cell that asks the students to write
    their code and explanation there.
    """

    def preprocess(self, nb, resources):
        """Preprocess the entire notebook."""
        keep_cells_idx = []
        for index, cell in enumerate(nb.cells):
            if 'solution' in cell.source.lower():
                keep_cells_idx.append(index)
            # The space at the end of the test string here is important
            elif len(keep_cells_idx) > 0 and cell.source.startswith('### '):
                keep_cells_idx.append(index)

        code_cell = copy.deepcopy(nb.cells[1])
        code_cell.execution_count = None
        code_cell.source = ('# Write your code and explanation here to solve the problem\n'
                            '# Make sure to print your final answer')

        keep_cells = nb.cells[:keep_cells_idx[0] + 1]
        for i in keep_cells_idx[1:]:
            keep_cells.append(nb.cells[i])
            keep_cells.append(code_cell)
        nb.cells = keep_cells
        return nb, resources
