try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='data-schema',
    url='https://github.com/Daishy/py-data-schema',
    version="0.1",
    description="Simple scheme-library to validate and enhance python data structurs (For example configurations)",
    long_description=open("README.md").read(),
    license='LGPL',
    platforms=['any'],
    packages=['dataschema'],
    author='Andre Schemschat',
    author_email='mail@schemschat.net',
    install_requires=[]      #  'setuptools >= 0.6b1' really?,
)