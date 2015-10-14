# -*- coding: utf-8 -*-
from os.path import abspath, dirname, join as path_join
from setuptools import setup

CURDIR = abspath(dirname(__file__))

# get VERSION number
execfile('src/CncLibrary/version.py')

KEYWORDS = ('cnc robotframework testing testautomation '
            'acceptancetesting atdd bdd')

SHORT_DESC = ('Robot Framework library for driving CNC mill ')

with open(path_join(CURDIR, 'README.rst'), 'r') as readme:
    LONG_DESCRIPTION = readme.read()

CLASSIFIERS = '''
Development Status :: 5 - Production/Stable
Programming Language :: Python :: 2 :: Only
Operating System :: OS Independent
Topic :: Software Development :: Testing
License :: OSI Approved :: MIT License
'''.strip().splitlines()

setup(name='CncLibrary',
      author='Eficode Oy',
      author_email='info@eficode.com',
      url='https://github.com/Eficode/robotframework-cnclibrary',
      license='MIT',
      install_requires=[
          'robotframework>=2.8',
          'pyserial>=2.7'
      ],
      packages=[
          'CncLibrary',
      ],
      package_dir={'': 'src'},
      keywords=KEYWORDS,
      classifiers=CLASSIFIERS,
      version=VERSION,
      description=SHORT_DESC,
      long_description=LONG_DESCRIPTION)