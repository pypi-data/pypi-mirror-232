#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [ ]

test_requirements = ['pytest>=3', ]

setup(
    author="Mohsen Alipour",
    author_email='alipour@algotik.ir',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="Get all data from TSETMC.com (Tehran Bourse).",
    install_requires=requirements,
    license="GNU General Public License v3",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='algotik_tse',
    name='algotik_tse',
    packages=find_packages(include=['algotik_tse', 'algotik_tse.*']),
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/mohsenalipour/algotik_tse',
    version='0.1.2',
    zip_safe=False,
)
