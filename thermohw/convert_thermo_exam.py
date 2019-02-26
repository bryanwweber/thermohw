"""
Convert a Jupyter Notebook format exam to the assignment and solution
notebooks and PDFs.
"""

# Standard Library
import os
from pathlib import Path
from typing import Dict, Optional, Sequence, Union, List, Any
from zipfile import ZipFile
from argparse import ArgumentParser
from datetime import datetime
from io import BytesIO

# Third Party
from nbconvert import NotebookExporter, PDFExporter
from traitlets.config import Config
from nbconvert.writers import FilesWriter

# Local imports
from .pymarkdown import PyMarkdownPreprocessor
from .preprocessors import ExamSAPreprocessor, ExamInstructionsPreprocessor
from .extract_attachments import ExtractAttachmentsPreprocessor
from .preprocessors import SolutionRemover
from .filters import convert_div, convert_raw_html
from .utils import combine_pdf_as_bytes

c = Config()
here = os.path.abspath(os.path.dirname(__file__))
c.PDFExporter.template_file = os.path.join(here, "homework.tpl")
c.PDFExporter.filters = {
    "convert_div": convert_div,
    "convert_raw_html": convert_raw_html,
}
c.PDFExporter.latex_count = 1


sa_nb_exp = NotebookExporter(
    preprocessors=[
        PyMarkdownPreprocessor,
        ExamSAPreprocessor,
        ExamInstructionsPreprocessor,
    ]
)

prob_nb_exp = NotebookExporter(
    preprocessors=[
        PyMarkdownPreprocessor,
        SolutionRemover,
        ExamInstructionsPreprocessor,
    ]
)

solution_nb_exp = NotebookExporter(preprocessors=[PyMarkdownPreprocessor])

solution_pdf_exp = PDFExporter(
    preprocessors=[PyMarkdownPreprocessor, ExtractAttachmentsPreprocessor(config=c)],
    config=c,
)
solution_pdf_exp.writer.build_directory = "."


def process(exam_num: int, time: str, date: str) -> None:
    """Process the exams in the exam_num folder for the time."""
    prefix = Path(f"exams/exam-{exam_num}")

    problems = list(prefix.glob(f"exam-{exam_num}-{time}-[0-9].ipynb"))
    problems = sorted(problems, key=lambda k: k.stem[-1])

    output_directory = (prefix / "output").resolve()
    fw = FilesWriter(build_directory=str(output_directory))

    assignment_zip_name = output_directory / f"exam-{exam_num}-{time}.zip"
    solution_zip_name = output_directory / f"exam-{exam_num}-{time}-soln.zip"

    solution_pdfs: List[BytesIO] = []

    exam_date_time = datetime.strptime(time + date, "%H%M%d-%b-%Y")
    res: Dict[str, Union[str, int]] = {
        "exam_num": exam_num,
        "time": exam_date_time.strftime("%I:%M %p"),
        "date": exam_date_time.strftime("%b. %d, %Y"),
        "delete_pymarkdown": True,
    }

    for problem in problems:
        res["unique_key"] = problem.stem
        problem_fname = str(problem.resolve())
        if problem.stem.endswith("1"):

            assignment_nb, _ = sa_nb_exp.from_filename(problem_fname, resources=res)

            with ZipFile(assignment_zip_name, mode="a") as zip_file:
                zip_file.writestr(problem.name, assignment_nb)
        else:
            assignment_nb, _ = prob_nb_exp.from_filename(problem_fname, resources=res)

            with ZipFile(assignment_zip_name, mode="a") as zip_file:
                zip_file.writestr(problem.name, assignment_nb)

        solution_pdf, _ = solution_pdf_exp.from_filename(problem_fname, resources=res)
        solution_pdfs.append(BytesIO(solution_pdf))

        solution_nb, _ = solution_nb_exp.from_filename(problem_fname, resources=res)
        with ZipFile(solution_zip_name, mode="a") as zip_file:
            zip_file.writestr(problem.name, solution_nb)

    resources: Dict[str, Any] = {
        "metadata": {
            "name": f"exam-{exam_num}-{time}-soln",
            "path": str(prefix),
            "modified_date": datetime.today().strftime("%B %d, %Y"),
        },
        "output_extension": ".pdf",
    }
    fw.write(
        combine_pdf_as_bytes(solution_pdfs), resources, f"exam-{exam_num}-{time}-soln"
    )


def main(argv: Optional[Sequence[str]] = None) -> None:
    """Parse arguments and process the exam assignment."""
    parser = ArgumentParser(description="Convert Jupyter Notebook exams to PDFs")
    parser.add_argument(
        "--exam",
        type=int,
        required=True,
        help="Exam number to convert",
        dest="exam_num",
    )
    parser.add_argument(
        "--time", type=str, required=True, help="Time of exam to convert"
    )
    parser.add_argument(
        "--date", type=str, required=True, help="The date the exam will take place"
    )
    args = parser.parse_args(argv)
    process(args.exam_num, args.time, args.date)


if __name__ == "__main__":
    main()
