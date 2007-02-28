#! /usr/bin/env python
# setup.py

from glob import glob
from distutils.core import setup

setup(name='Metagui',
    version='0.01',
    # description='',
    author='Eric Pierce',
    # author_email='',
    # url='',
    packages=['metagui'],
    scripts=['bin/metagui'],
    data_files=[('share/metagui/apps', glob('apps/*.py'))]
)