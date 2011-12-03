#!/usr/bin/env python

from distutils.core import setup

from sys import version
if version < '2.2.3':
    from distutils.dist import DistributionMetadata
    DistributionMetadata.classifiers = None
    DistributionMetadata.download_url = None

setup(
    name='python-stos-utils',
    version='2.2.0',
    description='Python Utilities for STOS',
    long_description='A set of classes for python scripts used in STOS.',
    author='Kevin Wang',
    author_email='kevin.wang@splashtop.com',
    url='http://www.splashtop.com',
    license='GPLv2',
    packages=['stos'],
    package_data={'stos': 
        ['examples/toolutil_ex.py',
        'examples/parseini_ex.py',
        'examples/parseini_data.ini']},
    py_modules=['stos.toolutil','stos.parseini'],
    )

