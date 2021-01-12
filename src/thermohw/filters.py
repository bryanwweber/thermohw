"""Convert divs with alert classes to equivalent LaTeX environments.

This module uses the JSON output format from Pandoc to look for ``Div``
elements (which are the Pandoc AST representation of ``div`` elements)
and convert them to a LaTeX environment with the appropriate name.
"""

from enum import Enum, auto
from typing import Any, Optional

from pandocfilters import applyJSONFilters, RawBlock, RawInline


# Allowed alert types are all from the Bootstrap alert types
# https://getbootstrap.com/docs/4.1/components/alerts/
class ALLOWED_ALERT_TYPES(Enum):
    success = auto()
    primary = auto()
    secondary = auto()
    warning = auto()
    danger = auto()
    info = auto()


def div_filter(key: str, value: list, format: str, meta: Any) -> Optional[list]:
    """Filter the JSON ``value`` for alert divs.

    Arguments
    ---------
    key
        Key of the structure
    value
        Values in the structure
    format
        Output format of the processing
    meta
        Meta information
    """
    if key != "Div" or format != "latex":
        return None

    [[_, classes, _], contents] = value
    try:
        alert_type = [name.split("-")[1] for name in classes if "-" in name][0]
    except IndexError:
        return None

    if alert_type not in ALLOWED_ALERT_TYPES.__members__:
        return None

    filtered = [RawBlock("latex", rf"\begin{{{alert_type}box}}")]
    filtered.extend(contents)
    filtered.append(RawBlock("latex", rf"\end{{{alert_type}box}}"))
    return filtered


def convert_div(text: str, format: Optional[str] = None) -> "applyJSONFilters":
    """Apply the `div_filter` action to the text."""
    return applyJSONFilters([div_filter], text, format=format)


def raw_html_filter(key: str, value: list, format: str, meta: Any) -> Optional[list]:
    """Filter the JSON ``value`` for raw html to convert to LaTeX.

    Arguments
    ---------
    key
        Key of the structure
    value
        Values in the structure
    format
        Output format of the processing
    meta
        Meta information
    """
    if key == "RawInline" and format == "latex" and value[0] == "html":
        if value[1] == "<sup>":
            filtered = [RawInline("latex", r"\textsuperscript{")]
        elif value[1] == "</sup>":
            filtered = [RawInline("latex", "}")]
        elif value[1] == "<sub>":
            filtered = [RawInline("latex", r"\textsubscript{")]
        elif value[1] == "</sub>":
            filtered = [RawInline("latex", "}")]
        else:
            return None
        return filtered

    return None


def convert_raw_html(text: str, format: Optional[str] = None) -> "applyJSONFilters":
    """Apply the `raw_html_filter` action to the text."""
    return applyJSONFilters([raw_html_filter], text, format=format)
