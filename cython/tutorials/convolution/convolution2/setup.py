from distutils.core import setup
from Cython.Build import cythonize
setup(name= "import_numpy_test", ext_modules = cythonize("import_numpy_test.pyx"))