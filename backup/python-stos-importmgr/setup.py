#!/usr/bin/env python

from distutils.core import setup

from sys import version
if version < '2.2.3':
    from distutils.dist import DistributionMetadata
    DistributionMetadata.classifiers = None
    DistributionMetadata.download_url = None

setup(
    name='python-stos-importmgr',
    version='1.1.0',
    description='STOS Import Manager',
    long_description='Modules to handle the settings \
imported from Window OS.',
    author='Kevin Wang',
    author_email='kevin.wang@splashtop.com',
    url='http://www.splashtop.com',
    license='GPLv2',
    packages=['stos.importmgr'],
    package_data={'stos.importmgr': ['examples/importmgr_ex.py']},
    py_modules=['stos.importmgr.core','stos.importmgr.ucget','stos.importmgr.ucset'],
    data_files=[('/etc/stos/importmgr/',
                ['data/importmgr.ini'])],
    scripts=['scripts/stos-ucget',
             'scripts/stos-ucset'],
    )

