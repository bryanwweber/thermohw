import os

from ..convert_thermo_hw import solution_pdf_exp

here = os.path.dirname(__file__)


def test_convert_pathological_image_name():
    print(here)
    res = {'unique_key': 'test-pathological-image-name', 'by_hand': False}
    solution_pdf, _ = solution_pdf_exp.from_filename(
        os.path.join(here, 'test-pathological-image-name.ipynb'),
        res,
    )
    assert len(solution_pdf) > 0
