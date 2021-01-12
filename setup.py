from setuptools import setup
from pathlib import Path
from typing import Dict

HERE = Path(__file__).parent

version: Dict[str, str] = {}
with HERE.joinpath("thermohw", "_version.py").open(mode="r") as version_file:
    exec(version_file.read(), version)

setup(version=version["__version__"])
