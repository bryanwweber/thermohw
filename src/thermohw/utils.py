"""
Utility functions for the converters.
"""

# Standard Library
from typing import List
from io import BytesIO

# Third-Party
from pdfrw import PdfReader, PdfWriter


def combine_pdf_as_bytes(pdfs: List[BytesIO]) -> bytes:
    """Combine PDFs and return a byte-string with the result.

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
