#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import codecs
from setuptools import setup


def read(fname):
    file_path = os.path.join(os.path.dirname(__file__), fname)
    return codecs.open(file_path, encoding='utf-8').read()


setup(
    name='pytest-collect_interface_info_plugin',
    version='1.0.7',
    author='LightOffX',
    author_email='',
    maintainer='LightOffX',
    maintainer_email='',
    license='BSD-3',
    url='https://github.com/LightOffX/pytest-collect_info_plugin',
    description='Get executed interface information in pytest interface automation framework',
    long_description=read('README.rst'),
    py_modules=['pytest_collect_info_plugin'],
    python_requires='>=3.5',
    install_requires=['pytest>=7.4.2',
                      "pytest",
                      "importlib-metadata",
                      "requests",
                      ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Pytest',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Testing',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: BSD License',
    ],
    entry_points={
        'pytest11': [
            'collect_info_plugin = pytest_collect_interface_info_plugin',
        ],
    },
)
