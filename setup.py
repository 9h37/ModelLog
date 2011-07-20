#!/usr/bin/env python

import sys
from distutils.core import setup

setup(name='ModelLog',
      version='1.0',
      description='syslog on model update or deletion',
      author='Benoit Guina',
      author_email='benoit.guina@9h37.fr',
      url='http://www.9h37.fr/',
      package_dir={'': 'src'},
      packages=['modellog'],
     )
