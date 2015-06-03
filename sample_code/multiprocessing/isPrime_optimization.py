# -*- coding: utf-8 -*-
"""
Created on Mon May 11 14:11:13 2015

@author: support
"""
import time
import multiprocessing

def isPrime(x):
    print "isPrime number: " + str(x)
    for i in range(2,x):
        if x%i==0:
            return False
    return True

def standard_test(func):
    for i in range(0,5):
        print
    print "***starting standard test***"
    start = time.time()

    results = []
    for i in range(0,100000):
        results.append(func(i))
    
    end = time.time()
    
    print "***test done. total time: " + str(end - start) + "  ****"
    
    for i in range(0,5):
        print
    
    return results
    
def pool_test(func):
    for i in range(0,5):
        print
    print "***starting standard test***"
    start = time.time()


    p = multiprocessing.Pool(multiprocessing.cpu_count())
    results = p.map(func, list(i for i in range(0, 100000)))
    
    end = time.time()
    
    print "***test done. total time: " + str(end - start) + "  ****"
    
    for i in range(0,5):
        print
    
    return results