#!/usr/bin/env python

import glob
from distutils.core import setup
from finiteloop.packaging import find_packages


setup(
    name='FiniteLoop',
    version='0.1',
    description='Finite Loop Utilities',
    author='Mike Crute',
    author_email='mike@finiteloopsoftware.com',
    url='http://finiteloopsoftware.com',
    packages=find_packages('finiteloop'),
    scripts=glob.glob("scripts/*"),
)
