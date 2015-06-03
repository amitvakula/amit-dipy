from distutils.core import setup
from Cython.Build import cythonize
import os

setup(name= "helloworld", ext_modules = cythonize("helloworld.pyx"))