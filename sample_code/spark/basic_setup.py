# -*- coding: utf-8 -*-
"""
Created on Thu May 28 13:59:56 2015

@author: support
"""

import os
import sys

# Configure the environment
if 'SPARK_HOME' not in os.environ:
    os.environ['SPARK_HOME'] = '/Users/support/Documents/code/dependencies/spark' # NOTE: set you spark home path here

# Create a variable for our root path
SPARK_HOME = os.environ['SPARK_HOME']

# Add the PySpark/py4j to the Python Path
sys.path.insert(1, os.path.join(SPARK_HOME, "python", "build"))
sys.path.insert(1, os.path.join(SPARK_HOME, "python"))

from pyspark import  SparkContext
# Note: you can only run this code once before getting an error if you don't run sc.stop()
sc = SparkContext( 'local', 'pyspark')
