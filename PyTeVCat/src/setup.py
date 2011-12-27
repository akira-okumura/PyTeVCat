"""
Setup script for PyTeVCat
$Id$
"""

from numpy.distutils.core import setup

setup(name="PyTeVCat",
      version="1.1.1",
      description="Python wrapper for TeVCat",
      author="Akira Okumura",
      author_email="oxon@mac.com",
      url='https://sourceforge.net/p/pytevcat/',
      license='BSD License',
      platforms=['MacOS :: MacOS X', 'POSIX', 'Windows'],
      packages=["tevcat"],
      install_requires=['astropysics', 'networkx==1.4'],
      package_data={"tevcat": ["img/*.png",]},
      classifiers=['Topic :: Scientific/Engineering :: Astronomy',
                   'Topic :: Scientific/Engineering :: Physics',
                   'Development Status :: 4 - Beta',
                   'Programming Language :: Python',
                   ],
      long_description='tevcat.Python interface for TeVCat (http://tevcat.uchicago.edu/)'
      )
