#!/usr/bin/python
from distutils.core import setup

#import glob
#os.system("cd doxygen ; doxygen ; cd ..")

setup(name="python-dvdauthor",
      version="0.1",
      author="Alexandre Bourget",
      author_email="wackysalut@bourget.cc",
      maintainer="Alexandre Bourget",
      maintainer_email="wackysalut@bourget.cc",
      description='Python module for object-oriented dvdauthor .xml file creation',
      url="http://tovid.wikia.com",
      license='GPL',
      py_modules=["dvdauthor"],
      )
#      data_files=[('docs', glob.glob('doxygen/html/*'))])
#                  ('', ['INSTALL', 'AUTHORS', 'COPYING'])])
