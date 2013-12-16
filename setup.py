#!/usr/bin/env python

import glob
from setuptools import setup
from finiteloop.packaging import find_packages

setup(
    name='finiteloop',
    version='0.1.6',
    description='Finite Loop Utilities',
    author='Mike Crute',
    author_email='mike@finiteloopsoftware.com',
    url='http://finiteloopsoftware.com',
    packages=find_packages('finiteloop'),
    scripts=glob.glob("scripts/*"),
    test_suite = 'finiteloop.test.suite',
)
