#!/usr/bin/env python

from distutils.core import setup

from sys import version
if version < '2.2.3':
    from distutils.dist import DistributionMetadata
    DistributionMetadata.classifiers = None
    DistributionMetadata.download_url = None

setup(
    name='python-scim-setup',
    version='1.0.0',
    description='SCIM Setup Utilities',
    long_description='Modules to handle SCIM setup.',
    author='Kevin Wang',
    author_email='kevin.wang@splashtop.com',
    url='http://www.splashtop.com',
    license='GPLv2',
    packages=['scim'],
    package_data={'scim': ['examples/ssu_ex.py']},
    py_modules=['scim.ssu','scim.ssuget','scim.ssuset'],
    data_files=[('/etc/scim/setup-utils/',
                ['data/init.conf',
                 'data/firstrun.conf',
                 'data/default_imlist.conf'])],
    scripts=['scripts/stos-ssuget','scripts/stos-ssuset'],
    )

