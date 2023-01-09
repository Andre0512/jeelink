#!/usr/bin/env python3
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="jeelink",
    version="0.2.0",
    author="Andre Basche",
    description="Python interface for jeelink sketches",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    project_urls={
        "GitHub": "https://github.com/Andre0512/jeelink",
        "PyPI": "https://pypi.org/project/jeelink/",
    },
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Console",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    platforms="any",
    py_modules=["jeelink"],
    packages=find_packages(),
    keywords="smart home automation",
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=["pyserial", "pyserial-asyncio"],
)
