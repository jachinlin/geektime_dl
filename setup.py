#!/usr/bin/env python
# coding: utf-8

from setuptools import setup, find_packages

version = 2.0

setup(
    name='geektime_dl',
    version=version,
    author='jachinlin',
    author_email='linjx1000@gmail.com',
    url='https://github.com/jachinlin/geektime_dl',
    description='把极客时间装进Kindle',
    license='MIT',
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
