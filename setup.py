#!/usr/bin/env python3
from setuptools import setup

setup(name='now_playing',
      version='0.1',
      description='A web service frontend to the Squeezebox CLI',
      author='OldIronHorse',
      author_email='',
      license='GPL 3.0',
      packages=['now_playing'],
      install_requires=[
        'flask',
        'juice'
      ],
      test_suite='nose.collector',
      tests_require=['nose'],
      zip_safe=False)
