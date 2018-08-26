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
process(hw_num, problems_to_do=None, prefix=None): Process the files
    for homework number ``hw_num``. Only process the specific problems
    in the ``problems`` argument.

main(argv=None): Process the command line arguments and run the
    `process` function

"""
# Standard library
from typing import Iterable, Dict, Sequence, Optional, List, Any
import os
from pathlib import Path
from argparse import ArgumentParser
from zipfile import ZipFile
from io import BytesIO
from datetime import date

# Third Party
from nbconvert import NotebookExporter, PDFExporter  # type: ignore
from traitlets.config import Config  # type: ignore
from nbconvert.writers import FilesWriter  # type: ignore
from pdfrw import PdfReader, PdfWriter  # type: ignore

# Local imports
from .extract_attachments import ExtractAttachmentsPreprocessor
from .pymarkdown import PyMarkdownPreprocessor
from .preprocessors import HomeworkPreprocessor, SolnRemoverPreprocessor
from .filters import convert_div, convert_raw_html

c = Config()
here = os.path.abspath(os.path.dirname(__file__))
c.PDFExporter.template_file = os.path.join(here, 'homework.tpl')
c.PDFExporter.filters = {'convert_div': convert_div, 'convert_raw_html': convert_raw_html}


def combine_pdf_as_bytes(pdfs: List[BytesIO]) -> bytes:
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


assignment_nb_exp = NotebookExporter(
    preprocessors=[
        HomeworkPreprocessor,
        SolnRemoverPreprocessor,
        PyMarkdownPreprocessor,
    ],
)

solution_nb_exp = NotebookExporter(
    preprocessors=[
        HomeworkPreprocessor,
        PyMarkdownPreprocessor,
    ],
)

assignment_pdf_exp = PDFExporter(
    preprocessors=[
        HomeworkPreprocessor,
        SolnRemoverPreprocessor,
        PyMarkdownPreprocessor,
        ExtractAttachmentsPreprocessor(config=c),
    ],
    config=c,
)
assignment_pdf_exp.writer.build_directory = '.'

solution_pdf_exp = PDFExporter(
    preprocessors=[
        HomeworkPreprocessor,
        PyMarkdownPreprocessor,
        ExtractAttachmentsPreprocessor(config=c),
    ],
    config=c,
)
solution_pdf_exp.writer.build_directory = '.'


def process(hw_num: int,
            problems_to_do: Optional[Iterable[int]] = None,
            prefix: Optional[Path] = None,
            by_hand: Optional[Iterable[int]] = None,
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
    by_hand, optional
        A list of the problems that should be labeled to be completed
        by hand and have an image with the solution included.

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

    assignment_pdf: bytes
    solution_pdf: bytes
    assignment_nb: str
    solution_nb: str

    for problem in problems:
        print('Working on: ', problem)
        res: Dict[str, str] = {'unique_key': problem.stem}
        problem_number = int(problem.stem.split('-')[-1])
        if by_hand is not None and problem_number in by_hand:
            res['by_hand'] = True
        else:
            res['by_hand'] = False
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
    parser = ArgumentParser(
        description="Convert Jupyter Notebook assignments to PDFs",
    )
    parser.add_argument('--hw', type=int, required=True, help="Homework number to convert",
                        dest='hw_num')
    parser.add_argument('-p', '--problems', type=int,
                        help="Problem numbers to convert",
                        dest='problems',
                        nargs='*')
    parser.add_argument('--by-hand', type=int,
                        help="Problem numbers to be completed by hand",
                        dest='by_hand',
                        nargs='*')
    args = parser.parse_args(argv)
    prefix = Path(f'homework/homework-{args.hw_num}')
    process(args.hw_num, args.problems, prefix=prefix, by_hand=args.by_hand)


if __name__ == '__main__':
    main()
