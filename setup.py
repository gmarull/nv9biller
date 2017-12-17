#!/usr/bin/env python

import re
from setuptools import setup

_version = re.search(r'__version__\s+=\s+\'(.*)\'',
                     open('nv9biller/__init__.py').read()).group(1)

setup(name='nv9biller',
      version=_version,
      packages=['nv9biller'],
      description='NV9USB Bill Validator Driver',
      long_description=open('README.rst').read(),
      author='Gerard Marull-Paretas',
      author_email='gerardmarull@gmail.com',
      url='https://www.teslabs.com',
      classifiers=[
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3'
          'Topic :: Communications',
          'Topic :: Software Development :: Libraries'
      ],
      install_requires=['pyserial>=3.4.0', 'crcmod>=1.7'])
