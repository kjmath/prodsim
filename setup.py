'''A setuptools based installer for prod-sim.
Based on https://github.com/pypa/sampleproject/blob/master/setup.py
Kelly Mathesius
prod-sim
2019-11-11
'''

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

INSTALL_REQUIRES = ['numpy']

TEST_REQUIRES = ['numpy']

DOCS_REQUIRES = []

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='prodsim',

    version='0.1',

    description='Factory-level production simulator.',

    author='Kelly Mathesius',
    author_email='kjmath@mit.edu',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Researcher/Manager',
        'Topic :: Production/Manufacturing',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3.7',
    ],

    # What does your project relate to?
    keywords='production manufacturing factory simulator',

    long_description=long_description,
    long_description_content_type="text/markdown",

    project_urls={
        'Documentation': 'https://github.mit.edu/kjmath/prodsim/blob/master/README.md',
        'Source Code': 'https://github.mit.edu/kjmath/prodsim',
    },

    install_requires=INSTALL_REQUIRES,
    extras_require={
        'test': TEST_REQUIRES + INSTALL_REQUIRES,
        'docs': DOCS_REQUIRES + INSTALL_REQUIRES,
    },

    packages=find_packages(),

    scripts=[],
)