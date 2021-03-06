#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os.path import dirname, join
from setuptools import setup, find_packages


with open(join(dirname(__file__), 'sshconnector/VERSION'), 'rb') as f:
    version = f.read().decode('ascii').strip()

required = [
    "paramiko>=2.0.2",
    "gevent>=1.1.2",
    "greenlet>=0.4.10",
    "cryptography>=1.5.2",
    "pyasn1>=0.1.9",
    "idna>=2.1",
    "six>=1.10.0"
]

setup(
    name='sshconnector',
    version=version,
    description='Simple API for connect server by ssh, execing command and uploading/downloading file by sftp.',
    long_description=open('README.rst').read(),
    author='kute',
    author_email='kutekute00@gmail.com',
    url='https://github.com/kute/sshconnector',
    packages=find_packages(),
    install_requires=required,
    license='MIT',
    classifiers=(
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
    ),
)
