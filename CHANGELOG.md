# Change Log
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

## [Unreleased]
### Added
- Install `conda-verify` on Travis CI

### Changed

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

[Unreleased]: https://github.com/bryanwweber/thermohw/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/bryanwweber/thermohw/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/bryanwweber/thermohw/compare/937175f68b1bd09597d3d91321772267ec068cae...v0.1.0
