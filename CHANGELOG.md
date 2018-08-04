# Change Log
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

## [Unreleased]
### Added
- `setup.cfg` file added to configure some metadata

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

[Unreleased]: https://github.com/bryanwweber/thermohw/compare/v0.2.4...HEAD
[0.2.4]: https://github.com/bryanwweber/thermohw/compare/v0.2.3...v0.2.4
[0.2.3]: https://github.com/bryanwweber/thermohw/compare/v0.2.2...v0.2.3
[0.2.2]: https://github.com/bryanwweber/thermohw/compare/v0.2.1...v0.2.2
[0.2.1]: https://github.com/bryanwweber/thermohw/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/bryanwweber/thermohw/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/bryanwweber/thermohw/compare/937175f68b1bd09597d3d91321772267ec068cae...v0.1.0
