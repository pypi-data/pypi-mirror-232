from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="pypackage-info",
    version="0.0.2",
    packages=find_packages(),
    author="PCCAG",
    description="A very simple tool. Can output the name, version, last modified time, and location of the installed module in the current environment in a tabular form at the terminal.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/PCCAG/pypackages-info",
    # python_requires=">=3.6, <3.11",
    entry_points={
        "console_scripts": [
            "pypackage-info = pypackage_info.info:main",
        ]
    },
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
