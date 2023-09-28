#!/usr/bin/env python
# -*- coding: utf-8 -*-
import glob

"""The setup script."""

from setuptools import find_packages, setup

with open("README.rst") as readme_file:
    readme = readme_file.read()

with open("HISTORY.rst") as history_file:
    history = history_file.read()

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup_requirements = [
    "pytest-runner",
]

test_requirements = [
    "pytest>=3",
]

data_files = glob.glob("nastranio/writers/templates/*.tpl", recursive=True)

setup(
    author="Nicolas Cordier",
    author_email="nicolas.cordier@numeric-gmbh.ch",
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.8",
    ],
    description="Efficient Nastran Parser",
    install_requires=requirements,
    long_description=readme + "\n\n" + history,
    include_package_data=True,
    keywords="nastranio",
    name="nastranio",
    packages=find_packages(include=["nastranio", "nastranio.*"]),
    data_files=[
        (
            "nastranio/writers/templates",
            data_files,
        )
    ],
    setup_requires=setup_requirements,
    test_suite="tests",
    tests_require=test_requirements,
    version="0.16.0",
    zip_safe=False,
    entry_points={
        "console_scripts": [
            "nastranio=nastranio.cli:main",
        ],
    },
)
