import os
import glob
from setuptools import setup, find_packages

with open("README.md", "r", encoding = "utf-8") as fh:
    long_description = fh.read()

setup(
    name='pcalf',
    version='1.2.6',
    description='Search calcyanin in a set of amino acid sequences',
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url='https://github.com/K2SOHIGH/pcalf',
    author='Maxime Millet',
    author_email='maxime.luc.millet@gmail.com',
    license='MIT',
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
         "pyhmmer",
         "biopython",
         "numpy",
         "pyyaml",
         "snakemake",
         "pandas",
         "tqdm",
         "plotly",
         "python-igraph",
    ],
    python_requires = ">=3.1",
    packages = find_packages(),
    # package_dir = {"": "pcalf"},
    include_package_data=True,
    scripts = [script for script in glob.glob("scripts/*") if not os.path.basename(script).startswith("_") ],
    zip_safe=False
)
