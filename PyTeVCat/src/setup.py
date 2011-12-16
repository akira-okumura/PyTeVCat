"""
Setup script for PyTeVCat
$Id$
"""

from numpy.distutils.core import setup

setup(name="PyTeVCat",
      version="1.0.0",
      description="Python wrapper for TeVCat",
      author="Akira Okumura",
      author_email="oxon@mac.com",
      packages=["tevcat"],
      package_data={"tevcat": ["img/*.png",]},
      )
