#!/usr/bin/env python3

import os

from setuptools import setup


def read(f_name):
    return open(os.path.join(os.path.dirname(__file__), f_name)).read()


setup(
    name='azote-palettes',
    version='1.0.1',
    description='Colour palette creator and colour names dictionary',
    packages=['azote_palettes'],
    include_package_data=True,
    package_data={
        "": ["images/*"]
    },
    url='https://github.com/nwg-piotr/azote-palettes',
    license='GPL3',
    author='Piotr Miller',
    author_email='nwg.piotr@gmail.com',
    python_requires='>=3.4.0',
    install_requires=[]
)
