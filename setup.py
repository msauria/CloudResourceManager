#!/usr/bin/env python

from distutils.core import setup
from setuptools import find_packages

def setup_package():
    metadata = dict(
        name = "CloudResourceManager",
        version = 1.0,
        description = 'Manage cloud resources based on workflow-specific needs in real-time',
        install_requires = ['yaml', 'cloudbridge', 'fabric'],
        package_dir = {'':'./'},
        packages = [])

    metadata['packages'] = find_packages(exclude=['examples', 'test', 'ez_setup.py'], where='./')
    setup(**metadata)

if __name__ == "__main__":
    setup_package()
