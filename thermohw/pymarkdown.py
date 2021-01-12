"""Nbconvert preprocessor for the python-markdown nbextension.

This module is copied from the ipython-contrib/jupyter_contrib_nbextensions
package. The original source of the module is available at

https://github.com/ipython-contrib/jupyter_contrib_nbextensions/blob/master/src/jupyter_contrib_nbextensions/nbconvert_support/pre_pymarkdown.py

The jupyter_contrib_nbextensions package is licensed as follows:

====================================
 The IPython-contrib licensing terms
====================================

IPython-contrib is licensed under the terms of the Modified BSD License (also
known as New or Revised or 3-Clause BSD), as follows:

- Copyright (c) 2013-2015, IPython-contrib Developers

All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

Redistributions of source code must retain the above copyright notice, this
list of conditions and the following disclaimer.

Redistributions in binary form must reproduce the above copyright notice, this
list of conditions and the following disclaimer in the documentation and/or
other materials provided with the distribution.

Neither the name of the IPython-contrib Developers nor the names of its
contributors may be used to endorse or promote products derived from this
software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

from typing import TYPE_CHECKING, Tuple, Dict
import re

from nbconvert.preprocessors import Preprocessor

if TYPE_CHECKING:
    from nbformat import NotebookNode  # noqa: F401 # typing only import


class PyMarkdownPreprocessor(Preprocessor):  # type: ignore
    """
    :mod:`nbconvert` Preprocessor for the python-markdown nbextension.

    This :class:`~nbconvert.preprocessors.Preprocessor` replaces kernel code in
    markdown cells with the results stored in the cell metadata.
    """

    def replace_variables(self, source: str, variables: Dict[str, str]) -> str:
        """Replace {{variable-name}} with stored value."""
        try:
            replaced = re.sub(
                "{{(.*?)}}", lambda m: variables.get(m.group(1), ""), source
            )
        except TypeError:
            replaced = source
        return replaced

    def preprocess_cell(
        self, cell: "NotebookNode", resources: Dict[str, bool], index: int
    ) -> Tuple["NotebookNode", Dict[str, bool]]:
        """Preprocess cell.

        Parameters
        ----------
        cell : NotebookNode cell
            Notebook cell being processed
        resources : dictionary
            Additional resources used in the conversion process. Allows
            preprocessors to pass variables into the Jinja engine.
        cell_index : int
            Index of the cell being processed (see base.py)

        """
        if cell.cell_type == "markdown":
            variables = cell["metadata"].get("variables", {})
            if len(variables) > 0:
                cell.source = self.replace_variables(cell.source, variables)
                if resources.get("delete_pymarkdown", False):
                    del cell.metadata["variables"]
        return cell, resources
