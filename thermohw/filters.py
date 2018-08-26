"""Convert divs with alert classes to equivalent LaTeX environments.

This module uses the JSON output format from Pandoc to look for ``Div``
elements (which are the Pandoc AST representation of ``div`` elements)
and convert them to a LaTeX environment with the appropriate name.
"""

from pandocfilters import applyJSONFilters, RawBlock, RawInline

# Allowed alert types are all from the Bootstrap alert types
# https://getbootstrap.com/docs/4.1/components/alerts/
ALLOWED_ALERT_TYPES = [
    'success',
    'primary',
    'secondary',
    'warning',
    'danger',
    'info',
]


def div_filter(key, value, format, meta):
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
    if key != 'Div' or format != 'latex':
        return None

    [[_, classes, _], contents] = value
    try:
        alert_type = [cls.split('-')[1] for cls in classes if '-' in cls][0]
    except IndexError:
        return None

    if alert_type not in ALLOWED_ALERT_TYPES:
        return None

    filtered = [RawBlock('latex', rf'\begin{{{alert_type}box}}')]
    filtered.extend(contents)
    filtered.append(RawBlock('latex', rf'\end{{{alert_type}box}}'))
    return filtered


def convert_div(text, format=None):
    """Apply the `dev_filter` action to the text."""
    return applyJSONFilters([div_filter], text, format=format)


def raw_html_filter(key, value, format, meta):
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
    if key == 'RawInline' and format == 'latex' and value[0] == 'html':
        if value[1] == '<sup>':
            filtered = [RawInline('latex', r'\textsuperscript{')]
        elif value[1] == '</sup>':
            filtered = [RawInline('latex', '}')]
        elif value[1] == '<sub>':
            filtered = [RawInline('latex', r'\textsubscript{')]
        elif value[1] == '</sub>':
            filtered = [RawInline('latex', '}')]
        else:
            return None
        return filtered

    return None


def convert_raw_html(text, format=None):
    """Apply the `raw_html_filter` action to the text."""
    return applyJSONFilters([raw_html_filter], text, format=format)
