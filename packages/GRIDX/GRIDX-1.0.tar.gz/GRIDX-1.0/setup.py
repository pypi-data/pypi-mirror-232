from setuptools import setup, find_packages
import codecs
import os

VERSION = '1.0'
DESCRIPTION = 'a simple tool for grids'
LONG_DESCRIPTION = 'a simple tool for girds still in working'

setup(
    name="GRIDX",
    version=VERSION,
    author="chanakya ram sai illa",
    author_email="chanakyaramsaiilla@gmail.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=[],
    keywords=['GRIDX', 'gridm'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
