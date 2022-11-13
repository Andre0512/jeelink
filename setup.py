#!/usr/bin/env python3
from setuptools import setup, find_packages

setup(
    name="jeelink-python",
    version="0.1",
    author="Andre Basche",
    license="MIT",
    platforms='any',
    py_modules=['jeelink-python'],
    packages=find_packages(),
    keywords='smart home automation',
    include_package_data=True,
    python_requires='>=3.8',
    install_requires=['pyserial-async'],
)
