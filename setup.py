#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import io
import os
import sys
from setuptools import setup, find_packages

# Version control
python_requires = '>=3.6'
MIN_VERSION = (3, 6)
error_msg = ('This package requires Python %d.%d or higher.' % MIN_VERSION)
try:
    if sys.version_info < MIN_VERSION:
        sys.exit(error_msg)
except AttributeError:  # sys.version_info was introduced in Python 2.0
    sys.exit(error_msg)


# Defining constants, file paths, README contents etc.
HERE = os.path.abspath(os.path.dirname(__file__))
SHORT_DESCRIPTION = 'Python library for calculating pressure ' \
                    'based on ruby fluorescence'
with io.open(os.path.join(HERE, "README.md"), encoding="utf-8") as f:
    LONG_DESCRIPTION = "\n" + f.read()

setup(
    name='pruby',
    version='0.1.0',
    author='Daniel Tchoń',
    author_email='dtchon@chem.uw.edu.pl',
    packages=find_packages(exclude=('legacy', 'cli')),
    package_data={'': ['icon.gif', 'test_data1.txt', 'test_data2.txt']},
    url='https://github.com/Baharis/pRuby',
    license='MIT',
    description=SHORT_DESCRIPTION,
    long_description_content_type='text/markdown',
    long_description=LONG_DESCRIPTION,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Chemistry',
        'Topic :: Scientific/Engineering :: Physics'
    ],
    install_requires=[
        'matplotlib>=3.0.0,!=3.3.*',
        'numpy>=1.18.1',
        'scipy>=1.5.1',
        'uncertainties>=3.*',
        'natsort==8.*'
    ]
)
