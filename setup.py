#!/usr/local/bin/python3
from setuptools import setup

setup(
    name='re-compare',
    version='0.0',
    description='compare pattern matching algorithms',
    packages=['re_compare'],
    package_data={},  # use this to add baselines to app
    entry_points={
        'console_scripts': ['re_compare=re_compare.re_compare:main']
    },
    install_requires=['numpy', 'pandas', 'tqdm', 'ply'],
    tests_require=['pytest'])
