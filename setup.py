#!/usr/bin/env python

try:
    from setuptools import setup, find_packages
    from setuptools.command.test import test
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages
    from setuptools.command.test import test

from django_common import settings

import os

here = os.path.dirname(os.path.abspath(__file__))
f = open(os.path.join(here, 'README.rst'))
long_description = f.read().strip()
f.close()

setup(
    name='django-common-helpers',
    version=settings.VERSION,
    author='Tivix',
    author_email='dev@tivix.com',
    url='http://github.com/tivix/django-common',
    description = 'Common things every Django app needs!',
    packages=find_packages(),
    long_description=long_description,
    keywords = 'django',
    zip_safe=False,
    install_requires=[
        'Django>=1.4.2',
        'South>=0.7.2'
    ],
    test_suite = 'django_common.tests',
    include_package_data=True,
    # cmdclass={},
    classifiers=[
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'Topic :: Software Development'
    ],
)
