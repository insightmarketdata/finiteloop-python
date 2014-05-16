#!/usr/bin/env python

import glob
from setuptools import setup
from finiteloop.packaging import find_packages

setup(
    name='finiteloop',
    version='0.1.15',
    description='Finite Loop Utilities',
    author='Finite Loop, LLC',
    author_email='info@finiteloopsoftware.com',
    url='http://finiteloopsoftware.com',
    packages=find_packages('finiteloop'),
    scripts=glob.glob("scripts/*"),
    test_suite = 'finiteloop.test.suite',
)
