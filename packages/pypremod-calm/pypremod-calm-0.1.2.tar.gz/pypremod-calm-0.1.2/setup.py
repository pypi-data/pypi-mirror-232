#!/usr/bin/env python

from setuptools import setup

setup(
      name='pypremod-calm',
      description='Python package for Computational ALuminium Metallurgy',
      url='https://www.sintef.no',
      version='0.1.2',
      packages=['calm'],
      install_requires=[],
      include_package_data=True,
      package_dir={'calm': 'calm'},
      package_data={
            "calm": ["entities/*.json"],
      }
)
