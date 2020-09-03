from setuptools import setup, find_packages
from pathlib import Path
from typing import Dict

HERE = Path(__file__).parent

version: Dict[str, str] = {}
with HERE.joinpath("thermohw", "_version.py").open(mode="r") as version_file:
    exec(version_file.read(), version)

readme = HERE.joinpath("README.md").read_text()
changelog = HERE.joinpath("CHANGELOG.md").read_text()
long_description = readme + "\n\n" + changelog

install_requires = [
    "nbconvert>=5.3,<6.0",
    "traitlets>=4.3,<5.0",
    "pdfrw>=0.4,<0.5",
    "pandocfilters>=1.4,<2.0",
]

tests_require = [
    "pytest>=3.2.0",
]

setup(
    name="thermohw",
    version=version["__version__"],
    description="Package for converting thermo homework assignments",
    long_description_content_type="text/markdown",
    long_description=long_description,
    author="Bryan W. Weber",
    author_email="bryan.w.weber@gmail.com",
    url="https://github.com/bryanwweber/thermohw",
    packages=find_packages(),
    install_requires=install_requires,
    license="BSD-3-Clause",
    keywords=["thermodynamics homework pdf jupyter notebook"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Education",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Scientific/Engineering :: Chemistry",
    ],
    tests_require=tests_require,
    python_requires="~=3.6",
    entry_points={
        "console_scripts": [
            "convert_thermo_hw=thermohw.convert_thermo_hw:main",
            "convert_thermo_exam=thermohw.convert_thermo_exam:main",
        ]
    },
    include_package_data=True,
    zip_safe=False,
    project_urls={
        "Bug Reports": "https://github.com/bryanwweber/thermohw/issues",
        "Source": "https://github.com/bryanwweber/thermohw/",
    },
)
