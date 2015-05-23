# -*- coding: utf-8 -*-
"""
Created on Sat May 23 13:21:44 2015

@author: support
"""

"""
Only run this code to set-up pyspark when you initialize the notebook. 
"""

import os
import sys
import time


# Configure the environment
if 'SPARK_HOME' not in os.environ:
    os.environ['SPARK_HOME'] = '/Users/support/Documents/code/dependencies/spark' # NOTE: set you spark home path here
# Create a variable for our root path
SPARK_HOME = os.environ['SPARK_HOME']
# Add the PySpark/py4j to the Python Path
sys.path.insert(1, os.path.join(SPARK_HOME, "python", "build"))
sys.path.insert(1, os.path.join(SPARK_HOME, "python"))


from pyspark import  SparkContext



def isPrime_test(spark_context):
    """
    Attempts to run a Spark cluster testing the number of 
    """
    def isprime(n):
        """
        check if integer n is a prime
        """
        # make sure n is a positive integer
        n = abs(int(n))
        # 0 and 1 are not primes
        if n < 2:
            return False
        # 2 is the only even prime number
        if n == 2:
            return True
        # all other even numbers are not primes
        if not n & 1:
            return False
        # range starts with 3 and only needs to go up the square root of n
        # for all odd numbers
        for x in range(3, int(n**0.5)+1, 2):
            if n % x == 0:
                return False
        return True
    
    start = time.time()
    count = 0
    for i in range(0, 1000000):
        if isprime(i):
            count+=1
    end = time.time()
    print "naiive count: " + str(count)
    print "naiive time: " + str(end-start)
    
    
    # Create an RDD of numbers from 0 to 1,000,000
    start = time.time()
    nums = spark_context.parallelize(xrange(1000000))
    # Compute the number of primes in the RDD
    count = nums.filter(isprime).count()
    end = time.time()
    
    print "PySpark count: " + str(count)
    print "PySpark time: " + str(end-start)

def main():
    """
    Main function running the Spy Spark Toy Examples
    """    
    # set up spark context
    sc = SparkContext( 'local[3]', 'pyspark')
    
    isPrime_test(sc)
    
    # close spark context
    sc.stop()

if __name__ == "__main__":
    main()