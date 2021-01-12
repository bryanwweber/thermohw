"""
Convert a Jupyter Notebook-format homework problem.

The single input Jupyter Notebook is converted into four files:

- A Notebook without the solution for students to fill in
- A PDF without the solution for students to fill in
- A Notebook with the solution
- A PDF with the solution

The solution is detected as any cells below a Markdown cell with the phrase "##
solution" in the cell. Below the solution-delimiting cell, any Markdown cell
that starts with a level-three header (###) is retained as a divider between
sections of the solution.

Input files should be named according to the convention::

    homework-A-B.ipynb

where ``A`` is the homework number and ``B`` is the problem number of this input
file in the homework assignment.

Methods
-------
process(hw_num, problems_to_do=None, prefix=None): Process the files for
    homework number ``hw_num``. Only process the specific problems in the
    ``problems`` argument.

main(argv=None): Process the command line arguments and run the `process`
    function

"""
# Standard library
from typing import Iterable, Dict, Sequence, Optional, List, Any, Union
from pathlib import Path
from argparse import ArgumentParser
from zipfile import ZipFile
from io import BytesIO
from datetime import date
import shutil
import sys

# Third Party
from nbconvert import NotebookExporter, PDFExporter
from traitlets.config import Config
from nbconvert.writers import FilesWriter
import nbformat

# Local imports
from .extract_attachments import ExtractAttachmentsPreprocessor
from .pymarkdown import PyMarkdownPreprocessor
from .preprocessors import RawRemover, SolutionRemover
from .filters import convert_div, convert_raw_html
from .utils import combine_pdf_as_bytes

c = Config()
here = Path(__file__).resolve().parent
c.PDFExporter.template_file = str(here / "homework.tpl")
c.PDFExporter.filters = {
    "convert_div": convert_div,
    "convert_raw_html": convert_raw_html,
}
c.PDFExporter.latex_count = 1


nb_exp = NotebookExporter(
    preprocessors=[RawRemover, SolutionRemover, PyMarkdownPreprocessor]
)

pdf_exp = PDFExporter(
    preprocessors=[
        RawRemover,
        SolutionRemover,
        PyMarkdownPreprocessor,
        ExtractAttachmentsPreprocessor(config=c),
    ],
    config=c,
)
pdf_exp.writer.build_directory = "."


def process(
    hw_num: int,
    problems_to_do: Optional[Iterable[int]] = None,
    prefix: Optional[Path] = None,
    by_hand: Optional[Iterable[int]] = None,
    legacy: bool = False,
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
    legacy, optional
        A boolean flag determining whether the legacy method of finding
        solutions will be used, based on parsing cell content.
    """
    if prefix is None:
        prefix = Path(".")

    problems: Iterable[Path]

    if problems_to_do is None:
        # The glob syntax here means a the filename must start with
        # homework-, be followed the homework number, followed by a
        # dash, then a digit representing the problem number for this
        # homework number, then any number of characters (in practice
        # either nothing or, rarely, another digit), then the ipynb
        # extension. Examples:
        # homework-1-1.ipynb, homework-10-1.ipynb, homework-3-10.ipynb
        problems = list(prefix.glob(f"homework-{hw_num}-[0-9]*.ipynb"))
    else:
        problems = [prefix / f"homework-{hw_num}-{i}.ipynb" for i in problems_to_do]

    problems = sorted(problems, key=lambda k: k.stem[-1])

    output_directory: Path = (prefix / "output").resolve()
    fw = FilesWriter(build_directory=str(output_directory))

    assignment_zip_name = output_directory / f"homework-{hw_num}.zip"
    solution_zip_name = output_directory / f"homework-{hw_num}-soln.zip"

    assignment_pdfs: List[BytesIO] = []
    solution_pdfs: List[BytesIO] = []

    assignment_pdf: bytes
    solution_pdf: bytes
    assignment_nb: str
    solution_nb: str

    res: Dict[str, Union[Dict[str, bool], str, bool]] = {
        "delete_pymarkdown": True,
        "global_content_filter": {"include_raw": False},
        "legacy": legacy,
    }

    for problem in problems:
        print("Working on:", problem)
        res["unique_key"] = problem.stem
        problem_number = int(problem.stem.split("-")[-1])
        if by_hand is not None and problem_number in by_hand:
            res["by_hand"] = True
        else:
            res["by_hand"] = False
        problem_fname = str(problem.resolve())
        problem_nb = nbformat.read(problem_fname, as_version=4)
        if "celltoolbar" in problem_nb.metadata:
            del problem_nb.metadata["celltoolbar"]

        # Process assignments
        res["remove_solution"] = True
        assignment_pdf, _ = pdf_exp.from_notebook_node(problem_nb, resources=res)
        assignment_pdfs.append(BytesIO(assignment_pdf))

        assignment_nb, _ = nb_exp.from_notebook_node(problem_nb, resources=res)
        with ZipFile(assignment_zip_name, mode="a") as zip_file:
            zip_file.writestr(problem.name, assignment_nb)

        # Process solutions
        res["remove_solution"] = False
        solution_pdf, _ = pdf_exp.from_notebook_node(problem_nb, resources=res)
        solution_pdfs.append(BytesIO(solution_pdf))

        solution_nb, _ = nb_exp.from_notebook_node(problem_nb, resources=res)
        with ZipFile(solution_zip_name, mode="a") as zip_file:
            zip_file.writestr(problem.stem + "-soln" + problem.suffix, solution_nb)

    resources: Dict[str, Any] = {
        "metadata": {
            "name": f"homework-{hw_num}",
            "path": str(prefix),
            "modified_date": date.today().strftime("%B %d, %Y"),
        },
        "output_extension": ".pdf",
    }
    fw.write(combine_pdf_as_bytes(assignment_pdfs), resources, f"homework-{hw_num}")

    resources["metadata"]["name"] = f"homework-{hw_num}-soln"
    fw.write(combine_pdf_as_bytes(solution_pdfs), resources, f"homework-{hw_num}-soln")


def main(argv: Optional[Sequence[str]] = None) -> None:
    """Parse arguments and process the homework assignment."""
    parser = ArgumentParser(description="Convert Jupyter Notebook assignments to PDFs")
    parser.add_argument(
        "--hw",
        type=int,
        required=True,
        help="Homework number to convert",
        dest="hw_num",
    )
    parser.add_argument(
        "-p",
        "--problems",
        type=int,
        help="Problem numbers to convert",
        dest="problems",
        nargs="*",
    )
    parser.add_argument(
        "--by-hand",
        type=int,
        help="Problem numbers to be completed by hand",
        dest="by_hand",
        nargs="*",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help=(
            "Remove the output folder. If --problems is passed, the specified"
            "problems will be processed. Otherwise, will exit after cleaning."
        ),
    )
    parser.add_argument(
        "--legacy",
        action="store_true",
        help=(
            "Enable legacy behavior for finding solution cells, based on "
            "finding specific cell content."
        ),
    )
    args = parser.parse_args(argv)
    prefix = Path(f"homework/homework-{args.hw_num}")
    if args.clean:
        shutil.rmtree(prefix.joinpath("output"), ignore_errors=True)
        if not args.problems:
            sys.exit(0)

    process(
        args.hw_num,
        args.problems,
        prefix=prefix,
        by_hand=args.by_hand,
        legacy=args.legacy,
    )


if __name__ == "__main__":
    main()
