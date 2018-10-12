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
from typing import TYPE_CHECKING, Tuple, List

# Third-Party
from nbconvert.preprocessors import Preprocessor
from nbformat.v4 import new_code_cell, new_markdown_cell

if TYPE_CHECKING:
    from nbformat import NotebookNode  # noqa: F401 # typing only


by_hand_source = ('**Attach an image of your solution for this problem in this cell. '
                  'Attach multiple images if necessary. Please make sure the text is '
                  'clear and legible.**')
by_hand_cell = new_markdown_cell(source=by_hand_source)

md_expl_source = ('**Write your engineering model, equations, and/or explanation of your process '
                  'here.**')
md_expl_cell = new_markdown_cell(source=md_expl_source)

code_ans_source = ('# Write your code here to solve the problem\n'
                   '# Make sure to write your final answer in the cell below.')
code_ans_cell = new_code_cell(source=code_ans_source)

md_ans_source = """\
<div class="alert alert-success">

**Answer:**

</div>
"""
md_ans_cell = new_markdown_cell(source=md_ans_source)

sketch_source = '**Attach an image of your sketch for this problem in this cell.**'
sketch_cell = new_markdown_cell(source=sketch_source)

exam_instructions_source = """\
---

## Instructions

You have 1.25 hours to complete the exam. When you are finished with the exam, you should download
a PDF of all of your Notebooks and upload it to Gradescope. You **_MUST_** upload the exam to
Gradescope before the end of your course period or **_IT WILL NOT BE ACCEPTED_**. Absolutely no
late exams will be accepted, no excuses, no BS. If you have any problems, contact me as soon as you
run into trouble.

Complete all of the questions below. Short answer questions should be answered in the indicated
Markdown cell immediately below the question statement, and can generally be answered in 1-3
sentences. The answers to problem solving questions should be placed in the indicated Markdown
cells, which should be immediately below your work on that problem.

You may use your computer, calculator, textbook, homework problem solutions, JupyterHub/ThermoState,
or any websites to solve the problems. However, you may not copy the question text (or portions of
the text) into a search engine, and **you must work by yourself** to solve these problems.
Furthermore, my standard policy on academic integrity from the course syllabus applies (in addition
to the statement below)—All of the work that you hand in must be entirely your own; as one example,
you may not use answers to these questions that you find on the web directly, your answers must
represent your own work and your own understanding.

---

## Honesty and Academic Inegrity Statement

**Read the following statement and type your name in the cell below to indicate your acceptance
of and agreement with these policies**

I agree that I will not discuss, disclose, copy, reproduce, adapt, or transmit exam content orally,
in writing, on the Internet, or through any other medium prior to the distribution of the exam
solutions by the Instructor. I agree that I will (and have) worked entirely on my own for this exam
and the work below represents entirely my individual work and understanding. I understand that my
failure to follow the above guidelines will result in the consequences outlined in the syllabus
under the academic honesty and integrity policy, possibly including, but not limited to, a failing
grade on this exam.

---

## Type your name in the cell below
"""
exam_instructions_cell = new_markdown_cell(source=exam_instructions_source)


class HomeworkPreprocessor(Preprocessor):  # type: ignore
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

    def preprocess(self, nb: 'NotebookNode', resources: dict) -> Tuple['NotebookNode', dict]:
        """Preprocess the entire notebook."""
        # Use this loop to remove raw cells because the NotebookExporter
        # doesn't have the exclude_raw configurable option
        keep_cells = []
        for cell in nb.cells:
            if cell.cell_type != 'raw':
                keep_cells.append(cell)

        nb.cells = keep_cells
        for index, cell in enumerate(nb.cells):
            nb.cells[index], resources = self.preprocess_cell(cell, resources, index)
        return nb, resources

    def preprocess_cell(self, cell: 'NotebookNode',
                        resources: dict, index: int) -> Tuple['NotebookNode', dict]:
        """Preprocess each cell of the notebook."""
        if cell.cell_type != 'code':
            return cell, resources

        cell.execution_count = None

        if 'Image' in cell.source:
            source = """# Delete this cell before exporting to PDF"""
            cell.source = source
            return cell, resources

        if index == 1:
            final_source = []
            for l in cell.source.split('\n'):
                if '%matplotlib inline' in l or 'import matplotlib' in l:
                    final_source.append(l)
                elif 'units.define' in l:
                    final_source.append(l)
                elif 'from' not in l:
                    continue
                else:
                    final_source.append(l)

            cell.source = '\n'.join(final_source)
            return cell, resources

        return cell, resources


class SolnRemoverPreprocessor(Preprocessor):  # type: ignore
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

    def preprocess(self, nb: 'NotebookNode', resources: dict) -> Tuple['NotebookNode', dict]:
        """Preprocess the entire notebook."""
        keep_cells_idx = []
        for index, cell in enumerate(nb.cells):
            if 'solution' in cell.source.lower():
                keep_cells_idx.append(index)
            # The space at the end of the test string here is important
            elif len(keep_cells_idx) > 0 and cell.source.startswith('### '):
                keep_cells_idx.append(index)

        keep_cells = nb.cells[:keep_cells_idx[0] + 1]
        for i in keep_cells_idx[1:]:
            keep_cells.append(nb.cells[i])
            if resources['by_hand']:
                keep_cells.append(by_hand_cell)
            else:
                if 'sketch' in nb.cells[i].source.lower():
                    keep_cells.append(sketch_cell)
                else:
                    keep_cells.append(md_expl_cell)
                    keep_cells.append(code_ans_cell)
                    keep_cells.append(md_ans_cell)
        nb.cells = keep_cells
        return nb, resources


class ExamAssignmentPreprocessor(Preprocessor):  # type: ignore
    """Preprocess an exam Notebook into the assignment."""

    def preprocess(self, nb: 'NotebookNode', resources: dict) -> Tuple['NotebookNode', dict]:
        """Preprocess the entire Notebook."""
        keep_cells_idx: List[int] = []
        for index, cell in enumerate(nb.cells):
            if '### solution' in cell.source.lower():
                cell.source = '### Solution'
                if not keep_cells_idx:
                    keep_cells_idx.append(index)
            elif '#### ' in cell.source.lower():
                keep_cells_idx.append(index)

        # This will be true for the problem solving Notebooks
        if not len(keep_cells_idx) == 1:
            keep_cells = nb.cells[:keep_cells_idx[0] + 1]
            for i in keep_cells_idx[1:]:
                keep_cells.append(md_expl_cell)
                keep_cells.append(code_ans_cell)
                keep_cells.append(md_ans_cell)
            # This is deliberately inside the if statement so that it only runs
            # for problem solving Notebooks, not for the short answer
            nb.cells = keep_cells

        nb.cells.insert(1, exam_instructions_cell)
        nb.cells.insert(2, new_markdown_cell(source=''))

        return nb, resources
