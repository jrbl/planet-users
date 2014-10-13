# -*- coding: utf-8 -*-
import os

from setuptools import setup

def read(*paths):
    """Build a file path from *paths* and return the contents."""
    with open(os.path.join(*paths), 'r') as f:
        return f.read()

short_desc = "A proof-of-concept user management service implementation."
long_desc = ''
for rstfile in ('README.rst', 'HISTORY.rst', 'AUTHORS.rst'):
    if os.path.exists(rstfile):
        long_desc += open(rstfile, 'rb').read() + "\n\n"
if not long_desc:
    long_desc = short_desc

requires_list = []
for line in open('requirements.txt', 'rb').readlines():
    line = line.strip()
    if line and line[0] != '#':
        requires_list += line

setup(
    name='usermanager',
    version='0.0.1',
    description=short_desc,
    long_description=long_desc,
    url='http://github.com/jrbl/planet-users/',
    license='GPL 3.0',
    author='Joe Blaylock',
    author_email='jrbl@jrbl.org',
    py_modules=['usermanager'],
    include_package_data=True,
    install_requires=requires_list,
    classifiers=[
        'Natural Language :: English',
        'Programming Language :: Python',
    ],
)
