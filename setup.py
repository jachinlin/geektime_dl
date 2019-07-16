#!/usr/bin/env python
# coding: utf-8

import os
from setuptools import setup, find_packages

version = '0.2.1'


def read(fname):
    with open(os.path.join(os.path.dirname(__file__), fname)) as f:
        return f.read()


setup(
    name='geektime_dl',
    version=version,
    author='jachinlin',
    author_email='linjx1000@gmail.com',
    url='https://github.com/jachinlin/geektime_dl',
    description='把极客时间装进Kindle',
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    license='MIT',
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3 :: Only'
    ],
    keywords='kindle ebook mobi geektime',
    packages=find_packages(exclude=['examples', 'tests']),
    package_data={'geektime_dl': ['geektime_ebook/templates/*']},
    install_requires=[
        'Jinja2',
        'kindle_maker',
        'requests'
    ],
    entry_points={
        'console_scripts': [
            'geektime = geektime_dl:geektime',
        ],
    }
)
