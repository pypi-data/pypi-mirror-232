# -*- coding: utf-8 -*-
'''
Setup script of pygnss
'''

from setuptools import setup, find_packages


# python setup.py bdist_egg


setup(
    name='ppgnss',
    version='1.0.0',
    description='Python Package of GNSS data processing',
    # long_description=README,
    author='Liang Zhang',
    author_email='lzhang2019@whu.edu.cn',
    url='https://gitee.com/snnugiser/pygnss',
    # license=LICENSE,
    packages=find_packages(exclude=('tests', 'docs'))
)

