from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'thermohw', '_version.py')) as version_file:
    exec(version_file.read())

with open(path.join(here, 'README.md')) as readme_file:
    readme = readme_file.read()

with open(path.join(here, 'CHANGELOG.md')) as changelog_file:
    changelog = changelog_file.read()

long_description = readme + '\n\n' + changelog

install_requires = [
    'nbconvert',
    'traitlets',
    'jupyter_contrib_nbextensions',
    'pdfrw',
]

# tests_require = [
#     'pytest>=3.2.0',
#     'pytest-cov',
# ]

setup(
    name='thermohw',
    version=__version__,  # noqa: F821
    description='Package for converting thermo homework assignments',
    long_description_content_type='text/markdown',
    long_description=long_description,
    author='Bryan W. Weber',
    author_email='bryan.w.weber@gmail.com',
    url='https://github.com/bryanwweber/thermohw',
    packages=find_packages(),
    install_requires=install_requires,
    license='BSD-3-Clause',
    keywords=['thermodynamics'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Education',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Topic :: Scientific/Engineering :: Chemistry',
    ],
    # tests_require=tests_require,
    python_requires='~=3.6',
    entry_points={
        'console_scripts': [
            'convert_thermo_hw=thermohw.convert_thermo_hw:main',
        ],
    },
    include_package_data=True,
)
