from setuptools import setup, find_packages
import codecs
import os


VERSION = '0.0.1'
DESCRIPTION = 'Additional parser functionality for the pdf_miner library.'
LONG_DESCRIPTION = 'A package that contains methods for finding paragrahs in the original pdf and splitting them in into sentences.'

# Setting up
setup(
    name="pdf_miner_parser",
    version=VERSION,
    author="leitegarcia1",
    author_email="leitegarcia1@llnl.gov",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=['python3', 'pdfminer.six', 'numpy', 're'],
    keywords=['python', 'pdf parser', 'pdf_miner'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
