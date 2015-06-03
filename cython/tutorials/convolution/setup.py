from distutils.core import setup
from Cython.Build import cythonize
import os

setup(name= "convolution", ext_modules = cythonize("convolution.pyx"))