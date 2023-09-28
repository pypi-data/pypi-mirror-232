from setuptools import setup, find_packages

VERSION = '0.0.1'
DESCRIPTION = 'Scan files based on file type'
LONG_DESCRIPTION = 'Will scan a folder for types of files based on an array and return a pandas dataframe with file info'

# Setting up
setup(
    # the name must match the folder name 'verysimplemodule'
    name="FileScanner",
    version=1.01,
    author="Ryan Sanders",
    author_email="rasanders22@gmail.com",
    description="Scan files based on file type",
    requires_python=">=3.9",
    long_description="Will scan a folder for types of files based on an array and return a pandas dataframe with file info",
    packages=find_packages(),
    install_requires=["pandas","pathlib"],  # add any additional packages that
    # needs to be installed along with your package. Eg: 'caer'
    keywords=['python', 'scans files'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)