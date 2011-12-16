"""
Setup script for PyTeVCat
$Id$
"""

import tevcat

from numpy.distutils.core import setup

setup(name="PyTeVCat",
      version="1.0.0",
      description="Python wrapper for TeVCat",
      author="Akira Okumura",
      author_email="oxon@mac.com",
      url='https://sourceforge.net/p/pytevcat/',
      license='BSD License',
      platforms=['MacOS :: MacOS X', 'POSIX', 'Windows'],
      packages=["tevcat"],
      install_requires=['coords'],
      package_data={"tevcat": ["img/*.png",]},
      classifiers=['Topic :: Scientific/Engineering :: Astronomy',
                   'Topic :: Scientific/Engineering :: Physics',
                   'Development Status :: 4 - Beta',
                   'Programming Language :: Python',
                   ],
      long_description=tevcat.__doc__
      )
