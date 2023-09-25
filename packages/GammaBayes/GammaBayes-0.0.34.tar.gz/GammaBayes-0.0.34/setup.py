from setuptools import setup
import subprocess
import sys
import os

# check that python version is 3.7 or above
python_version = sys.version_info
if python_version < (3, 7):
    sys.exit("Python < 3.7 is not supported, aborting setup")
    
    


VERSION = '0.0.34'


setup(name='GammaBayes',
      description='A user-friendly Bayesian inference library',
      url='https://github.com/lpin0002/GammaBayes',
      author='Liam Pinchbeck',
      author_email='Liam.Pinchbeck@monash.edu',
      license="MIT",
      version=VERSION,
      packages=['gammabayes'],
      python_requires='>=3.7',
      install_requires=[
          "astropy>=5.1",
        "corner>=2.2.2",
        "dynesty==2.1.2",
        "jupyterlab>=3.6.3",
        "matplotlib==3.7.1",
        "scipy==1.10.1",
        "tqdm>=4.65.0",
        "numpy >=1.23",
        "gammapy==0.20.1",
        "pandas>=1.5.3",
    ],
      classifiers=[
          "License :: OSI Approved :: MIT License",
          "Operating System :: Unix"]
      )
