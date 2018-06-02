#!/usr/bin/env python
from setuptools import setup

setup(name='ReCompare',
        version='0.0',
        description='compare re',
        packages=['re_compare'],
        package_data={}, # use this to add baselines to app
        entry_points={'console_scripts': ['re_compare=re_compare.re_compare:main']},
        setup_requires=['pytest-runner','ijson'],
        tests_require=['pytest'],
      )
