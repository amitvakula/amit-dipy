from distutils.core import setup
from Cython.Build import cythonize
import os

setup(name= "primes", ext_modules = cythonize("primes.pyx"))