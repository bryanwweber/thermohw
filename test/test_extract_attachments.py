"""Test the extract_attachments preprocessor."""
from nbformat.v4 import new_markdown_cell
from binascii import a2b_base64

from thermohw import ExtractAttachmentsPreprocessor


preproc = ExtractAttachmentsPreprocessor()


def test_pathological_image_name() -> None:
    """Test that image name with escaped characters is converted properly."""
    fname = (
        "%28%29%40%23%24%25%5E%26%2A%21%3C%3E%3F%2C%7B%7D%5B%5D%5C%7C%7E%60%2B%3D%20"
    )
    repl = "-" * (len(fname) // 3)
    data = (
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB"
        "0C8AAAAASUVORK5CYII="
    )
    in_cell = new_markdown_cell(source=(f"![{fname}.png](attachment:{fname}.png)"))
    in_cell["attachments"] = {f"{fname}.png": {"image/png": data}}
    cell, resources = preproc.preprocess_cell(in_cell, {"outputs": {}}, 0)
    assert cell.source == f"![{fname}.png](_0_{repl}.png)"
    assert resources["outputs"][f"_0_{repl}.png"] == a2b_base64(data)
