#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import find_packages, setup

requirements = [
    "cdp-backend[pipeline]==3.2.3",
    "selenium==4.21.0",
    "webdriver_manager==4.0.1",
]

test_requirements = [
    "ruff==0.4.4"
]

dev_requirements = [
    *test_requirements,
    "wheel>=0.34.2",
]

extra_requirements = {
    "test": test_requirements,
    "dev": dev_requirements,
    "all": [
        *requirements,
        *dev_requirements,
    ],
}

setup(
    author="Smai Fullerton",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.10",
    ],
    description="Package containing the gather functions for Example.",
    install_requires=requirements,
    license="MIT license",
    long_description_content_type="text/markdown",
    include_package_data=True,
    keywords="civic technology, open government",
    name="cdp-missoula-backend",
    packages=find_packages(exclude=["tests", "*.tests", "*.tests.*"]),
    python_requires=">=3.10",
    tests_require=test_requirements,
    extras_require=extra_requirements,
    url="https://github.com/OpenMontana/missoula-council-data-project",
    version="1.0.0",
    zip_safe=False,
)
