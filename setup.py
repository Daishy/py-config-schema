try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import sys

setup(
    name='configschema',
    url='https://github.com/Daishy/py-config-schema',
    version="0.1",
    description="Simple validator-library for validating and completing a program-configuration",
    long_description=open("README.md").read(),
    license='LGPL',
    platforms=['any'],
    packages=['configschema'],
    author='Andre Schemschat',
    author_email='mail@schemschat.net',
    install_requires=[]      #  'setuptools >= 0.6b1' really?,
)