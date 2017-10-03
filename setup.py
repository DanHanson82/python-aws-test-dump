#!/usr/bin/env python

from setuptools import setup, find_packages


setup(
    name='aws_test_dump',
    version='0.2.0',
    description='simple script for dumping and restoring aws test data for local testing',
    url='https://github.com/DanHanson82/python-aws-test-dump',
    author='Daniel Hanson',
    author_email='daniel.hanson82@gmail.com',
    license='MIT',
    packages=find_packages(exclude=['*.tests']),
    scripts=['bin/aws_test_dump'],
    classifiers=[
        # looking to test on 3 but currently working with 2.7
        'Programming Language :: Python :: 2.7',
    ],
    install_requires=[
        "boto3",
        "six",
    ],
    zip_safe=False)
