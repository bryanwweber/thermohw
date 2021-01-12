# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

<!-- markdownlint-disable MD022 MD024 MD032 -->

## [0.7.0] - 2021-JAN-12
### Added
- The `SolutionRemover` preprocessor now uses cell tags to find the solution and its parts
- A `legacy` command line argument switches back to the old method of finding the solution based on parsing the source of the cell
- A test of the new tag-based `SolutionRemover`

### Changed
- Highlighted answer cells cannot be deleted in the assignment notebook
- Support for Python 3.6 is dropped
- Moved to `src` directory layout and don't include tests with the package

### Fixed
- Type hinting for `resources` dictionaries in some preprocessors

### Removed
- Remove exam processing, which didn't work well and wasn't really used

## [0.6.0] - 2020-SEP-11
### Added
- Option to clean the output folder can be specified.
- Test with the latest Python 3.9

### Changed
- Change base template for our template to `style_jupyter` instead of `style_ipython`. Has a number of benefits, most notably, line breaking in code cells.

### Fixed
- Fix uploading the Anaconda package

## [0.5.2] - 2020-SEP-03
### Changed
- Switch to GitHub Actions

## [0.5.1] - 2020-SEP-03
### Fixed
- The version number was incorrect for v0.5.0
- Tests!

## [0.5.0] - 2020-SEP-03
### Added
- Add ability to process exam files into assignments and solutions
- Cells that contain the word "Sketch" indicate that they require an image submission

### Changed
- Run Black on all the code files
- Delete Pymarkdown variables from the cell metadata to avoid revealing the solutions
- Move `combine_pdf_as_bytes()` to `utils.py`
- Only run `xelatex` on the converted files once

### Fixed
- Files without `### part name` now correctly excludes the solution

### Removed
- The `HomeworkPreprocessor` class was no longer useful, because it was removing things it shouldn't have been

## [0.4.2] - 2018-SEP-03
### Added
- Test suite started, with a test of the `ExtractOutputsPreprocessor` that checks pathological filenames
- Run test suite on TravisCI

### Changed
- Distribute the LICENSE file with built artifacts

### Fixed
- Fix pathological image filenames that caused URL escaping errors

## [0.4.1] - 2018-AUG-30
### Fixed
- Fix spaces in attached image names cause LaTeX to fail

## [0.4.0] - 2018-AUG-26
### Added
- `raw_html_filter` to process raw inline HTML to equivalent LaTeX forms
- Option to show the solution should be done by hand, `--by-hand` command line option

### Changed
- Reset all cell executions to be None when a Notebook is processed

## [0.3.1] - 2018-AUG-14
### Added
- Expose filter functions from `div_filter.py` in `__init__.py`

## [0.3.0] - 2018-AUG-14
### Added
- Add filter to convert [Bootstrap `alert-*`](https://getbootstrap.com/docs/4.1/components/alerts/) classes to LaTeX `tcolorbox`es

## [0.2.5] - 2018-AUG-03
### Added
- `setup.cfg` file added to configure some metadata
- Add `flake8` configuration to `setup.cfg`
- More keywords to `setup` function in `setup.py`
- Module docstring for the new `preprocessors` module
- Export more classes and functions from `__init__.py`

### Changed
- The `HomeworkPreprocessor` and `SolnRemoverPreprocessor` are moved from `convert_thermo_hw` module to `preprocessors` module

### Fixed
- Fix some typing errors

### Removed
- Remove the `ExtractOutputsPreprocessor` which is not needed anymore

## [0.2.4] - 2018-AUG-03
### Fixed
- PyPI deploy password for Travis CI must be encrypted with `--pro` flag

## [0.2.3] - 2018-AUG-03
### Fixed
- Fix anaconda.org upload token decryption

## [0.2.2] - 2018-AUG-03
### Fixed
- Typo in README.md
- Conda recipe description was not valid YAML

## [0.2.1] - 2018-AUG-03
### Added
- Install `conda-verify` on Travis CI

### Changed
- Change Python version dependency in `conda.recipe/meta.yaml` to be less the 4.0

### Fixed
- Fix accessing Jinja variables in `conda.recipe/meta.yaml`

### Removed

## [0.2.0] - 2018-AUG-03
### Added
- Add Travis CI configuration
- Include the `homework.tpl` template file with the distribution
- Appropriate classes are now exported in `__init__.py`

### Changed
- Use `PyMarkdownPreprocessor` from our own module to avoid having `jupyter_contrib_nbextensions` as a dependency
- Set the `build_directory` of the `PDFExporter` `FileWriter` instance to prevent writing intermediate files in the local directory
- Sort the list of problems to be processed by problem number
- Automatically write the Notebook outputs to a zip file
- Automatically combine the PDF outputs to a single PDF file
- Refactor the processing loop to avoid creating the `FilesWriter` on every iteration

### Fixed
- Fix warnings about docstrings
- Fix that paths must be resolved to be processed
- Fix typos in docstrings
- Specify that the `long_description` content for PyPI is Markdown formatted

## [0.1.0] - 2018-JUL-29
### Added
- Convert Jupyter Notebook to PDF with and without solutions
- Convert Jupyter Notebook to a set of Notebooks, with and without solutions
- README with instructions for use

[0.7.0]: https://github.com/bryanwweber/thermohw/compare/v0.6.0...v0.7.0
[0.6.0]: https://github.com/bryanwweber/thermohw/compare/v0.5.2...v0.6.0
[0.5.2]: https://github.com/bryanwweber/thermohw/compare/v0.5.1...v0.5.2
[0.5.1]: https://github.com/bryanwweber/thermohw/compare/v0.5.0...v0.5.1
[0.5.0]: https://github.com/bryanwweber/thermohw/compare/v0.4.2...v0.5.0
[0.4.2]: https://github.com/bryanwweber/thermohw/compare/v0.4.1...v0.4.2
[0.4.1]: https://github.com/bryanwweber/thermohw/compare/v0.4.0...v0.4.1
[0.4.0]: https://github.com/bryanwweber/thermohw/compare/v0.3.1...v0.4.0
[0.3.1]: https://github.com/bryanwweber/thermohw/compare/v0.3.0...v0.3.1
[0.3.0]: https://github.com/bryanwweber/thermohw/compare/v0.2.5...v0.3.0
[0.2.5]: https://github.com/bryanwweber/thermohw/compare/v0.2.4...v0.2.5
[0.2.4]: https://github.com/bryanwweber/thermohw/compare/v0.2.3...v0.2.4
[0.2.3]: https://github.com/bryanwweber/thermohw/compare/v0.2.2...v0.2.3
[0.2.2]: https://github.com/bryanwweber/thermohw/compare/v0.2.1...v0.2.2
[0.2.1]: https://github.com/bryanwweber/thermohw/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/bryanwweber/thermohw/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/bryanwweber/thermohw/compare/937175f68b1bd09597d3d91321772267ec068cae...v0.1.0
