#!/usr/bin/env python

from setuptools import setup

setup(name='pypremod',
      description='Python package for Premod solver',
      url='https://www.sintef.no',
      install_requires=[
          'numpy',
          'pandas',
          'pytest',
          'scipy',
          'matplotlib',
          'pypremod-calm',
          'pypremod-strength'
      ],
      version = '0.1.3',
      packages=['premod'])
