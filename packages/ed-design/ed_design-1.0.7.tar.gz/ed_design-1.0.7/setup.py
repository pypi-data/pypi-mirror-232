import setuptools
from datetime import datetime
now = datetime.now()
dt_string = now.strftime('%Y%m%d.%H%M')

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='ed_design',
    version='1.0.7',
    author="Martin Vidkjaer",
    author_email="mav@envidan.dk",
    description="Python package developed by Envidan A/S scoping to follow the design of the company brand. This package is only for internal use.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://dev.azure.com/EnviDan-AS/ed_design",
    packages=setuptools.find_packages(),

    install_requires=[
        'matplotlib',  # <=3.5.3',  # Not sure why i have set this...
        'numpy',
        'pandas',
        'seaborn',
    ],
    python_requires='>3.0.0',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    include_package_data=True,  # Include package data specified in MANIFEST.in
    # package_data={'': ['ed_design/style']},
)
