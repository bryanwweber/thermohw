"""
Convert a Jupyter Notebook-format homework problem.

The single input Jupyter Notebook is converted into four files:

- A Notebook without the solution for students to fill in
- A PDF without the solution for students to fill in
- A Notebook with the solution
- A PDF with the solution

The second cell of the input Notebook must contain any imports required
to run the problem as well as definitions that should not be shown to
the students, either in the problem or the solution. This cell is
processed so that only imports with ``from`` and matplotlib imports
remain.

The solution is detected as any cells below a Markdown cell with the
word "solution" in the cell. Below the solution-delimiting cell, any
Markdown cell with a level-three header (###) is retained as a divider
between sections of the solution.

Input files should be named according to the convention::

    homwork-A-B.ipynb

where ``A`` is the homework number and ``B`` is the problem number of
this input file in the homework assignment.

Methods
-------
process(hw_num, problems=None, prefix=None): Process the files for
    homework number ``hw_num``. Only process the specific problems
    in the ``problems`` argument.

main(argv=None): Process the command line arguments and run the
    `process` function

"""
# Standard library
from typing import Iterable, Dict, Sequence, Optional, List, Any
import os
import copy
from pathlib import Path
from argparse import ArgumentParser
from zipfile import ZipFile
from io import BytesIO
from datetime import date

# Third Party
from nbconvert import NotebookExporter, PDFExporter  # type: ignore
from nbconvert.preprocessors import Preprocessor, ExtractOutputPreprocessor  # type: ignore
from traitlets.config import Config  # type: ignore
from nbconvert.writers import FilesWriter  # type: ignore
from pdfrw import PdfReader, PdfWriter  # type: ignore

# Local imports
from .extract_attachments import ExtractAttachmentsPreprocessor

c = Config()
c.ExtractOutputPreprocessor.output_filename_template = "{unique_key}_{cell_index}_{index}"

here = os.path.abspath(os.path.dirname(__file__))
c.PDFExporter.template_file = os.path.join(here, 'homework.tpl')


def combine_pdf_as_bytes(pdfs: List[BytesIO]):
    """Combine PDFs and return a bytestring with the result.

    Arguments
    ---------
    pdfs
        A list of BytesIO representations of PDFs

    """
    writer = PdfWriter()
    for pdf in pdfs:
        writer.addpages(PdfReader(pdf).pages)
    bio = BytesIO()
    writer.write(bio)
    bio.seek(0)
    output = bio.read()
    bio.close()
    return output


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


assignment_nb_exp = NotebookExporter(
    preprocessors=[HomeworkPreprocessor,
                   SolnRemoverPreprocessor,
                   'jupyter_contrib_nbextensions.nbconvert_support.PyMarkdownPreprocessor',
                   ExtractOutputPreprocessor(config=c)],
)

solution_nb_exp = NotebookExporter(
    preprocessors=[HomeworkPreprocessor,
                   'jupyter_contrib_nbextensions.nbconvert_support.PyMarkdownPreprocessor',
                   ExtractOutputPreprocessor(config=c)],
)

assignment_pdf_exp = PDFExporter(
    preprocessors=[HomeworkPreprocessor,
                   SolnRemoverPreprocessor,
                   'jupyter_contrib_nbextensions.nbconvert_support.PyMarkdownPreprocessor',
                   ExtractAttachmentsPreprocessor(config=c),
                   ExtractOutputPreprocessor(config=c)],
    config=c,
)
assignment_pdf_exp.writer.build_directory = '.'

solution_pdf_exp = PDFExporter(
    preprocessors=[HomeworkPreprocessor,
                   'jupyter_contrib_nbextensions.nbconvert_support.PyMarkdownPreprocessor',
                   ExtractAttachmentsPreprocessor(config=c),
                   ExtractOutputPreprocessor(config=c)],
    config=c,
)
solution_pdf_exp.writer.build_directory = '.'


def process(hw_num: int,
            problems_to_do: Optional[Iterable[int]] = None,
            prefix: Optional[Path] = None,
            ) -> None:
    """Process the homework problems in ``prefix`` folder.

    Arguments
    ---------
    hw_num
        The number of this homework
    problems_to_do, optional
        A list of the problems to be processed
    prefix, optional
        A `~pathlib.Path` to this homework assignment folder

    """
    if prefix is None:
        prefix = Path('.')

    problems: Iterable[Path]

    if problems_to_do is None:
        # The glob syntax here means a the filename must start with
        # homework-, be followed the homework number, followed by a
        # dash, then a digit representing the problem number for this
        # homework number, then any number of characters (in practice
        # either nothing or, rarely, another digit), then the ipynb
        # extension. Examples:
        # homework-1-1.ipynb, homework-10-1.ipynb, homework-3-10.ipynb
        problems = list(prefix.glob(f'homework-{hw_num}-[0-9]*.ipynb'))
    else:
        problems = [prefix/f'homework-{hw_num}-{i}.ipynb' for i in problems_to_do]

    problems = sorted(problems, key=lambda k: k.stem[-1])

    output_directory: Path = (prefix/'output').resolve()
    fw = FilesWriter(build_directory=str(output_directory))

    assignment_zip_name = output_directory/f'homework-{hw_num}.zip'
    solution_zip_name = output_directory/f'homework-{hw_num}-soln.zip'

    assignment_pdfs: List[BytesIO] = []
    solution_pdfs: List[BytesIO] = []

    for problem in problems:
        print('Working on: ', problem)
        res: Dict[str, str] = {'unique_key': problem.stem}
        problem_fname = str(problem.resolve())

        assignment_pdf, _ = assignment_pdf_exp.from_filename(problem_fname, resources=res)
        assignment_pdfs.append(BytesIO(assignment_pdf))

        solution_pdf, _ = solution_pdf_exp.from_filename(problem_fname, resources=res)
        solution_pdfs.append(BytesIO(solution_pdf))

        assignment_nb, _ = assignment_nb_exp.from_filename(problem_fname, resources=res)

        with ZipFile(assignment_zip_name, mode='a') as zip_file:  # type: ignore
            zip_file.writestr(problem.name, assignment_nb)

        solution_nb, _ = solution_nb_exp.from_filename(problem_fname, resources=res)

        with ZipFile(solution_zip_name, mode='a') as zip_file:  # type: ignore
            zip_file.writestr(problem.stem + '-soln' + problem.suffix, solution_nb)

    resources: Dict[str, Any] = {
        'metadata': {
            'name': f'homework-{hw_num}',
            'path': str(prefix),
            'modified_date': date.today().strftime('%B %d, %Y'),
        },
        'output_extension': '.pdf',
    }
    fw.write(combine_pdf_as_bytes(assignment_pdfs), resources, f'homework-{hw_num}')

    resources['metadata']['name'] = f'homework-{hw_num}-soln'
    fw.write(combine_pdf_as_bytes(solution_pdfs), resources, f'homework-{hw_num}-soln')


def main(argv: Optional[Sequence[str]] = None) -> None:
    """Parse arguments and process the homework assignment."""
    parser: ArgumentParser = ArgumentParser(
        description="Convert Jupyter Notebook assignments to PDFs",
    )
    parser.add_argument('--hw', type=int, required=True, help="Homework number to convert",
                        dest='hw_num')
    parser.add_argument('-p', '--problems', type=int,
                        help="Problem numbers to convert",
                        dest='problems',
                        nargs='*')
    args = parser.parse_args(argv)
    process(args.hw_num, args.problems, prefix=Path('homework/homework-{}'.format(args.hw_num)))


if __name__ == '__main__':
    main()
