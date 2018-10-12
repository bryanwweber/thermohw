"""
Convert a Jupyter Notebook format exam to the assignment and solution
notebooks and PDFs.
"""

# Standard Library
import os

# Third Party
from nbconvert import NotebookExporter, PDFExporter
from traitlets.config import Config

# Local imports
from .pymarkdown import PyMarkdownPreprocessor
from .preprocessors import ExamAssignmentPreprocessor
from .filters import convert_div, convert_raw_html

c = Config()
here = os.path.abspath(os.path.dirname(__file__))
c.PDFExporter.template_file = os.path.join(here, 'homework.tpl')
c.PDFExporter.filters = {'convert_div': convert_div, 'convert_raw_html': convert_raw_html}

assignment_nb_exp = NotebookExporter(
    preprocessors=[
        PyMarkdownPreprocessor,
        ExamAssignmentPreprocessor,
    ],
)

solution_pdf_exp = PDFExporter(
    preprocessors=[PyMarkdownPreprocessor],
    config=c,
)
solution_pdf_exp.writer.build_directory = '.'
