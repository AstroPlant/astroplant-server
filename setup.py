#!/usr/bin/env python

from distutils.core import setup

setup(name='astroplant-server',
      version='1.0.0a1',
      description='AstroPlant server',
      author='AstroPlant',
      author_email='thomas@kepow.org',
      url='https://astroplant.io',
      packages=['backend', 'server', 'website',],
)
