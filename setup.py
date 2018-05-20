#!/usr/bin/env python
# coding: utf-8

from setuptools import setup, find_packages

setup(
    name='geektime_ebook_maker',
    version='0.0.1',
    author='jachinlin',
    author_email='linjx1000@gmail.com',
    url='https://github.com/jachinlin/geektime_ebook_maker',
    description='把极客时间装进Kindle',
    license='MIT',
    keywords='kindle ebook mobi geektime',
    packages=find_packages(exclude=['examples', 'tests']),
    package_data={'geektime_ebook_maker': ['geektime_ebook/templates/*']},
    install_requires=[
        'Jinja2==2.10',
        'kindle_maker',
        'requests==2.18.4'
    ],
    entry_points={
        'console_scripts': [
            'geektime = geektime_ebook_maker:geektime',
        ],
    }
)
