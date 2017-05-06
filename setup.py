"""
Setup script for PyTeVCat
"""

from numpy.distutils.core import setup

setup(name="PyTeVCat",
      version="1.2.0",
      description="Python wrapper for TeVCat",
      author="Akira Okumura",
      author_email="oxon@mac.com",
      url='https://github.com/akira-okumura/PyTeVCat/',
      license='BSD License',
      platforms=['MacOS :: MacOS X', 'POSIX'],
      packages=["tevcat"],
      install_requires=['astropy', 'numpy'],
      package_data={"tevcat": ["img/*.png",]},
      classifiers=['Topic :: Scientific/Engineering :: Astronomy',
                   'Topic :: Scientific/Engineering :: Physics',
                   'Development Status :: 5 - Production/Stable',
                   'Programming Language :: Python',
                   ],
      long_description='tevcat.Python interface for TeVCat (http://tevcat.uchicago.edu/)'
      )
